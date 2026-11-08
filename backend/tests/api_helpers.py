
"""
Helpers pour les tests d'intégration de l'API.
"""

FOODS_URL = "/foods"
RECIPES_URL = "/recipes"
CONSUMPTIONS_URL = "/food-consumptions"
NUTRITION_GOAL_URL = "/nutrition-goal"
MEASUREMENTS_URL = "/measurements"
AUTH_URL = "/auth"
USERS_URL = "/users"
TARGET_URL = "/nutrition-goal/current/target"


"""
Crée un aliment manuel et retourne sa représentation JSON.
"""
def create_food(
    client,
    headers: dict,
    name: str = "Yogourt grec nature",
    reference_weight_g: int = 100,
    calories_kcal: int = 370,
    protein_g: int = 20,
    carbohydrates_g: int = 50,
    fat_g: int = 10,
) -> dict:    
    response = client.post(
        FOODS_URL,
        json={
            "name": name,
            "brand": "Leclerc",
            "category": "dairy",
            "reference_weight_g": reference_weight_g,
            "calories_kcal": calories_kcal,
            "protein_g": protein_g,
            "carbohydrates_g": carbohydrates_g,
            "fat_g": fat_g,
            "source": "manual",
        },
        headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


"""
Crée une recette et retourne sa représentation JSON.
"""
def create_recipe(
    client,
    headers: dict,
    name: str = "Bol de poulet et riz",
) -> dict:
    response = client.post(
        RECIPES_URL,
        json={
            "name": name,
            "description": "Repas riche en protéines.",
            "total_weight_g": "800",
            "servings": 4,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


"""
Ajoute un aliment à une recette.
"""
def create_recipe_ingredient(
    client,
    headers: dict,
    recipe_id: str,
    food_id: str,
    quantity_g: str,
) -> dict:
    response = client.post(
        f"{RECIPES_URL}/{recipe_id}/ingredients",
        json={
            "food_id": food_id,
            "quantity_g": quantity_g,
            "recipe_id": recipe_id
        },
        headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


"""
Crée un objectif nutritionnel et retourne sa représentation JSON.
"""
def create_nutrition_goal(client, headers: dict) -> dict:
    response = client.post(
        NUTRITION_GOAL_URL,
        json={
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-11-01",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def recalculate_target(
    client,
    headers: dict,
    reference_weight_kg: float,
) -> dict:
    response = client.post(
        f"{NUTRITION_GOAL_URL}/current/target/recalculate",
        json={
            "reference_weight_kg": reference_weight_kg,
            "sex": "M",
            "birth_year": 1990,
            "height_cm": 180,
            "activity_level": "moderate",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def get_active_target(client, headers: dict) -> dict:
    response = client.get(
        f"{NUTRITION_GOAL_URL}/current/target",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()

