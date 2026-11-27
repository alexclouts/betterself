import pytest

from betterself.core.serving_units import ServingUnit, is_liquid, parse_serving, unit_for_product


def unit_of(text):
    return parse_serving(text).unit


# --- Unités dont le poids vient de l'étiquette ---


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2 slices (50 g)", ServingUnit("tranche", "tranches", 25, False)),
        ("1 bar (40 g)", ServingUnit("barre", "barres", 40, False)),
        ("3 crackers (15g)", ServingUnit("craquelin", "craquelins", 5, False)),
        ("2 tranches (46 g)", ServingUnit("tranche", "tranches", 23, False)),
        ("1 scoop (32 g)", ServingUnit("scoop", "scoops", 32, False)),
        ("1 mesure (30 g)", ServingUnit("scoop", "scoops", 30, False)),
        ("0.5 cup (30 g)", ServingUnit("tasse", "tasses", 60, False)),
        ("1/4 de tasse (30 g)", ServingUnit("tasse", "tasses", 120, False)),
        ("2 tbsp (30 g)", ServingUnit("c. à soupe", "c. à soupe", 15, False)),
        ("1 c. à thé (4 g)", ServingUnit("c. à thé", "c. à thé", 4, False)),
        ("1 bag (120 g)", ServingUnit("sac", "sacs", 120, False)),
        ("113 g / 1 morceau", ServingUnit("morceau", "morceaux", 113, False)),
    ],
)
def test_unit_with_label_weight(text, expected):
    assert unit_of(text) == expected


@pytest.mark.parametrize(
    ("text", "singular"),
    [
        ("1 piece (30 g)", "morceau"), ("2 pièces (30 g)", "morceau"),
        ("1 unit (52 g)", "unité"), ("1 each (40 g)", "unité"),
    ],
)
def test_pieces_and_units(text, singular):
    assert unit_of(text).singular == singular


def test_manufacturer_serving_becomes_portion():
    assert unit_of("1 serving (30 g)") == ServingUnit("portion", "portions", 30, False)
    assert unit_of("2 servings (60 g)") == ServingUnit("portion", "portions", 30, False)
    assert unit_of("1 portion (250 ml)") == ServingUnit("portion", "portions", 250, True)


def test_mojibake_is_repaired():
    assert unit_of("1 c. � soupe (15 g)").singular == "c. à soupe"


# --- Poids estimés ---


def test_volume_is_converted_and_estimated():
    assert unit_of("1 bottle (591 mL)") == ServingUnit("bouteille", "bouteilles", 591, True)
    assert unit_of("1 Tbsp (15 ml)") == ServingUnit("c. à soupe", "c. à soupe", 15, True)


def test_measure_without_weight_uses_default():
    assert unit_of("1 portion (1 cup)") == ServingUnit("tasse", "tasses", 250, True)
    assert unit_of("2 tbsp") == ServingUnit("c. à soupe", "c. à soupe", 15, True)


# --- Pas d'unité ---


@pytest.mark.parametrize(
    "text",
    [
        None, "", "30 g", "240ml",
        "1 portion",                                # portion sans poids
        "1Pouch", "18 crackers",                    # contenant ou aliment sans poids
        "3 bidules (20 g)",                         # mot inconnu
    ],
)
def test_no_unit(text):
    assert unit_of(text) is None


@pytest.mark.parametrize(
    "text",
    [
        "75 Slice (75 g)",       # poids saisi à la place du nombre
        "0.125 slice (75 g)",    # tranche de 600 g
        "1 cup (5 g)",           # tasse trop légère
        "30 1/4 cup (30 g)",     # nombre fractionnaire invraisemblable
    ],
)
def test_implausible_units_are_ignored(text):
    assert unit_of(text) is None


# --- Portion exprimée en volume ---


@pytest.mark.parametrize(
    ("text", "is_volume"),
    [
        ("250 ml", True), ("1 portion (250 mL)", True), ("1 portion (8 fl oz)", True),
        ("1 cup (250 ml)", True), ("1 cup (240 ml / 245 g)", False),
        ("30 g", False), ("2 slices (50 g)", False), (None, False),
    ],
)
def test_serving_is_volume(text, is_volume):
    assert parse_serving(text).serving_is_volume is is_volume


# --- Liquides ---


@pytest.mark.parametrize(
    "tags",
    [
        "en:dairies,en:milks-liquid-and-powder,en:milks",
        "en:beverages-and-beverages-preparations,en:beverages,en:carbonated-drinks,en:sodas",
        "en:beverages,en:teas,en:tea-based-beverages,en:iced-teas",
        "en:beverages,en:coffees,en:coffee-drinks",
        "en:meals,en:soups",
    ],
)
def test_liquids(tags):
    assert is_liquid(tags)


@pytest.mark.parametrize(
    "tags",
    [
        None, "", "en:dairies,en:cheeses",
        "en:milks,en:milk-powders",
        "en:beverages,en:instant-beverages,en:instant-coffees",
        "en:beverages,en:teas,en:tea-bags",
        "en:beverages,en:coffees,en:ground-coffees",
        "en:beverages,en:coffees",
        "en:soups,en:dehydrated-soups",
        "en:beverages-and-beverages-preparations,en:beverage-preparations",
    ],
)
def test_not_liquids(tags):
    assert not is_liquid(tags)


def test_liquid_without_unit_gets_a_cup():
    milk = "en:dairies,en:milks"
    assert unit_for_product(parse_serving("250 ml"), milk) == ServingUnit("tasse", "tasses", 250, True)
    assert unit_for_product(parse_serving(None), milk) == ServingUnit("tasse", "tasses", 250, True)
    # Une unité tirée de la portion l'emporte.
    assert unit_for_product(parse_serving("1 bottle (500 ml)"), milk).singular == "bouteille"
    # Un solide sans unité reste en grammes.
    assert unit_for_product(parse_serving(None), "en:dairies,en:cheeses") is None


# Une portion en volume se verse : elle reçoit la mesure qui lui correspond, sans catégorie.
@pytest.mark.parametrize(
    ("text", "ml", "singular"),
    [("5 ml", 5, "c. à thé"), ("15 ml", 15, "c. à soupe"), ("30 ml", 30, "c. à soupe"),
     ("250 ml", 250, "tasse"), ("355 mL", 355, "tasse")],
)
def test_volume_serving_gets_a_measure(text, ml, singular):
    unit = unit_for_product(parse_serving(text), None, ml)
    assert unit.singular == singular and unit.is_estimated
