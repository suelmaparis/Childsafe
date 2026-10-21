from app.monitoring.signal_extractor import (
    extract_school_signals,
)


def test_detects_school_context():
    signals = extract_school_signals(
        "As crianças participaram numa atividade na escola."
    )

    assert signals["school_context"] is True
    assert signals["school_uniform_mentioned"] is False
    assert signals["school_schedule_mentioned"] is False


def test_detects_uniform_and_school_schedule():
    signals = extract_school_signals(
        "Alunos com uniforme escolar durante "
        "o horário escolar."
    )

    assert signals["school_context"] is True
    assert signals["school_uniform_mentioned"] is True
    assert signals["school_schedule_mentioned"] is True


def test_does_not_invent_school_signals():
    signals = extract_school_signals(
        "Fotografia de uma praia ao pôr do sol."
    )

    assert signals["school_context"] is False
    assert signals["school_uniform_mentioned"] is False
    assert signals["school_schedule_mentioned"] is False
