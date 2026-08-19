from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.reviewer import Reviewer
from app.models.reviewer_audit_log import ReviewerAuditLog
from app.services.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# REQUEST MODELS
# ============================================================


class ReviewerCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    role: str = "reviewer"


class ReviewerStatusUpdate(BaseModel):
    is_active: bool


# ============================================================
# DATABASE DEPENDENCY
# ============================================================


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# AUTHENTICATION
# ============================================================


def get_current_reviewer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Reviewer:
    """
    Resolve the authenticated reviewer from the JWT.

    The reviewer identity comes from the signed token,
    not from user-provided request data.
    """

    try:
        payload = decode_access_token(token)

        reviewer_id = int(
            payload["sub"]
        )

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    reviewer = db.get(
        Reviewer,
        reviewer_id,
    )

    if reviewer is None:
        raise HTTPException(
            status_code=401,
            detail="Reviewer not found.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not reviewer.is_active:
        raise HTTPException(
            status_code=403,
            detail="Reviewer account is inactive.",
        )

    return reviewer


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================


def require_role(*allowed_roles: str):
    """
    Create a FastAPI dependency that allows access only
    to authenticated reviewers with one of the specified roles.
    """

    def role_checker(
        current_reviewer: Reviewer = Depends(
            get_current_reviewer
        ),
    ) -> Reviewer:
        if current_reviewer.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions.",
            )

        return current_reviewer

    return role_checker


# ============================================================
# LOGIN
# ============================================================


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    reviewer = (
        db.query(Reviewer)
        .filter(
            Reviewer.username
            == form_data.username
        )
        .first()
    )

    if reviewer is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not verify_password(
        form_data.password,
        reviewer.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not reviewer.is_active:
        raise HTTPException(
            status_code=403,
            detail="Reviewer account is inactive.",
        )

    access_token = create_access_token(
        reviewer_id=reviewer.id,
        username=reviewer.username,
        role=reviewer.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# CURRENT REVIEWER
# ============================================================


@router.get("/me")
def get_me(
    reviewer: Reviewer = Depends(
        get_current_reviewer
    ),
):
    return {
        "id": reviewer.id,
        "username": reviewer.username,
        "role": reviewer.role,
        "is_active": reviewer.is_active,
    }


# ============================================================
# CREATE REVIEWER
# ============================================================


@router.post(
    "/reviewers",
    status_code=201,
)
def create_reviewer(
    reviewer_data: ReviewerCreate,
    current_admin: Reviewer = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db),
):
    """
    Create a reviewer account.

    Only administrators may create reviewer accounts.

    The administrative action is recorded
    in reviewer_audit_logs.
    """

    allowed_roles = {
        "reviewer",
        "senior_reviewer",
        "admin",
    }

    username = (
        reviewer_data.username.strip()
    )

    if not username:
        raise HTTPException(
            status_code=422,
            detail="Username cannot be empty.",
        )

    if reviewer_data.role not in allowed_roles:
        raise HTTPException(
            status_code=422,
            detail="Invalid reviewer role.",
        )

    existing = (
        db.query(Reviewer)
        .filter(
            Reviewer.username
            == username
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "Reviewer username already exists."
            ),
        )

    reviewer = Reviewer(
        username=username,
        password_hash=hash_password(
            reviewer_data.password
        ),
        role=reviewer_data.role,
        is_active=True,
    )

    try:
        # -----------------------------------------------------
        # Create reviewer
        # -----------------------------------------------------

        db.add(reviewer)

        # Obtain the reviewer ID without committing.
        db.flush()

        # -----------------------------------------------------
        # Create audit record
        # -----------------------------------------------------

        audit_log = ReviewerAuditLog(
            actor_reviewer_id=current_admin.id,
            target_reviewer_id=reviewer.id,
            action="reviewer_created",
            details=(
                "Reviewer account created "
                f"with role={reviewer.role}."
            ),
        )

        db.add(audit_log)

        # Reviewer + audit log are committed together.
        db.commit()

        db.refresh(reviewer)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to create reviewer.",
        ) from exc

    return {
        "id": reviewer.id,
        "username": reviewer.username,
        "role": reviewer.role,
        "is_active": reviewer.is_active,
        "created_at": reviewer.created_at,
    }


# ============================================================
# LIST REVIEWERS
# ============================================================


@router.get("/reviewers")
def list_reviewers(
    current_admin: Reviewer = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db),
):
    reviewers = (
        db.query(Reviewer)
        .order_by(
            Reviewer.created_at.asc()
        )
        .all()
    )

    return [
        {
            "id": reviewer.id,
            "username": reviewer.username,
            "role": reviewer.role,
            "is_active": reviewer.is_active,
            "created_at": reviewer.created_at,
        }
        for reviewer in reviewers
    ]


# ============================================================
# UPDATE REVIEWER STATUS
# ============================================================


@router.patch(
    "/reviewers/{reviewer_id}/status"
)
def update_reviewer_status(
    reviewer_id: int,
    status_update: ReviewerStatusUpdate,
    current_admin: Reviewer = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db),
):
    """
    Activate or deactivate a reviewer account.

    Only administrators may change reviewer account status.

    Status changes are recorded in reviewer_audit_logs.
    """

    reviewer = db.get(
        Reviewer,
        reviewer_id,
    )

    if reviewer is None:
        raise HTTPException(
            status_code=404,
            detail="Reviewer not found.",
        )

    # Prevent an administrator from accidentally
    # changing their own account status.
    if reviewer.id == current_admin.id:
        raise HTTPException(
            status_code=409,
            detail=(
                "Administrator cannot change "
                "their own active status."
            ),
        )

    previous_status = (
        reviewer.is_active
    )

    reviewer.is_active = (
        status_update.is_active
    )

    try:
        # -----------------------------------------------------
        # Create audit log only if status actually changed
        # -----------------------------------------------------

        if (
            previous_status
            != reviewer.is_active
        ):
            if reviewer.is_active:
                action = (
                    "reviewer_reactivated"
                )
            else:
                action = (
                    "reviewer_deactivated"
                )

            audit_log = ReviewerAuditLog(
                actor_reviewer_id=(
                    current_admin.id
                ),
                target_reviewer_id=(
                    reviewer.id
                ),
                action=action,
                details=(
                    "Reviewer active status "
                    f"changed from "
                    f"{previous_status} "
                    f"to {reviewer.is_active}."
                ),
            )

            db.add(audit_log)

        # Reviewer change + audit log are committed together.
        db.commit()

        db.refresh(reviewer)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to update reviewer status."
            ),
        ) from exc

    return {
        "id": reviewer.id,
        "username": reviewer.username,
        "role": reviewer.role,
        "is_active": reviewer.is_active,
        "created_at": reviewer.created_at,
    }

@router.get("/audit-logs")
def list_reviewer_audit_logs(
    action: str | None = None,
    actor_reviewer_id: int | None = None,
    target_reviewer_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
    current_admin: Reviewer = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db),
):
    """
    List administrative reviewer audit events.

    Only administrators may access the administrative
    audit history.

    Optional filters:
    - action
    - actor_reviewer_id
    - target_reviewer_id

    Pagination:
    - limit: 1 to 100
    - offset: 0 or greater
    """

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 100.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=422,
            detail="offset must be 0 or greater.",
        )

    query = db.query(ReviewerAuditLog)

    if action is not None:
        query = query.filter(
            ReviewerAuditLog.action == action
        )

    if actor_reviewer_id is not None:
        query = query.filter(
            ReviewerAuditLog.actor_reviewer_id
            == actor_reviewer_id
        )

    if target_reviewer_id is not None:
        query = query.filter(
            ReviewerAuditLog.target_reviewer_id
            == target_reviewer_id
        )

    total = query.count()

    audit_logs = (
        query
        .order_by(
            ReviewerAuditLog.created_at.desc(),
            ReviewerAuditLog.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": audit_log.id,
                "actor_reviewer_id": (
                    audit_log.actor_reviewer_id
                ),
                "target_reviewer_id": (
                    audit_log.target_reviewer_id
                ),
                "action": audit_log.action,
                "details": audit_log.details,
                "created_at": audit_log.created_at,
            }
            for audit_log in audit_logs
        ],
    }