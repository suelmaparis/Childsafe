import logging

from app.monitoring.detector import detect_candidate
from app.monitoring.registry import get_enabled_collectors

logging.basicConfig(level=logging.INFO)


def main():
    collectors = [
        c for c in get_enabled_collectors()
        if c.channel == "meta_instagram_collector"
    ]

    if not collectors:
        print("Coletor Instagram desligado. Define META_INSTAGRAM_ENABLED=true no .env.")
        return

    candidates = collectors[0].collect()
    print(f"Candidatos recolhidos: {len(candidates)}")

    stats = {"crianca": 0, "localizacao": 0, "voluntariado": 0, "escola": 0}
    relevant = []
    near_misses = []

    for c in candidates:
        d = detect_candidate(c)
        school = (c.metadata or {}).get("school_signals") or {}

        stats["crianca"] += bool(c.contains_child)
        stats["localizacao"] += bool(c.location_detected)
        stats["voluntariado"] += bool(c.volunteer_context)
        stats["escola"] += bool(school.get("school_context"))

        if d["relevant"]:
            relevant.append((c, d))
        elif c.contains_child and c.location_detected:
            near_misses.append((c, d))

    print("Estatísticas:", stats)
    print(f"Relevantes: {len(relevant)} | Quase-casos (criança + localização): {len(near_misses)}")

    for title, group in (("RELEVANTES", relevant), ("QUASE-CASOS", near_misses)):
        print("=" * 60, title)
        for c, d in group[:15]:
            print("-" * 60)
            print("score:", d["signal_score"], "| sinais:", d["signals"])
            print(c.description[:150].replace("\n", " "))


if __name__ == "__main__":
    main()