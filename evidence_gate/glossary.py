"""Building words that mean the same thing in Dutch, English and Spanish."""

from evidence_gate.text import tokenize

CONCEPTS: dict[str, str] = {
    "pile": "pile piles paal palen heipaal heipalen palenplan pilote pilotes",
    "block": "block blocks blok blokken bloque bloques",
    "cavity": "cavity spouw spouwmuur camara",
    "insulation": "insulation insulated isolatie geisoleerd ongeisoleerd aislamiento aislado",
    "crawl_space": "crawl kruipruimte",
    "floor_plan": "plattegrond plattegronden plantas",
    "heating": "heating heater verwarming kachel gaskachel calefaccion",
    "roof": "roof dak tejado techo",
    "house": "house houses woning woningen casa casas vivienda viviendas",
    "permit": "permit vergunning bouwvergunning permiso licencia",
    "length": "long length lang lengte largo longitud",
    "height": "high height hoog hoogte alto altura",
    "handover": "handed completion opgeleverd gereedmelding entregado entrega",
}

WORD_TO_CONCEPT = {
    word: concept for concept, words in CONCEPTS.items() for word in words.split()
}

def units(text: str) -> list[frozenset[str]]:
    """Spit a question into units: each is a set of words that count as the same."""
    result: list[frozenset[str]] = []
    for word in tokenize(text):
        concept = WORD_TO_CONCEPT.get(word)
        unit = frozenset(CONCEPTS[concept].split()) if concept else frozenset([word])
        if unit not in result:
            result.append(unit)
    return result

def expand(text: str) -> str:
    """The question plus every glossary word for the concepts it mentions."""
    extra = [word for unit in units(text) if len(unit) > 1 for word in sorted(unit)]
    return " ".join([text, *extra])

