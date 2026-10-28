import pytest
from fastapi import HTTPException

from app.api.media import media_analysis_status
from app.core import settings
from app.models.reviewer import Reviewer


def test_media_status_disabled_for_admin(monkeypatch):
    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        False,
    )

    result = media_analysis_status(
        current_reviewer=Reviewer(
            role="admin",
            is_active=True,
        )
    )

    assert result == {
        "enabled": False,
        "status": "disabled",
    }


def test_media_status_enabled_for_admin(monkeypatch):
    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        True,
    )

    result = media_analysis_status(
        current_reviewer=Reviewer(
            role="admin",
            is_active=True,
        )
    )

    assert result == {
        "enabled": True,
        "status": "available",
    }
def test_media_status_requires_authentication(client):
    response = client.get("/media/status")

    assert response.status_code == 401
def test_media_status_forbidden_for_reviewer(
    client,
    auth_headers,
):
    response = client.get(
        "/media/status",
        headers=auth_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }
def test_media_status_accessible_to_admin(
    client,
    admin_auth_headers,
    monkeypatch,
):
    from app.core import settings

    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        False,
    )

    response = client.get(
        "/media/status",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "enabled": False,
        "status": "disabled",
    }
def test_media_status_accessible_to_senior_reviewer(
    client,
    db_session,
    monkeypatch,
):
    from app.core import settings
    from app.models.reviewer import Reviewer
    from app.services.auth import hash_password

    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        False,
    )

    senior_reviewer = Reviewer(
        username="test_senior_media",
        password_hash=hash_password(
            "SeniorMediaPassword123!"
        ),
        role="senior_reviewer",
        is_active=True,
    )

    db_session.add(senior_reviewer)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test_senior_media",
            "password": "SeniorMediaPassword123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/media/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "enabled": False,
        "status": "disabled",
    }