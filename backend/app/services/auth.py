import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


load_dotenv()


JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


password_hash = PasswordHash.recommended()


jwt_secret = os.getenv("JWT_SECRET")

if not jwt_secret:
    raise RuntimeError(
        "JWT_SECRET is not configured."
    )


def hash_password(
    password: str,
) -> str:
    """
    Hash a reviewer password for storage.
    """

    return password_hash.hash(
        password
    )


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against its stored hash.
    """

    return password_hash.verify(
        password,
        hashed_password,
    )


def create_access_token(
    reviewer_id: int,
    username: str,
    role: str,
) -> str:
    """
    Create a signed JWT access token.
    """

    now = datetime.now(
        timezone.utc
    )

    expires_at = (
        now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(reviewer_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        jwt_secret,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:
    """
    Decode and validate a JWT access token.
    """

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[
                JWT_ALGORITHM
            ],
        )

    except jwt.ExpiredSignatureError as exc:
        raise ValueError(
            "Access token has expired."
        ) from exc

    except jwt.InvalidTokenError as exc:
        raise ValueError(
            "Invalid access token."
        ) from exc

    return payload
