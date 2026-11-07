
from decimal import Decimal

from tests.api_helpers import (
    CONSUMPTIONS_URL,
    create_food,
    create_recipe,
    create_recipe_ingredient,
    RECIPES_URL
)
from tests.utils import register_and_login, register_and_login_other_user, auth_headers

"""
Cette suite de tests vérifie l'intégration des fonctionnalités liées aux recettes et à la nutrition.
"""

"""
Un utilisateur peut créer une recette, y ajouter des aliments et obtenir la valeur nutritionnelle totale.
"""
def test_create_recipe_with_ingredients_and_get_nutrition(
    client,
):
    access_token = register_and_login(client)
    headers = auth_headers(access_token)

    # Création des aliments nécessaires pour la recette
    chicken = create_food(
        client,
        headers,
        name="Poitrine de poulet cuite",
        reference_weight_g="100",
        calories_kcal="165",
        protein_g="31",
        carbohydrates_g="0",
        fat_g="3.6",
    )
    rice = create_food(
        client,
        headers,
        name="Riz blanc cuit",
        reference_weight_g="100",
        calories_kcal="130",
        protein_g="2.7",
        carbohydrates_g="28",
        fat_g="0.3",
    )
    # Création de la recette
    recipe = create_recipe(
        client,
        headers
    )
    # Ajout des ingrédients à la recette
    create_recipe_ingredient(
        client,
        headers,
        recipe_id=recipe["id"],
        food_id=chicken["id"],
        quantity_g="400",
    )
    create_recipe_ingredient(
        client,
        headers,
        recipe_id=recipe["id"],
        food_id=rice["id"],
        quantity_g="400",
    )
    # Récupération de la recette 
    response = client.get(
        f"{RECIPES_URL}/{recipe['id']}",
        headers=headers
    )
    assert response.status_code == 200, response.text

    # Vérification des valeurs nutritionnelles
    recipe = response.json()

    assert recipe["servings"] == 4
    assert Decimal(str(recipe["total_weight_g"])) == Decimal("800")
    assert recipe["name"] == "Bol de poulet et riz"

    assert "nutrition" in recipe
    assert Decimal(str(recipe["nutrition"]["calories_kcal"])) == Decimal("1180")
    assert Decimal(str(recipe["nutrition"]["protein_g"])) == Decimal("134.8")
    assert Decimal(str(recipe["nutrition"]["carbohydrates_g"])) == Decimal("112")
    assert Decimal(str(recipe["nutrition"]["fat_g"])) == Decimal("15.6")

    assert "ingredients" in recipe
    assert len(recipe["ingredients"]) == 2
    assert Decimal(str(recipe["ingredients"][0]["quantity_g"])) == Decimal("400")
    assert Decimal(str(recipe["ingredients"][1]["quantity_g"])) == Decimal("400")


"""
Un utilisateur ne peut pas accéder aux recettes d'un autre utilisateur.
"""
def test_recipe_is_isolated_between_users(
    client,
):
    owner_headers = auth_headers(register_and_login(client))
    other_user_headers = auth_headers(register_and_login_other_user(client))

    # Tentative d'accès à la recette par un autre utilisateur
    recipe = create_recipe(
        client,
        owner_headers,
    )
    response = client.get(
        f"{RECIPES_URL}/{recipe['id']}",
        headers=other_user_headers,
    )
    assert response.status_code == 404

    # Tentative de modification de la recette par un autre utilisateur
    update_response = client.patch(
        f"{RECIPES_URL}/{recipe['id']}",
        json={
            "name": "Recette modifiée sans autorisation",
        },
        headers=other_user_headers
    )
    assert update_response.status_code == 404

    # Tentative de suppression de la recette par un autre utilisateur
    delete_response = client.delete(
        f"{RECIPES_URL}/{recipe['id']}",
        headers=other_user_headers,
    )
    assert delete_response.status_code == 404

    # Vérification que les données n'ont pas été modifiées par l'autre utilisateur
    owner_response = client.get(
        f"{RECIPES_URL}/{recipe['id']}",
        headers=owner_headers,
    )
    assert owner_response.status_code == 200
    assert owner_response.json()["name"] == "Bol de poulet et riz"


"""
Un utilisateur peut consommer un aliment et voir son apport nutritionnel agrégé pour la journée.
"""
def test_create_consumption_and_get_daily_summary(
    client,
):
    access_token = register_and_login(client)
    headers = auth_headers(access_token)

    yogourt = create_food(client, auth_headers(access_token))
    chicken = create_food(
        client,
        headers,
        name="Poitrine de poulet cuite",
        reference_weight_g="100",
        calories_kcal="165",
        protein_g="31",
        carbohydrates_g="0",
        fat_g="3.6",
    )

    # Ajout de la consommation de yogourt au journal alimentaire
    response = client.post(
        CONSUMPTIONS_URL,
        json={
            "food_id": yogourt["id"],
            "quantity_g": "150",
            "consumed_at": "2026-11-07T18:00:00Z",
            "meal_type": "dinner"
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text

    # Ajout de la consommation de poulet au journal alimentaire
    response = client.post(
        CONSUMPTIONS_URL,
        json={
            "food_id": chicken["id"],
            "quantity_g": "200",
            "consumed_at": "2026-11-07T18:00:00Z",
            "meal_type": "dinner"
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text

    # Récupération du résumé nutritionnel pour la journée
    summary_response = client.get(
        f"{CONSUMPTIONS_URL}/summary?date=2026-11-07",
        headers=headers
    )
    assert summary_response.status_code == 200

    # Vérification des valeurs nutritionnelles agrégées pour la journée
    summary = summary_response.json()
    assert Decimal(str(summary["calories_kcal"])) == Decimal("885")
    assert Decimal(str(summary["protein_g"])) == Decimal("92")
    assert Decimal(str(summary["carbohydrates_g"])) == Decimal("75")
    assert Decimal(str(summary["fat_g"])) == Decimal("22.2")

    # Vérification que la date du résumé correspond à la date demandée
    assert summary["date"] == "2026-11-07"