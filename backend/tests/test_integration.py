
from decimal import Decimal

from tests.api_helpers import (
    CONSUMPTIONS_URL,
    NUTRITION_GOAL_URL, 
    RECIPES_URL, 
    MEASUREMENTS_URL,
    TARGET_URL,
    USERS_URL,
    create_food,
    create_recipe,
    create_recipe_ingredient,
    create_nutrition_goal,
    recalculate_target,
    get_active_target,
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


"""
Un utilisateur peut créer une mesure de poids, ce qui a pour effet de recalculer 
la cible nutritionnelle en fonction du nouveau poids.
"""
def test_recalculate_goal_target_after_weight_decrease(client):
    access_token = register_and_login(client)
    headers = auth_headers(access_token)

    create_nutrition_goal(client, headers)

    # Première cible, calculée à partir d'un poids de 85 kg.
    initial_target = recalculate_target(
        client,
        headers,
        reference_weight_kg=85,
    )
    initial_target_id = initial_target["id"]
    initial_calories = Decimal(
        str(initial_target["calories_target_kcal"])
    )

    # Nouvelle mesure de poids : l'utilisateur passe de 85 kg à 80 kg.
    measurement_response = client.post(
        MEASUREMENTS_URL,
        json={
            "date": "2026-11-07",
            "weight_kg": 80,
        },
        headers=headers,
    )
    assert measurement_response.status_code == 201, measurement_response.text

    measurement = measurement_response.json()
    assert Decimal(str(measurement["weight_kg"])) == Decimal("80")

    # Recalcul explicite de la cible après la nouvelle mesure.
    updated_target = recalculate_target(
        client, headers, reference_weight_kg=measurement["weight_kg"],
    )
    updated_calories = Decimal(
        str(updated_target["calories_target_kcal"])
    )

    # Le poids a diminué, donc la cible calorique doit diminuer.
    assert updated_calories < initial_calories

    # La nouvelle cible doit être différente de l'ancienne.
    assert updated_target["id"] != initial_target_id

    # La cible active doit désormais être la nouvelle cible.
    active_target = get_active_target(client, headers)
    assert active_target["id"] == updated_target["id"]
    assert active_target["id"] != initial_target_id

    assert Decimal(str(active_target["reference_weight_kg"])) == Decimal("80")
    assert active_target["valid_until"] is None


"""
Un utilisateur peut créer une recette et consommer une partie de celle-ci, ce qui doit être correctement reflété dans le résumé journalier.
"""
def test_create_recipe_and_consume_half_recipe(client):
    access_token = register_and_login(client)
    headers = auth_headers(access_token)

    chicken = create_food(
        client,
        headers,
        name="Poitrine de poulet cuite",
        calories_kcal="165",
        protein_g="31",
        carbohydrates_g="0",
        fat_g="3.6",
    )
    rice = create_food(
        client,
        headers,
        name="Riz blanc cuit",
        calories_kcal="130",
        protein_g="2.7",
        carbohydrates_g="28",
        fat_g="0.3",
    )
    recipe = create_recipe(client, headers)

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

    # L'utilisateur consomme 400 g sur 800 g, soit la moitié de la recette.
    consumption_response = client.post(
        CONSUMPTIONS_URL,
        json={
            "recipe_id": recipe["id"],
            "quantity_g": "400",
            "consumed_at": "2026-11-08T18:00:00Z",
            "meal_type": "dinner",
        },
        headers=headers,
    )
    assert consumption_response.status_code == 201, consumption_response.text

    # Vérification de la consommation créée.
    consumption = consumption_response.json()
    assert consumption["recipe_id"] == recipe["id"]
    assert Decimal(str(consumption["quantity_g"])) == Decimal("400")
    assert Decimal(str(consumption["calories_kcal"])) == Decimal("590")
    assert Decimal(str(consumption["protein_g"])) == Decimal("67.4")
    assert Decimal(str(consumption["carbohydrates_g"])) == Decimal("56")
    assert Decimal(str(consumption["fat_g"])) == Decimal("7.8")

    # Vérification du résumé journalier.
    summary_response = client.get(
        f"{CONSUMPTIONS_URL}/summary",
        params={"date": "2026-11-08"},
        headers=headers,
    )
    assert summary_response.status_code == 200, summary_response.text

    summary = summary_response.json()
    assert Decimal(str(summary["calories_kcal"])) == Decimal("590")
    assert Decimal(str(summary["protein_g"])) == Decimal("67.4")
    assert Decimal(str(summary["carbohydrates_g"])) == Decimal("56")
    assert Decimal(str(summary["fat_g"])) == Decimal("7.8")


"""
Un utilisateur nouvellement inscrit doit compléter plusieurs étapes d'onboarding avant que son statut ne soit considéré comme complet. 
Ce test vérifie que le statut d'onboarding passe de "incomplet" à "complet" après que toutes les étapes requises ont été effectuées.
"""
def test_onboarding_status_incomplete_then_complete(client):
    access_token = register_and_login(client)
    headers = auth_headers(access_token)

    # Après l'inscription, l'onboarding n'est pas terminé.
    initial_response = client.get(
        f"{USERS_URL}/me/onboarding-status",
        headers=headers,
    )
    assert initial_response.status_code == 200, initial_response.text

    initial_status = initial_response.json()
    assert initial_status["is_complete"] is False
    assert "profile" in initial_status["missing_steps"]
    assert "body_measurement" in initial_status["missing_steps"]
    assert "nutrition_goal" in initial_status["missing_steps"]
    assert "goal_target" in initial_status["missing_steps"]

    # Création du profil.
    profile_response = client.put(
        f"{USERS_URL}/me/profile",
        json={
            "first_name": "Alex",
            "year_of_birth": 1990,
            "sex": "M",
            "height_cm": "180",
            "activity_level": "moderate",
        },
        headers=headers,
    )
    assert profile_response.status_code in {200, 201}, profile_response.text

    # Création d'une mesure de poids.
    measurement_response = client.post(
        MEASUREMENTS_URL,
        json={
            "date": "2026-11-08",
            "weight_kg": 85,
        },
        headers=headers,
    )
    assert measurement_response.status_code == 201, measurement_response.text

    # Création de l'objectif nutritionnel.
    goal_response = client.post(
        NUTRITION_GOAL_URL,
        json={
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-11-01",
        },
        headers=headers,
    )
    assert goal_response.status_code == 201, goal_response.text

    # Création de la cible nutritionnelle active.
    target_response = client.post(
        f"{TARGET_URL}/recalculate",
        json={
            "reference_weight_kg": 85,
            "sex": "M",
            "birth_year": 1990,
            "height_cm": "180",
            "activity_level": "moderate",
        },
        headers=headers,
    )
    assert target_response.status_code == 201, target_response.text

    # L'onboarding est maintenant complet.
    final_response = client.get(
        f"{USERS_URL}/me/onboarding-status",
        headers=headers,
    )
    assert final_response.status_code == 200, final_response.text

    final_status = final_response.json()
    assert final_status["is_complete"] is True
    assert final_status["missing_steps"] == []
    assert final_status["steps"] == {
        "profile": True,
        "body_measurement": True,
        "nutrition_goal": True,
        "goal_target": True,
    }