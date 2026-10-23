from app.services.ai_risk_assessment import AIRiskAssessment


def test_geo_data_across_report_endpoints(
    client,
    auth_headers,
    monkeypatch,
):
    """Os dados geográficos acompanham a denúncia sem expor o denunciante."""

    def fake_ai_assessment(reason, description):
        return AIRiskAssessment(
            level="low",
            score=10,
            reasons=["Synthetic test."],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    # 1. Criar denúncia
    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/geo-integration-test",
            "reason": "potential_child_exposure",
            "description": "Publicação fictícia sobre Mindelo.",
            "incident_location": "Mindelo",
            "reporter_location": "Localização privada de teste",
        },
    )

    assert response.status_code == 200, response.json()

    created = response.json()
    report_id = int(created["report_id"].replace("CV-", ""))

    expected_geo = {
        "incident_location": "Mindelo",
        "geo_location_text": "mindelo",
        "geo_source": "reporter_declared",
        "geo_verification_status": "pending",
    }

    def verify_geo(data):
        for field, expected in expected_geo.items():
            assert data[field] == expected

        assert "reporter_location" not in data

    verify_geo(created["report"])

    # 2. Consultar denúncia individual
    detail_response = client.get(
        f"/reports/{report_id}",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200
    verify_geo(detail_response.json())

    # 3. Consultar lista de denúncias
    list_response = client.get(
        "/reports/",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    reports = list_response.json()

    listed_report = next(
        item
        for item in reports
        if item["report_id"] == created["report_id"]
    )

    verify_geo(listed_report)

    # 4. Consultar relatório de análise
    audit_response = client.get(
        f"/reports/{report_id}/audit",
        headers=auth_headers,
    )

    assert audit_response.status_code == 200
    verify_geo(audit_response.json()["report"])

def test_geo_report_endpoints_require_authentication(
    client,
    monkeypatch,
):
    """Os relatórios geográficos não podem ser consultados anonimamente."""

    def fake_ai_assessment(reason, description):
        return AIRiskAssessment(
            level="low",
            score=10,
            reasons=["Synthetic test."],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    created_response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/geo-auth-test",
            "reason": "potential_child_exposure",
            "description": "Publicação fictícia sobre Mindelo.",
            "incident_location": "Mindelo",
        },
    )

    assert created_response.status_code == 200

    report_id = int(
        created_response.json()["report_id"].replace("CV-", "")
    )

    protected_endpoints = [
        "/reports/",
        f"/reports/{report_id}",
        f"/reports/{report_id}/audit",
    ]

    for endpoint in protected_endpoints:
        response = client.get(endpoint)

        assert response.status_code in (401, 403), (
            endpoint,
            response.status_code,
            response.text,
        )