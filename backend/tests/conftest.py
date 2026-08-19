import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.api.reports import get_db as reports_get_db
from app.api.auth import get_db as auth_get_db
from app.main import app

# Import models so Base.metadata knows about every table.
from app.models.report import Report
from app.models.report_ai_analysis import ReportAIAnalysis
from app.models.report_review import ReportReview
from app.models.reviewer import Reviewer
from app.services.auth import hash_password



TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[
    reports_get_db
] = override_get_db

app.dependency_overrides[
    auth_get_db
] = override_get_db


@pytest.fixture(autouse=True)
def reset_test_database():
    """
    Create a fresh database before every test
    and remove all tables after the test.

    This prevents tests from affecting one another.
    """

    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def reviewer_user(db_session):
    reviewer = Reviewer(
        username="test_reviewer",
        password_hash=hash_password(
            "TestPassword123!"
        ),
        role="reviewer",
        is_active=True,
    )

    db_session.add(reviewer)
    db_session.commit()
    db_session.refresh(reviewer)

    return reviewer


@pytest.fixture
def auth_headers(
    client,
    reviewer_user,
):
    response = client.post(
        "/auth/login",
        data={
            "username": "test_reviewer",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()[
        "access_token"
    ]

    return {
        "Authorization": (
            f"Bearer {token}"
        )
    }

@pytest.fixture
def admin_user(db_session):
    admin = Reviewer(
        username="test_admin",
        password_hash=hash_password(
            "AdminPassword123!"
        ),
        role="admin",
        is_active=True,
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


@pytest.fixture
def admin_auth_headers(
    client,
    admin_user,
):
    response = client.post(
        "/auth/login",
        data={
            "username": "test_admin",
            "password": "AdminPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }