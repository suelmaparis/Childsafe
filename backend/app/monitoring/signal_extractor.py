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

    "praia",
    "mindelo",
    "sal",
    "boa vista",
    "santiago",
    "são vicente",
    "santo antão",
    "fogo",
    "brava",
    "maio",
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

    return {
        "contains_child": contains_any(
            CHILD_TERMS
        ),

        "location_detected": contains_any(
            LOCATION_TERMS
        ),

        "volunteer_context": contains_any(
            VOLUNTEER_TERMS
        ),

        "tourism_context": contains_any(
            TOURISM_TERMS
        ),
    }