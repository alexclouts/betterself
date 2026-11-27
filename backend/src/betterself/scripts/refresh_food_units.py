from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.database import SessionLocal, settings
# Tous les modèles doivent être chargés pour que SQLAlchemy résolve les relations
# (Food → User, FoodConsumption…), comme dans alembic/env.py.
from betterself.models import (  # noqa: F401
    consumption_models,
    goal_models,
    measurement_models,
    profile_models,
    recipe_models,
    target_models,
    user_models,
)
from betterself.models.food_models import Food, FoodSource
from betterself.repos.off_catalog_repo import OffCatalogRepository

"""
Recopie l'unité du catalogue Open Food Facts (unit_name, unit_name_plural,
unit_g, weight_is_estimated) sur les aliments déjà importés, après une
reconstruction du catalogue. Les entrées du journal ne changent pas : elles
sont enregistrées en grammes.

Usage (depuis backend/) :
    uv run python -m betterself.scripts.refresh_food_units
"""

UNIT_FIELDS = ("unit_name", "unit_name_plural", "unit_g", "weight_is_estimated")


@dataclass
class RefreshReport:
    updated: int = 0
    unchanged: int = 0
    # Aliments dont le code-barres n'est plus dans le catalogue : laissés tels quels.
    missing: int = 0


def refresh_food_units(db: Session, catalog: OffCatalogRepository) -> RefreshReport:
    report = RefreshReport()
    foods = db.scalars(
        select(Food).where(
            Food.source == FoodSource.OPEN_FOOD_FACTS,
            Food.external_reference_id.is_not(None),
        )
    )

    for food in foods:
        product = catalog.get(food.external_reference_id)
        if product is None:
            report.missing += 1
            continue

        changes = {
            field: getattr(product, field)
            for field in UNIT_FIELDS
            if getattr(food, field) != getattr(product, field)
        }
        if not changes:
            report.unchanged += 1
            continue

        for field, value in changes.items():
            setattr(food, field, value)
        report.updated += 1

    db.flush()
    return report


def main() -> None:
    catalog = OffCatalogRepository(settings.off_catalog_path)
    with SessionLocal() as db:
        report = refresh_food_units(db, catalog)
        db.commit()
    print(
        f"{report.updated} aliments mis à jour, {report.unchanged} inchangés, "
        f"{report.missing} absents du catalogue."
    )


if __name__ == "__main__":
    main()
