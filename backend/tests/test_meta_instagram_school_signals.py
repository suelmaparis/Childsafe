from app.monitoring.collectors.meta_instagram import (
    MetaInstagramCollector,
)
from app.monitoring.detector import detect_candidate


def test_instagram_candidate_includes_school_metadata():
    collector = MetaInstagramCollector(client=object())

    candidate = collector._to_candidate({
        "id": "TEST-SCHOOL-001",
        "permalink": "https://example.com/school-test",
        "caption": (
            "Crianças com uniforme escolar "
            "durante o horário escolar."
        ),
    })

    school = candidate.metadata["school_signals"]

    assert school["school_context"] is True
    assert school["school_uniform_mentioned"] is True
    assert school["school_schedule_mentioned"] is True

    # Os sinais escolares não alteram a pontuação.
    assert candidate.signal_score == 1

    detection = detect_candidate(candidate)
    assert detection["relevant"] is False
