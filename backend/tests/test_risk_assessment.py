from app.services.risk_assessment import assess_risk


def test_low_risk():
    result = assess_risk(
        "general_content",
        "A normal family photo with no safety concern.",
    )

    assert result.level == "low"
    assert result.score == 0


def test_medium_risk():
    result = assess_risk(
        "potential_child_exposure",
        "A child appears in a public post.",
    )

    assert result.level == "medium"
    assert result.score == 20


def test_critical_risk_score_is_capped_at_100():
    result = assess_risk(
        "suspected_exploitation",
        (
            "Possible sexual exploitation and immediate danger "
            "involving a vulnerable child."
        ),
    )

    assert result.level == "critical"
    assert result.score == 100
    assert result.score <= 100
def test_publicacao_educativa_nao_recebe_risco_medio_automatico():
    result = assess_risk(
        "potential_child_exposure",
        (
            "Criámos o ChildSafeCV para sensibilizar "
            "a sociedade sobre a proteção das crianças "
            "em Cabo Verde."
        ),
    )

    assert result.level == "low"
    assert result.score == 0

def test_divulgacao_de_dados_escolares_recebe_risco():
    result = assess_risk(
        "potential_child_exposure",
        (
            "Uma publicação divulga o nome completo "
            "de uma criança, a escola onde estuda "
            "e o horário de saída das aulas."
        ),
    )

    assert result.score >= 20
    assert result.level in (
        "medium",
        "high",
        "critical",
    )

def test_denuncia_de_terceiros_nao_confirma_exposicao():
    result = assess_risk(
        "potential_child_exposure",
        (
            "Denunciamos uma publicação de terceiros "
            "que divulgou o nome completo, a escola "
            "e o horário de saída de uma criança. "
            "Esta mensagem serve para sensibilizar "
            "a sociedade e pedir proteção."
        ),
    )

    assert any(
        "Potential disclosure" in reason
        for reason in result.reasons
    )
def test_publicacao_com_localizacao_habitual_recebe_risco():
    result = assess_risk(
        "potential_child_exposure",
        (
            "A public social media post shows a child "
            "and includes information that could reveal "
            "where the child regularly spends time."
        ),
    )

    assert result.score >= 20
    assert result.level in ("medium", "high", "critical")