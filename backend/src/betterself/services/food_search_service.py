from dataclasses import dataclass
from datetime import datetime

from betterself.core.exceptions import CatalogUnavailable
from betterself.core.text_search import barcode_candidates, name_rank, tokenize
from betterself.models.user_models import User
from betterself.repos.food_repo import FoodRepository
from betterself.repos.off_catalog_repo import CatalogProduct, OffCatalogRepository
from betterself.schemas.food_schemas import FoodSearchRead, FoodSearchResult

# Nombre d'aliments de l'historique placés en tête, pour ne pas masquer les autres.
MAX_HISTORY_ON_TOP = 5


@dataclass
class _Candidate:
    result: FoodSearchResult
    rank: int
    popularity: int
    last_used: datetime | None

    def relevance(self) -> tuple:
        return (self.rank, -self.popularity, len(self.result.name), self.result.name)


"""
Recherche unique dans les aliments de la base et dans le catalogue Open Food Facts.

Les résultats sont triés ensemble, sans égard à leur provenance. Les aliments déjà
consignés ou créés par l'utilisateur sont proposés en premier.
"""
class FoodSearchService:
    def __init__(self, foods: FoodRepository, catalog: OffCatalogRepository):
        self.foods = foods
        self.catalog = catalog

    def search(self, user: User, query: str, limit: int = 20) -> FoodSearchRead:
        words = tokenize(query)

        # Sans terme de recherche, on propose l'historique.
        if not words:
            history = self.foods.list_history(user, limit=limit)
            return FoodSearchRead(
                results=[FoodSearchResult.from_food(food, in_history=True) for food in history],
                catalog_available=True,
            )

        try:
            products = self.catalog.search(query, limit=limit)
            catalog_available = True
        except CatalogUnavailable:
            products = []
            catalog_available = False

        candidates = self._collect(user, query, words, products)

        history = [c for c in candidates if c.last_used is not None]
        history.sort(key=lambda c: (c.rank, -c.last_used.timestamp()))
        top = history[:MAX_HISTORY_ON_TOP]

        on_top = {id(c) for c in top}
        others = sorted(
            (c for c in candidates if id(c) not in on_top),
            key=_Candidate.relevance,
        )

        return FoodSearchRead(
            results=[c.result for c in (top + others)[:limit]],
            catalog_available=catalog_available,
        )

    # Réunit les aliments et les produits, sans répéter un produit déjà importé.
    def _collect(
        self,
        user: User,
        query: str,
        words: list[str],
        products: list[CatalogProduct],
    ) -> list[_Candidate]:
        matches = self.foods.search_with_history(
            user,
            words=words,
            barcodes=barcode_candidates(query),
            catalog_codes=[product.code for product in products],
        )
        popularity = {product.code: product.popularity for product in products}
        imported_codes = {food.external_reference_id for food, _ in matches if food.is_imported}

        candidates = [
            _Candidate(
                result=FoodSearchResult.from_food(food, in_history=last_used is not None),
                rank=name_rank(food.name, words),
                popularity=popularity.get(food.external_reference_id, 0) if food.is_imported else 0,
                last_used=last_used,
            )
            for food, last_used in matches
        ]
        candidates += [
            _Candidate(
                result=FoodSearchResult.from_product(product),
                rank=name_rank(product.name, words),
                popularity=product.popularity,
                last_used=None,
            )
            for product in products
            if product.code not in imported_codes
        ]
        return candidates
