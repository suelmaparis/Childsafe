from app.monitoring.signal_extractor import extract_signals


def test_sal_de_cozinha_nao_e_localizacao():
    result = extract_signals(
        "As crianças adicionaram sal à comida."
    )

    assert result["contains_child"] is True
    assert result["location_detected"] is False
    assert result["signal_score"] == 1


def test_mindelo_continua_a_ser_localizacao():
    result = extract_signals(
        "As crianças participaram numa atividade em Mindelo."
    )

    assert result["contains_child"] is True
    assert result["location_detected"] is True
    assert result["signal_score"] == 2
def test_publicacao_institucional_nao_e_exposicao():
    result = extract_signals(
        "Como nasceu o ChildSafeCV? "
        "Criámos esta plataforma para proteger "
        "as crianças de Cabo Verde e sensibilizar "
        "a sociedade sobre a exposição infantil."
    )

    assert result["contains_child"] is True
    assert result["location_detected"] is True
    assert result["signal_score"] == 2
from app.monitoring.candidate import MonitoringCandidate
from app.monitoring.detector import detect_candidate


def test_publicacao_de_sensibilizacao_nao_gera_alerta():
    description = (
        "Como nasceu o ChildSafeCV? "
        "Criámos esta plataforma para proteger "
        "as crianças de Cabo Verde e sensibilizar "
        "a sociedade sobre a exposição infantil."
    )

    signals = extract_signals(description)

    candidate = MonitoringCandidate(
        platform="instagram",
        url="https://www.instagram.com/p/exemplo/",
        description=description,
        reason="potential_child_exposure",
        source_channel="meta_instagram_collector",
        source_reference="teste_sensibilizacao",
        contains_child=signals["contains_child"],
        location_detected=signals["location_detected"],
        volunteer_context=signals["volunteer_context"],
        tourism_context=signals["tourism_context"],
        signal_score=signals["signal_score"],
        signal_confidence=signals["signal_confidence"],
    )

    result = detect_candidate(candidate)

    assert result["relevant"] is True

def test_denuncia_com_linguagem_de_sensibilizacao_continua_relevante():
    description = (
        "Criámos esta plataforma para proteger as crianças "
        "de Cabo Verde. Denunciamos uma publicação que "
        "divulga o nome completo, a escola e o horário "
        "de saída de uma criança em Mindelo."
    )

    signals = extract_signals(description)

    candidate = MonitoringCandidate(
        platform="instagram",
        url="https://www.instagram.com/p/exemplo-denuncia/",
        description=description,
        reason="potential_child_exposure",
        source_channel="meta_instagram_collector",
        source_reference="teste_denuncia",
        contains_child=signals["contains_child"],
        location_detected=signals["location_detected"],
        volunteer_context=signals["volunteer_context"],
        tourism_context=signals["tourism_context"],
        signal_score=signals["signal_score"],
        signal_confidence=signals["signal_confidence"],
    )

    result = detect_candidate(candidate)

    assert result["relevant"] is True

def test_denuncia_com_outras_palavras_nao_e_ignorada():
    description = (
        "Criámos esta plataforma para proteger as crianças "
        "de Cabo Verde. Encontrámos fotografias de uma menina "
        "com o uniforme escolar, acompanhadas da identificação "
        "da turma e do estabelecimento onde estuda."
    )

    signals = extract_signals(description)

    candidate = MonitoringCandidate(
        platform="instagram",
        url="https://www.instagram.com/p/exemplo-protecao/",
        description=description,
        reason="potential_child_exposure",
        source_channel="meta_instagram_collector",
        source_reference="teste_denuncia_alternativa",
        contains_child=signals["contains_child"],
        location_detected=signals["location_detected"],
        volunteer_context=signals["volunteer_context"],
        tourism_context=signals["tourism_context"],
        signal_score=signals["signal_score"],
        signal_confidence=signals["signal_confidence"],
    )

    result = detect_candidate(candidate)

    assert result["relevant"] is True