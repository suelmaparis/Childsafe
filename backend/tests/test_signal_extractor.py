from app.monitoring.signal_extractor import (
    extract_signals,
)


def test_extract_child_and_volunteer_signals():
    signals = extract_signals(
        "Volunteer visit with local children "
        "in Praia, Cabo Verde."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True


def test_extract_tourism_signal():
    signals = extract_signals(
        "Tourist trip to Sal during holiday."
    )

    assert signals["tourism_context"] is True
    assert signals["location_detected"] is True


def test_empty_text_returns_false_signals():
    signals = extract_signals("")

    assert signals == {
        "contains_child": False,
        "location_detected": False,
        "volunteer_context": False,
        "tourism_context": False,
        "signal_score": 0,
        "signal_confidence": 0.0,
    }
def test_portuguese_child_and_volunteer_signals():
    signals = extract_signals(
        "Voluntários com crianças "
        "em Praia, Cabo Verde."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True
    assert signals["tourism_context"] is False


def test_portuguese_tourism_signals():
    signals = extract_signals(
        "Turistas em viagem com crianças "
        "na ilha do Sal, Cabo Verde."
    )

    assert signals["contains_child"] is True
    assert signals["tourism_context"] is True
    assert signals["location_detected"] is True
    assert signals["volunteer_context"] is False


def test_portuguese_location_without_risk_context():
    signals = extract_signals(
        "Fotografia da cidade da Praia, Cabo Verde."
    )

    assert signals["location_detected"] is True
    assert signals["contains_child"] is False
    assert signals["volunteer_context"] is False
    assert signals["tourism_context"] is False


def test_portuguese_volunteer_without_child():
    signals = extract_signals(
        "Projeto de voluntariado comunitário "
        "em São Vicente."
    )

    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True
    assert signals["contains_child"] is False

def test_does_not_match_term_inside_another_word():
    signals = extract_signals(
        "This is a consolidated report."
    )

    assert signals["location_detected"] is False

def test_french_child_and_volunteer_signals():
    signals = extract_signals(
        "Des bénévoles avec des enfants "
        "à Praia, au Cap-Vert."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True
    assert signals["tourism_context"] is False


def test_french_tourism_signals():
    signals = extract_signals(
        "Des touristes en voyage avec des enfants "
        "sur l'île de Sal, au Cap-Vert."
    )

    assert signals["contains_child"] is True
    assert signals["tourism_context"] is True
    assert signals["location_detected"] is True
    assert signals["volunteer_context"] is False

def test_spanish_child_and_volunteer_signals():
    signals = extract_signals(
        "Voluntarios con niños "
        "en Praia, Cabo Verde."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True
    assert signals["tourism_context"] is False


def test_spanish_tourism_signals():
    signals = extract_signals(
        "Turistas de viaje con niños "
        "en Sal, Cabo Verde."
    )

    assert signals["contains_child"] is True
    assert signals["tourism_context"] is True
    assert signals["location_detected"] is True
    assert signals["volunteer_context"] is False
def test_accent_normalization():
    signals = extract_signals(
        "Voluntários com crianças "
        "em São Vicente."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True


def test_unaccented_text_matches_accented_terms():
    signals = extract_signals(
        "Voluntarios com criancas "
        "em Sao Vicente."
    )

    assert signals["contains_child"] is True
    assert signals["volunteer_context"] is True
    assert signals["location_detected"] is True

def test_signal_score_and_confidence():
    signals = extract_signals(
        "Volunteer activity with children "
        "in Praia, Cabo Verde."
    )

    assert signals["signal_score"] == 3
    assert signals["signal_confidence"] == 0.8


def test_signal_score_zero():
    signals = extract_signals(
        "Beautiful sunset over the ocean."
    )

    assert signals["signal_score"] == 0
    assert signals["signal_confidence"] == 0.0