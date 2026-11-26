"""
Écritures concurrentes sur les ingrédients d'une recette.

Contrairement aux autres tests, ceux-ci utilisent de vraies transactions séparées,
validées en base : c'est la seule façon de reproduire deux requêtes simultanées.
Les données créées sont supprimées à la fin de chaque test.

Scénario : la transaction A modifie la recette sans valider; la transaction B,
dans un autre fil, tente une écriture sur la même recette. B doit attendre le
verrou de A, puis travailler à partir de l'état validé par A.
"""
import threading
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecipeWithoutIngredients
from betterself.models.food_models import Food
from betterself.models.recipe_models import Recipe, RecipeIngredient
from betterself.models.user_models import User
from betterself.repos.food_repo import FoodRepository
from betterself.repos.recipe_repo import RecipeRepository
from betterself.schemas.recipe_schemas import RecipeIngredientCreate
from betterself.services.recipe_service import RecipeService

# Temps laissé à B pour montrer qu'il est bloqué par le verrou de A.
BLOCK_CHECK_SECONDS = 0.5
# Garde-fou : un fil bloqué indéfiniment fait échouer le test au lieu de le figer.
JOIN_TIMEOUT_SECONDS = 10


def make_service(session: Session) -> RecipeService:
    return RecipeService(
        recipe_repository=RecipeRepository(session),
        food_repository=FoodRepository(session),
    )


def make_food(name: str) -> Food:
    return Food(
        name=name,
        reference_weight_g=Decimal("100"),
        calories_kcal=Decimal("100"),
        protein_g=Decimal("10"),
        carbohydrates_g=Decimal("10"),
        fat_g=Decimal("1"),
    )


@pytest.fixture
def committed_recipe(test_engine):
    """
    Recette validée en base : 100 g + 200 g = 300 g, plus deux aliments libres.
    """
    with Session(test_engine) as session:
        user = User(email=f"concurrence-{uuid.uuid4()}@example.com", pwd_hash="x")
        foods = [make_food(f"Aliment {index}") for index in range(4)]
        recipe = Recipe(
            user=user,
            name="Recette concurrente",
            servings=1,
            total_weight_g=Decimal("300"),
            ingredients=[
                RecipeIngredient(food=foods[0], quantity_g=Decimal("100")),
                RecipeIngredient(food=foods[1], quantity_g=Decimal("200")),
            ],
        )
        session.add_all([user, *foods, recipe])
        session.commit()
        data = {
            "user_id": user.id,
            "recipe_id": recipe.id,
            "ingredient_ids": [ingredient.id for ingredient in recipe.ingredients],
            "free_food_ids": [foods[2].id, foods[3].id],
            "food_ids": [food.id for food in foods],
        }

    yield data

    # Nettoyage : la recette (et ses ingrédients), puis les aliments et l'utilisateur.
    with Session(test_engine) as session:
        session.delete(session.get(Recipe, data["recipe_id"]))
        session.flush()
        for food_id in data["food_ids"]:
            session.delete(session.get(Food, food_id))
        session.delete(session.get(User, data["user_id"]))
        session.commit()


def run_in_thread(test_engine, action):
    """
    Exécute `action(service, user)` dans une transaction et un fil séparés.
    Retourne le fil et un dict qui recevra l'exception éventuelle.
    """
    outcome: dict = {}

    def target():
        with Session(test_engine) as session:
            try:
                action(make_service(session), session)
                session.commit()
            except Exception as error:  # noqa: BLE001 — rapporté au test
                session.rollback()
                outcome["error"] = error

    thread = threading.Thread(target=target)
    thread.start()
    return thread, outcome


def read_recipe(test_engine, recipe_id) -> tuple[Decimal, int]:
    with Session(test_engine) as session:
        recipe = session.get(Recipe, recipe_id)
        count = len(
            session.scalars(
                select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
            ).all()
        )
        return Decimal(recipe.total_weight_g), count


# Deux suppressions simultanées ne peuvent pas vider la recette.
def test_concurrent_deletions_keep_last_ingredient(test_engine, committed_recipe):
    recipe_id = committed_recipe["recipe_id"]
    first_id, second_id = committed_recipe["ingredient_ids"]

    with Session(test_engine) as session_a:
        user_a = session_a.get(User, committed_recipe["user_id"])
        make_service(session_a).delete_ingredient(user_a, recipe_id, first_id)

        thread, outcome = run_in_thread(
            test_engine,
            lambda service, session: service.delete_ingredient(
                session.get(User, committed_recipe["user_id"]), recipe_id, second_id
            ),
        )
        thread.join(BLOCK_CHECK_SECONDS)
        assert thread.is_alive(), "B aurait dû attendre le verrou de A."

        session_a.commit()

    thread.join(JOIN_TIMEOUT_SECONDS)
    assert not thread.is_alive()
    assert isinstance(outcome.get("error"), RecipeWithoutIngredients)

    total_weight, count = read_recipe(test_engine, recipe_id)
    assert count == 1
    assert total_weight == Decimal("200")


# Deux ajouts simultanés : le poids total compte les deux ingrédients.
def test_concurrent_additions_keep_total_weight(test_engine, committed_recipe):
    recipe_id = committed_recipe["recipe_id"]
    food_a, food_b = committed_recipe["free_food_ids"]

    with Session(test_engine) as session_a:
        user_a = session_a.get(User, committed_recipe["user_id"])
        make_service(session_a).create_ingredient(
            user_a, recipe_id, RecipeIngredientCreate(food_id=food_a, recipe_id=recipe_id, quantity_g=Decimal("50"))
        )

        thread, outcome = run_in_thread(
            test_engine,
            lambda service, session: service.create_ingredient(
                session.get(User, committed_recipe["user_id"]),
                recipe_id,
                RecipeIngredientCreate(food_id=food_b, recipe_id=recipe_id, quantity_g=Decimal("70")),
            ),
        )
        thread.join(BLOCK_CHECK_SECONDS)
        assert thread.is_alive(), "B aurait dû attendre le verrou de A."

        session_a.commit()

    thread.join(JOIN_TIMEOUT_SECONDS)
    assert not thread.is_alive()
    assert "error" not in outcome, outcome.get("error")

    total_weight, count = read_recipe(test_engine, recipe_id)
    assert count == 4
    assert total_weight == Decimal("420")
