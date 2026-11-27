import re
from dataclasses import dataclass

"""
Analyse le texte libre `serving_size` d'Open Food Facts (« 2 slices (50 g) »,
« 1 cup (250 ml) », « 1 bar (40 g) ») pour en tirer une unité propre à l'aliment
et son poids. Utilisé à la construction du catalogue (scripts/build_catalog.py).

Le poids d'une unité est « estimé » quand il ne vient pas de l'étiquette :
volume converti à raison de 1 ml = 1 g, ou mesure de cuisine sans poids
(valeur par défaut de DEFAULT_UNIT_G). L'application affiche alors une mise en garde.
"""


# Catégories d'unités.
FOOD = "aliment"        # tranche, barre, biscuit…
MEASURE = "mesure"      # tasse, c. à soupe, c. à thé
CONTAINER = "contenant" # canette, bouteille, sachet… (gardé seulement avec un poids ou un volume)


@dataclass(frozen=True)
class Unit:
    singular: str
    plural: str
    category: str


@dataclass(frozen=True)
class ServingUnit:
    singular: str
    plural: str
    grams: float
    is_estimated: bool


@dataclass(frozen=True)
class ServingInfo:
    unit: ServingUnit | None
    # Vrai si la portion (serving_quantity) est un volume converti en grammes.
    serving_is_volume: bool


UNITS: dict[str, Unit] = {}


def _add(category: str, singular: str, plural: str, *variants: str) -> None:
    unit = Unit(singular, plural, category)
    for variant in variants:
        UNITS[variant] = unit


# --- Unités propres à l'aliment ---
# Portion du fabricant (« 1 serving (30 g) ») : proposée comme unité, à côté des grammes.
_add(FOOD, "portion", "portions", "portion", "portions", "serving", "servings", "part")
_add(FOOD, "unité", "unités", "unit", "units", "unité", "unités", "each", "ea")
_add(FOOD, "morceau", "morceaux", "piece", "pieces", "piece(s)", "pièce", "pièces", "pc", "pcs",
     "plece", "pleces", "peice", "peices", "assorted pieces", "pieces, approx",
     "morceau", "morceaux", "morceaux assortis")
_add(FOOD, "tranche", "tranches", "slice", "slices", "tranche", "tranches", "cm slice")
_add(FOOD, "barre", "barres", "bar", "bars", "barre", "barres")
_add(FOOD, "biscuit", "biscuits", "cookie", "cookies", "biscuit", "biscuits")
_add(FOOD, "craquelin", "craquelins", "cracker", "crackers", "craquelin", "craquelins",
     "crisps", "rice cake", "rice cakes", "galette de riz", "galettes de riz")
_add(FOOD, "croustille", "croustilles", "chip", "chips", "croustille", "croustilles")
_add(FOOD, "scoop", "scoops", "scoop", "scoops", "rounded scoop", "mesure", "mesures")
_add(FOOD, "pain", "pains", "bun", "buns", "roll", "rolls", "bread", "pain", "pains",
     "petit pain", "petits pains")
_add(FOOD, "bagel", "bagels", "bagel", "bagels")
_add(FOOD, "muffin", "muffins", "muffin", "muffins", "english muffin", "english muffins",
     "muffin anglais", "muffins anglais")
_add(FOOD, "tortilla", "tortillas", "tortilla", "tortillas", "wrap", "wraps")
_add(FOOD, "pita", "pitas", "pita", "pitas", "flatbread", "naan", "pain plat")
_add(FOOD, "saucisse", "saucisses", "sausage", "sausages", "saucisse", "saucisses",
     "wiener", "wieners", "link", "links", "hot dog")
_add(FOOD, "boulette", "boulettes", "meatball", "meatballs", "boulette", "boulettes")
_add(FOOD, "galette", "galettes", "patty", "patties", "burger", "burgers", "galette", "galettes")
_add(FOOD, "pizza", "pizzas", "pizza", "pizzas")
_add(FOOD, "gâteau", "gâteaux", "cake", "cakes", "of cake", "gâteau", "gâteaux",
     "cupcake", "cupcakes", "cheesecake")
_add(FOOD, "tarte", "tartes", "pie", "pies", "tart", "tarts", "tarte", "tartes", "quiche")
_add(FOOD, "sandwich", "sandwichs", "sandwich", "sandwiches", "sandwichs", "sanduich")
_add(FOOD, "bâtonnet", "bâtonnets", "stick", "sticks", "strip", "strips", "bâtonnet", "bâtonnets")
_add(FOOD, "carré", "carrés", "square", "squares", "carré", "carrés", "brownie", "brownies")
_add(FOOD, "cube", "cubes", "cube", "cubes", "cm cube", "cube de", "cube of")
_add(FOOD, "œuf", "œufs", "egg", "eggs", "large egg", "large eggs", "medium eggs",
     "extra large eggs", "oeuf", "oeufs", "œuf", "œufs")
_add(FOOD, "crevette", "crevettes", "shrimp", "shrimps", "crevette", "crevettes")
_add(FOOD, "filet", "filets", "fillet", "fillets", "filet", "filets", "breast", "breasts", "poitrine")
_add(FOOD, "aile", "ailes", "wing", "wings", "aile", "ailes")
_add(FOOD, "olive", "olives", "olive", "olives")
_add(FOOD, "croissant", "croissants", "croissant", "croissants")
_add(FOOD, "beigne", "beignes", "donut", "donuts", "beigne", "beignes")
_add(FOOD, "pâtisserie", "pâtisseries", "pastry", "pastries", "danish", "strudel", "scone", "scones")
_add(FOOD, "gaufre", "gaufres", "waffle", "waffles", "gaufre", "gaufres")
_add(FOOD, "gaufrette", "gaufrettes", "wafer", "wafers", "gaufrette", "gaufrettes")
_add(FOOD, "crêpe", "crêpes", "pancake", "pancakes", "crêpe", "crêpes")
_add(FOOD, "rondelle", "rondelles", "ring", "rings", "rondelle", "rondelles")
_add(FOOD, "bonbon", "bonbons", "candy", "candies", "bonbon", "bonbons", "bite", "bites",
     "gummy", "gummies", "jujube", "jujubes")
_add(FOOD, "boule", "boules", "ball", "balls", "boule", "boules")
_add(FOOD, "raviolo", "raviolis", "dumpling", "dumplings", "perogies", "pierogies", "pierogi",
     "samosa", "samosas", "biscotti")
_add(FOOD, "rouleau", "rouleaux", "spring roll", "spring rolls", "egg roll", "egg rolls")
_add(FOOD, "brochette", "brochettes", "skewer", "skewers", "brochette", "brochettes")
_add(FOOD, "feuille", "feuilles", "sheet", "sheets", "feuille", "feuilles")
_add(FOOD, "capsule", "capsules", "capsule", "capsules", "pod", "pods")
_add(FOOD, "bretzel", "bretzels", "pretzel", "pretzels", "bretzel", "bretzels")
_add(FOOD, "datte", "dattes", "date", "dates")
_add(FOOD, "cornichon", "cornichons", "pickle", "pickles")
_add(FOOD, "pépite", "pépites", "nugget", "nuggets")
_add(FOOD, "côte", "côtes", "rib", "ribs", "chop", "chops")
_add(FOOD, "steak", "steaks", "steak", "steaks")
_add(FOOD, "cornet", "cornets", "cone", "cones")
_add(FOOD, "burrito", "burritos", "burrito", "burritos")
_add(FOOD, "baguette", "baguettes", "baguette")
_add(FOOD, "pomme de terre", "pommes de terre", "potato", "potatoes")

# --- Mesures de cuisine ---
_add(MEASURE, "tasse", "tasses", "cup", "cups", "tasse", "tasses", "de tasse", "cup prepared",
     "cup drained", "cup dry", "cup condensed", "cup cooked", "cup (prepared)", "cup, drained",
     "cup, prepared")
_add(MEASURE, "c. à soupe", "c. à soupe", "tbsp", "tbsp.", "tbs", "tbps", "tablespoon",
     "tablespoons", "table spoon", "c. à soupe", "c. à table", "cuillère à soupe",
     "cuillères à soupe", "c.s.", "c. à s.")
_add(MEASURE, "c. à thé", "c. à thé", "tsp", "teaspoon", "teaspoons", "c. à thé", "c. à café",
     "cuillère à thé", "cuillères à thé", "c. à t.")

# --- Contenants ---
_add(CONTAINER, "canette", "canettes", "can", "cans", "can drained", "pop", "canette", "canettes",
     "cannette")
_add(CONTAINER, "bouteille", "bouteilles", "bottle", "bottles", "bouteille", "bouteilles")
_add(CONTAINER, "emballage", "emballages", "package", "packages", "of package", "pkg", "pack",
     "packs", "packet", "packets", "kit", "paquet", "paquets", "emballage", "emballages")
_add(CONTAINER, "sac", "sacs", "bag", "bags", "sac", "sacs")
_add(CONTAINER, "sachet", "sachets", "pouch", "pouches", "of pouch", "sachet", "sachets")
_add(CONTAINER, "contenant", "contenants", "container", "containers", "jar", "tub", "pot", "pots",
     "contenant", "contenants", "conteneur")
_add(CONTAINER, "barquette", "barquettes", "tray", "trays", "box", "boite", "boîte", "carton",
     "bowl", "bol", "plat", "meal", "barquette", "barquettes")

# Poids par défaut d'une mesure de cuisine sans poids indiqué (densité de l'eau).
DEFAULT_UNIT_G = {"tasse": 250.0, "c. à soupe": 15.0, "c. à thé": 5.0}

WEIGHT_WORDS = {"g", "gr", "gram", "grams", "gramme", "grammes", "ml"}

# Poids plausibles d'une unité (g), par unité ou, à défaut, par catégorie.
UNIT_BOUNDS_G = {
    FOOD: (1, 500), CONTAINER: (5, 2000), "portion": (1, 1000),
    "tasse": (20, 500), "c. à soupe": (3, 40), "c. à thé": (1, 15),
    "tranche": (5, 150), "biscuit": (3, 100), "croustille": (0.5, 10), "craquelin": (1, 30),
    "barre": (10, 150), "pizza": (50, 1000), "œuf": (30, 80), "muffin": (30, 200),
    "saucisse": (10, 250), "bonbon": (1, 50), "olive": (2, 15), "crevette": (3, 40),
    "canette": (100, 1000), "bouteille": (100, 2000),
}

# Nombre minimal d'unités : « 0,125 tranche (75 g) » est une erreur de saisie.
MIN_FOOD_COUNT = 0.25
MIN_OTHER_COUNT = 0.1

FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅓": 1 / 3, "⅔": 2 / 3}
NUMBER = r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?|[½¼¾⅓⅔])"
SERVING_PATTERN = re.compile(rf"^{NUMBER}?\s*([^\d()]*?)\s*(?:\((.*)\))?\s*$")
AMOUNT_PATTERN = re.compile(rf"{NUMBER}\s*(g|gr|grams?|grammes?|ml)\b")
# « 113 g / 1 morceau » : le poids avant l'unité.
WEIGHT_FIRST_PATTERN = re.compile(rf"^{NUMBER}\s*(g|ml)\s*/\s*(.+)$")
VOLUME_PATTERN = re.compile(r"\d\s*(ml|cl|l|fl\.?\s*oz)\b")


def _number(text: str) -> float | None:
    text = text.strip()
    if text in FRACTIONS:
        return FRACTIONS[text]
    if " " in text:
        # Nombre fractionnaire (« 1 1/2 ») ; « 30 1/4 » est une erreur de saisie.
        whole, fraction = text.split(None, 1)
        rest = _number(fraction)
        return float(whole) + rest if float(whole) < 10 and rest is not None else None
    if "/" in text:
        numerator, denominator = text.split("/")
        return float(numerator) / float(denominator) if float(denominator) else None
    return float(text.replace(",", "."))


# Minuscules, espaces simples, et réparation des accents mal encodés (« c. � soupe »).
def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"c\.?\s*�\s*", "c. à ", text)
    text = text.replace("pi�ce", "pièce").replace("�", "é")
    text = re.sub(r"c\.?\s*à\s*th[ée]", "c. à thé", text)
    text = re.sub(r"c\.?\s*à\s*soupe", "c. à soupe", text)
    return re.sub(r"\s+", " ", text).strip()


# Poids ou volume entre parenthèses : (valeur, est_un_volume).
def _amount(text: str) -> tuple[float, bool] | None:
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    return _number(match.group(1)), match.group(2) == "ml"


# Adjectifs de taille ignorés : « 2 tranches moyennes », « 1 medium slice », « 3 thin slices ».
SIZE_WORDS = {
    "petit", "petite", "petits", "petites", "moyen", "moyenne", "moyens", "moyennes",
    "grand", "grande", "grands", "grandes", "gros", "grosse", "grosses",
    "mince", "minces", "épais", "épaisse", "épaisses",
    "small", "medium", "large", "extra", "thin", "thick", "regular", "big", "mini",
}


# « tranches moyennes » → « tranches », sauf si l'expression est connue telle quelle
# (« petit pain », « large eggs »).
def _without_size_words(word: str) -> str:
    if word in UNITS:
        return word
    kept = [part for part in word.split() if part not in SIZE_WORDS]
    return " ".join(kept) if kept else word


def _is_plausible(unit: Unit, count: float, grams: float) -> bool:
    # « 75 slices (75 g) » : le poids a été saisi à la place du nombre.
    if count >= 10 and abs(count - grams) <= 0.2 * grams:
        return False
    if count < (MIN_FOOD_COUNT if unit.category == FOOD else MIN_OTHER_COUNT):
        return False
    low, high = UNIT_BOUNDS_G.get(unit.singular, UNIT_BOUNDS_G.get(unit.category, (1, 1000)))
    return low <= grams / count <= high


def _parse_unit(text: str) -> ServingUnit | None:
    weight_first = WEIGHT_FIRST_PATTERN.match(text)
    if weight_first:
        text = f"{weight_first.group(3)} ({weight_first.group(1)} {weight_first.group(2)})"

    match = SERVING_PATTERN.match(text)
    if not match:
        return None

    count = _number(match.group(1)) if match.group(1) else 1.0
    word = _without_size_words(match.group(2).strip(" .:-"))
    details = match.group(3) or ""

    if word in WEIGHT_WORDS:
        return None
    # « 1 portion (1 cup) » : la mesure entre parenthèses est plus précise que « portion ».
    if word in UNITS and UNITS[word].singular == "portion":
        inner = re.match(rf"^{NUMBER}\s*([^\d()]+?)$", details.strip())
        inner_word = inner.group(2).strip() if inner else None
        if inner_word in UNITS and UNITS[inner_word].category == MEASURE:
            word, count, details = inner_word, _number(inner.group(1)), ""

    unit = UNITS.get(word)
    if unit is None or not count:
        return None
    # « 3 cm cube » : le nombre est la taille du cube, pas un nombre d'unités.
    if "cm" in word:
        count = 1.0

    amount = _amount(details)
    if amount is None:
        # Sans poids, seule une mesure de cuisine a une valeur par défaut.
        if unit.category != MEASURE:
            return None
        return ServingUnit(unit.singular, unit.plural, DEFAULT_UNIT_G[unit.singular], True)

    grams, is_volume = amount
    if grams is None or not _is_plausible(unit, count, grams):
        return None
    # « 1 portion (250 ml) » : une portion en volume se mesure à la tasse ou à la cuillère.
    if unit.singular == "portion" and is_volume:
        return measure_for_volume(grams / count)
    return ServingUnit(unit.singular, unit.plural, round(grams / count, 2), is_volume)


def parse_serving(serving_size: str | None) -> ServingInfo:
    if not serving_size or not serving_size.strip():
        return ServingInfo(unit=None, serving_is_volume=False)

    text = _clean(serving_size)
    # Une portion exprimée en volume, sans poids : serving_quantity est en ml.
    is_volume = bool(VOLUME_PATTERN.search(text)) and not re.search(r"\d\s*(g|gr|grams?|grammes?)\b", text)
    return ServingInfo(unit=_parse_unit(text), serving_is_volume=is_volume)


# --- Liquides ---

# Catégories Open Food Facts des liquides.
LIQUID_TAGS = {"en:beverages", "en:milks", "en:soups"}
# Produits secs rangés parmi les boissons : poudres, café moulu, thé en sachets…
DRY_TAG_PATTERN = re.compile(
    r"powder|dried|dehydrated|instant|beverage-preparations|preparations$|tea-bags|tea-leaves"
    r"|capsule|coffee-beans|ground-coffee|soup-mix|noodle"
)
# Catégories parentes qui regroupent liquides et produits secs : elles ne tranchent pas.
MIXED_PARENT_TAGS = {"en:beverages-and-beverages-preparations", "en:milks-liquid-and-powder"}
# Café et thé : liquides seulement s'ils sont des boissons prêtes à boire.
DRY_UNLESS_DRINK = {"en:coffees": "en:coffee-drinks", "en:teas": "en:tea-based-beverages"}

# Unité proposée pour un liquide sans unité : une tasse (250 ml ≈ 250 g).
LIQUID_DEFAULT_UNIT = ServingUnit("tasse", "tasses", DEFAULT_UNIT_G["tasse"], True)


# Vrai si les catégories (« en:beverages,en:milks ») désignent un liquide prêt à boire.
def is_liquid(categories_tags: str | None) -> bool:
    tags = {tag.strip() for tag in (categories_tags or "").split(",") if tag.strip()}
    if not tags & LIQUID_TAGS:
        return False
    if any(DRY_TAG_PATTERN.search(tag) for tag in tags - MIXED_PARENT_TAGS):
        return False
    return not any(dry in tags and drink not in tags for dry, drink in DRY_UNLESS_DRINK.items())


# Mesure de cuisine adaptée à une portion en volume : 15 ml → c. à soupe, 250 ml → tasse.
def measure_for_volume(volume_ml: float) -> ServingUnit:
    for singular, plural, limit_ml in (("c. à thé", "c. à thé", 7.5), ("c. à soupe", "c. à soupe", 60)):
        if volume_ml <= limit_ml:
            return ServingUnit(singular, plural, DEFAULT_UNIT_G[singular], True)
    return LIQUID_DEFAULT_UNIT


"""
Unité d'un produit : celle de la portion; sinon, pour une portion en volume
(« 250 ml »), la mesure de cuisine qui lui correspond; sinon une tasse pour
un liquide reconnu à ses catégories. None : le produit se saisit en grammes.
"""
def unit_for_product(
    info: ServingInfo, categories_tags: str | None, serving_quantity: float | None = None
) -> ServingUnit | None:
    if info.unit is not None:
        return info.unit
    if info.serving_is_volume and serving_quantity and serving_quantity > 0:
        return measure_for_volume(serving_quantity)
    if is_liquid(categories_tags):
        return LIQUID_DEFAULT_UNIT
    return None
