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
