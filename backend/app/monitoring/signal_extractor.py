import re
import unicodedata


CHILD_TERMS = {
    # English
    "child",
    "children",
    "kid",
    "kids",
    "boy",
    "boys",
    "girl",
    "girls",
    "schoolchildren",
    "student",
    "students",

    # Portuguese
    "criança",
    "crianças",
    "menino",
    "meninos",
    "menina",
    "meninas",
    "aluno",
    "alunos",
    "aluna",
    "alunas",

    # French
    "enfant",
    "enfants",
    "garçon",
    "garçons",
    "fille",
    "filles",
    "élève",
    "élèves",

    # Spanish
    "niño",
    "niños",
    "niña",
    "niñas",
    "menor",
    "menores",
    "estudiante",
    "estudiantes",
}


VOLUNTEER_TERMS = {
    # English
    "volunteer",
    "volunteers",
    "volunteering",
    "charity",
    "mission",
    "community project",
    "donation",

    # Portuguese
    "voluntário",
    "voluntários",
    "voluntária",
    "voluntárias",
    "voluntariado",
    "caridade",
    "missão",
    "projeto comunitário",
    "doação",

    # French
    "bénévole",
    "bénévoles",
    "bénévolat",
    "charité",
    "mission humanitaire",
    "projet communautaire",
    "don",
    "dons",

    # Spanish
    "voluntario",
    "voluntarios",
    "voluntaria",
    "voluntarias",
    "voluntariado",
    "caridad",
    "misión humanitaria",
    "proyecto comunitario",
    "donación",
}


TOURISM_TERMS = {
    # English
    "tourist",
    "tourists",
    "tourism",
    "vacation",
    "holiday",
    "travel",
    "traveler",
    "travellers",
    "travelling",
    "trip",

    # Portuguese
    "turista",
    "turistas",
    "turismo",
    "férias",
    "viagem",
    "viajante",
    "viajantes",
    "viajar",

    # French
    "touriste",
    "touristes",
    "tourisme",
    "vacances",
    "voyage",
    "voyages",
    "voyageur",
    "voyageurs",

    # Spanish
    "turista",
    "turistas",
    "turismo",
    "vacaciones",
    "viaje",
    "viajes",
    "viajero",
    "viajeros",
}


LOCATION_TERMS = {
    "cabo verde",
    "cape verde",
    "cap-vert",

    "cidade da praia",
    "mindelo",
    "ilha do sal",
    "boa vista",
    "santiago",
    "são vicente",
    "santo antão",
    "ilha do fogo",
    "ilha brava",
    "ilha do maio",
    "são nicolau",
}


def normalize_text(
    text: str | None,
) -> str:
    value = (
        text or ""
    ).strip().lower()

    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )


def extract_signals(
    text: str | None,
) -> dict:
    normalized = normalize_text(
        text
    )

    def contains_any(
        terms: set[str],
    ) -> bool:
        for term in terms:
            normalized_term = normalize_text(
                term
            )

            pattern = (
                r"(?<!\w)"
                + re.escape(normalized_term)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized,
            ):
                return True

        return False
    
    contains_child = contains_any(
        CHILD_TERMS
    )

    location_detected = contains_any(
        LOCATION_TERMS
    )

    volunteer_context = contains_any(
        VOLUNTEER_TERMS
    )

    tourism_context = contains_any(
        TOURISM_TERMS
    )

    # Reconhecer a Ilha do Sal em contextos de viagem.
    if tourism_context and not location_detected:
        location_detected = bool(
            re.search(
                r"\b(?:trip|travel|flight)\s+to\s+sal\b",
                normalized,
            )
        )

    signal_score = sum(
        [
            contains_child,
            location_detected,
            volunteer_context,
            tourism_context,
        ]
    )

    confidence_map = {
        0: 0.0,
        1: 0.25,
        2: 0.55,
        3: 0.8,
        4: 0.95,
    }

    signal_confidence = confidence_map[
        signal_score
    ]

    return {
        "contains_child": contains_child,
        "location_detected": location_detected,
        "volunteer_context": volunteer_context,
        "tourism_context": tourism_context,
        "signal_score": signal_score,
        "signal_confidence": signal_confidence,
    }

def extract_school_signals(text: str | None) -> dict:
    """Identifica referências textuais a contextos escolares."""
    normalized = normalize_text(text)

    def has_terms(terms: set[str]) -> bool:
        return any(
            re.search(
                r"(?<!\w)" + re.escape(normalize_text(term)) + r"(?!\w)",
                normalized,
            )
            for term in terms
        )

    school_terms = {
        "escola",
        "escolas",
        "colégio",
        "colegio",
        "school",
        "schools",
        "école",
        "écoles",
        "escuela",
        "escuelas",
    }

    uniform_terms = {
        "uniforme escolar",
        "uniformes escolares",
        "school uniform",
        "school uniforms",
        "uniforme de escola",
    }

    schedule_terms = {
        "horário escolar",
        "horarios escolares",
        "horário das aulas",
        "school hours",
        "school schedule",
    }

    school_uniform_mentioned = has_terms(uniform_terms)
    school_schedule_mentioned = has_terms(schedule_terms)

    school_context = (
        has_terms(school_terms)
        or school_uniform_mentioned
        or school_schedule_mentioned
    )

    return {
        "school_context": school_context,
        "school_uniform_mentioned": school_uniform_mentioned,
        "school_schedule_mentioned": school_schedule_mentioned,
    }
