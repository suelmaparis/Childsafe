from datetime import datetime, timezone
from types import SimpleNamespace

from pypdf import PdfReader

from app.services.report_pdf import generate_report_pdf


def test_geo_information_in_pdf():
    """Verifica as informações geográficas no PDF."""

    report = SimpleNamespace(
        id=999999,
        created_at=datetime.now(timezone.utc),
        status="received",
        review_status="pending",
        platform="Instagram",
        reason="potential_child_exposure",
        url="https://example.com/geo-pdf-test",
        description="Denúncia fictícia sobre Mindelo.",
        incident_location=None,
        reporter_location=None,
        geo_latitude=None,
        geo_longitude=None,
        geo_location_text="mindelo",
        geo_source="publication_text",
        geo_verification_status="pending",
    )

    pdf_buffer = generate_report_pdf(report)

    reader = PdfReader(pdf_buffer)

    text = "\n".join(
        page.extract_text()
        for page in reader.pages
    )

    assert "mindelo" in text.lower()
    assert "publication_text" in text
    assert "pending" in text

    assert "AVISO:" in text
    assert "não confirma" in text

    assert "Latitude" in text
    assert "Longitude" in text