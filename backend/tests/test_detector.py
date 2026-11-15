from app.monitoring.signal_extractor import extract_signals, extract_school_signals
from app.monitoring.candidate import MonitoringCandidate
from app.monitoring.detector import detect_candidate


def make(text):
    s = extract_signals(text)
    return MonitoringCandidate(
        platform="Instagram", url="x", description=text, source_reference="1",
        contains_child=s["contains_child"],
        location_detected=s["location_detected"],
        volunteer_context=s["volunteer_context"],
        tourism_context=s["tourism_context"],
        metadata={"school_signals": extract_school_signals(text)},
    )


def test_ganvie_ignored():
    text = ("Ganvié is a lake village in Benin. For many children, the school "
            "journey is by boat. People earn money through trading and tourism.")
    assert detect_candidate(make(text))["relevant"] is False


def test_cabo_verde_volunteer_school_passes():
    text = "Volunteering at a school in Mindelo, Cabo Verde. The kids loved it."
    assert detect_candidate(make(text))["relevant"] is True

def test_other_african_country_volunteer_passes():
    text = "Volunteering at a school in Nairobi, Kenya. The kids loved it."
    assert detect_candidate(make(text))["relevant"] is True


def test_outside_africa_ignored():
    text = "Volunteering at a school in Lima, Peru. The kids loved it."
    assert detect_candidate(make(text))["relevant"] is False

def test_orphanage_volunteering_in_africa_passes():
    text = "Volunteering at an orphanage in Accra, Ghana."
    assert detect_candidate(make(text))["relevant"] is True