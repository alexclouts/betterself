import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from betterself.core.exceptions import CatalogUnavailable
from betterself.core.text_search import barcode_candidates, name_rank, tokenize

logger = logging.getLogger(__name__)

# Les valeurs nutritionnelles d'Open Food Facts sont exprimées pour 100 g.
REFERENCE_WEIGHT_G = Decimal("100.00")

# Longueur maximale des colonnes `name` et `brand` de la table `foods`.
MAX_TEXT_LENGTH = 255

# Portions jugées plausibles : les données participatives contiennent des erreurs.
MIN_SERVING_G = 1
MAX_SERVING_G = 1000

PRODUCT_COLUMNS = (
    "p.code, p.name, p.brands, p.serving_g, "
    "p.kcal_100g, p.protein_100g, p.carbs_100g, p.fat_100g, p.scans"
)


"""
Produit du catalogue Open Food Facts, déjà converti aux unités de BetterSelf.
"""
@dataclass(frozen=True)
class CatalogProduct:
    code: str
    name: str
    brand: str | None
    serving_g: Decimal | None
    reference_weight_g: Decimal
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal
    popularity: int


def _to_decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


# Retourne la portion, ou None si elle est absente ou invraisemblable.
def _to_serving(value: float | None) -> Decimal | None:
    if value is None or not MIN_SERVING_G <= value <= MAX_SERVING_G:
        return None
    return _to_decimal(value)


def _to_product(row: tuple) -> CatalogProduct:
    code, name, brands, serving_g, kcal, protein, carbs, fat, scans = row
    brand = (brands or "").strip()[:MAX_TEXT_LENGTH]

    return CatalogProduct(
        code=code,
        name=name.strip()[:MAX_TEXT_LENGTH],
        brand=brand or None,
        serving_g=_to_serving(serving_g),
        reference_weight_g=REFERENCE_WEIGHT_G,
        calories_kcal=_to_decimal(kcal),
        protein_g=_to_decimal(protein),
        carbohydrates_g=_to_decimal(carbs),
        fat_g=_to_decimal(fat),
        popularity=scans or 0,
    )


"""
Consulte, en lecture seule, le catalogue local construit à partir de l'export
Open Food Facts. Lève `CatalogUnavailable` si le catalogue est absent ou illisible.

Le fichier est ouvert à chaque requête, ce qui permet de le remplacer par une
version plus récente sans redémarrer l'application.
"""
class OffCatalogRepository:
    def __init__(self, path: str | None):
        self.path = path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # as_uri() encode les espaces du chemin ; mode=ro ne crée jamais de fichier.
        uri = f"{Path(self.path).resolve().as_uri()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        try:
            yield connection
        finally:
            connection.close()

    def _fetch(self, statement: str, parameters: tuple, words: list[str]) -> list[CatalogProduct]:
        if not self.path:
            raise CatalogUnavailable("OFF_CATALOG_PATH n'est pas configuré.")

        try:
            with self._connect() as connection:
                connection.create_function(
                    "name_rank", 1, lambda name: name_rank(name, words), deterministic=True
                )
                rows = connection.execute(statement, parameters).fetchall()
        except sqlite3.Error as error:
            logger.warning("Catalogue Open Food Facts inaccessible.", exc_info=True)
            raise CatalogUnavailable("Le catalogue est illisible.") from error

        return [_to_product(row) for row in rows]

    # Retourne un produit selon son code-barres exact.
    def get(self, code: str) -> CatalogProduct | None:
        products = self._fetch(
            f"SELECT {PRODUCT_COLUMNS} FROM products p WHERE p.code = ?", (code,), []
        )
        return products[0] if products else None

    """
    Recherche des produits par code-barres, ou par nom et marque.
    Les résultats sont triés par pertinence du nom, puis par popularité.
    """
    def search(self, query: str, limit: int = 20) -> list[CatalogProduct]:
        words = tokenize(query)
        if not words:
            return []

        for code in barcode_candidates(query):
            product = self.get(code)
            if product:
                return [product]

        # Chaque mot est mis entre guillemets pour que la syntaxe FTS5
        # (OR, NEAR, *, :) saisie par l'utilisateur ne soit jamais interprétée.
        match = " ".join(f'"{word}"*' for word in words)

        return self._fetch(
            f"""
            SELECT {PRODUCT_COLUMNS}
            FROM products_fts f
            JOIN products p ON p.rowid = f.rowid
            WHERE products_fts MATCH ?
            ORDER BY name_rank(p.name), p.scans DESC, length(p.name), p.code
            LIMIT ?
            """,
            (match, limit),
            words,
        )
