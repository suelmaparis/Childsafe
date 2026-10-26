from app.models.report import Report


def test_public_report_duplicate_returns_existing_case(
    client,
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        lambda reason, description: None,
    )

    payload = {
        "platform": "Instagram",
        "url": "https://www.instagram.com/p/TEST123/",
        "reason": "potential_child_exposure",
        "description": (
            "Synthetic test without real child data."
        ),
    }

    first = client.post(
        "/reports/public",
        json=payload,
    )

    second = client.post(
        "/reports/public",
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert (
        first.json()["report_id"]
        == second.json()["report_id"]
    )

    reports = db_session.query(Report).filter(
        Report.source_type == "public_report",
        Report.source_channel == "public_web_form",
    ).all()

    assert len(reports) == 1
def test_public_report_duplicate_with_share_parameters(
    client,
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        lambda reason, description: None,
    )

    payload = {
        "platform": "Instagram",
        "url": "https://www.instagram.com/p/TEST456/?igsh=abc",
        "reason": "potential_child_exposure",
        "description": "Synthetic test without real child data.",
    }

    first = client.post(
        "/reports/public",
        json=payload,
    )

    payload["url"] = "https://instagram.com/p/TEST456/"

    second = client.post(
        "/reports/public",
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["report_id"] == second.json()["report_id"]

    reports = db_session.query(Report).filter(
        Report.source_type == "public_report",
        Report.source_channel == "public_web_form",
    ).all()

    assert len(reports) == 1

def test_public_report_reuses_legacy_case(
    client,
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        lambda reason, description: None,
    )

    # Simulate a public report created before deduplication.
    old_report = Report(
        platform="Instagram",
        url="https://www.instagram.com/p/OLD123/?igsh=abc",
        reason="potential_child_exposure",
        description="Synthetic historical test.",
        source_type="public_report",
        source_channel="public_web_form",
        source_reference=None,
    )

    db_session.add(old_report)
    db_session.commit()
    db_session.refresh(old_report)

    response = client.post(
        "/reports/public",
        json={
            "platform": "Instagram",
            "url": "https://instagram.com/p/OLD123/",
            "reason": "potential_child_exposure",
            "description": "Synthetic new submission.",
        },
    )

    assert response.status_code == 200
    assert response.json()["report_id"] == (
        f"CV-{old_report.id:06d}"
    )

    reports = db_session.query(Report).filter(
        Report.source_type == "public_report",
        Report.source_channel == "public_web_form",
    ).all()

    assert len(reports) == 1
    assert reports[0].source_reference is None
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


def test_public_report_does_not_hide_unrelated_integrity_error(
    client,
    monkeypatch,
):
    def fake_create_report_record(report, db):
        original_error = IntegrityError(
            statement="INSERT INTO reports",
            params={},
            orig=Exception("Unrelated database constraint"),
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to save report.",
        ) from original_error

    monkeypatch.setattr(
        "app.api.reports.create_report_record",
        fake_create_report_record,
    )

    response = client.post(
        "/reports/public",
        json={
            "platform": "Instagram",
            "url": "https://instagram.com/p/ERROR123/",
            "reason": "potential_child_exposure",
            "description": "Synthetic integrity error test.",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Unable to save report."

import sqlite3

from sqlalchemy.exc import IntegrityError


def test_public_report_recovers_from_unique_index_collision(
    client,
    db_session,
    monkeypatch,
):
    from app.services.public_report_deduplication import (
        public_report_reference,
    )

    url = "https://instagram.com/p/RACE123/"
    reference = public_report_reference("Instagram", url)

    def fake_create_report_record(report, db):
        # Simulate another submission creating the case first.
        existing = Report(
            platform="Instagram",
            url=url,
            reason="potential_child_exposure",
            description="Synthetic concurrent submission.",
            source_type="public_report",
            source_channel="public_web_form",
            source_reference=reference,
        )

        db.add(existing)
        db.commit()

        original_error = sqlite3.IntegrityError(
            "UNIQUE constraint failed: reports.source_reference"
        )

        original_error.sqlite_errorname = (
            "SQLITE_CONSTRAINT_UNIQUE"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to save report.",
        ) from IntegrityError(
            statement="INSERT INTO reports",
            params={},
            orig=original_error,
        )

    monkeypatch.setattr(
        "app.api.reports.create_report_record",
        fake_create_report_record,
    )

    response = client.post(
        "/reports/public",
        json={
            "platform": "Instagram",
            "url": url,
            "reason": "potential_child_exposure",
            "description": "Synthetic test without real child data.",
        },
    )

    assert response.status_code == 200

    reports = db_session.query(Report).filter(
        Report.source_type == "public_report",
        Report.source_channel == "public_web_form",
    ).all()

    assert len(reports) == 1
    assert response.json()["report_id"] == (
        f"CV-{reports[0].id:06d}"
    )