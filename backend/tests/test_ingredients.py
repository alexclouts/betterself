from decimal import Decimal

from tests.utils import auth_headers, register_and_login, register_and_login_other_user


RECIPES_URL = "/recipes"
FOODS_URL = "/foods"


# Crée un utilisateur, le connecte et retourne ses en-têtes d'authentification
def get_auth_headers(client) -> dict:
    access_token = register_and_login(client)
    return auth_headers(access_token)


# Crée une recette et retourne sa représentation JSON
def create_recipe(client, headers: dict) -> dict:
    response = client.post(
        RECIPES_URL,
        json={
            "name": "Bol de poulet et riz",
            "description": "Recette de test.",
            "total_weight_g": 800,
            "servings": 6,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


# Crée un aliment et retourne sa représentation JSON
def create_food(client, headers: dict) -> dict:
    response = client.post(
        FOODS_URL,
        json={
            "name": "Yogourt grec nature",
            "brand": "Leclerc",
            "category": "dairy",
            "reference_weight_g": 100,
            "calories_kcal": 370,
            "protein_g": 20,
            "carbohydrates_g": 50,
            "fat_g": 10,
            "source": "manual",
            "external_reference_id": None,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


# URL des ingrédients d'une recette
def ingredients_url(recipe_id: str) -> str:
    return f"{RECIPES_URL}/{recipe_id}/ingredients"


# URL d'un ingrédient précis
def ingredient_url(recipe_id: str, ingredient_id: str) -> str:
    return f"{RECIPES_URL}/{recipe_id}/ingredients/{ingredient_id}"


# Données valides pour créer un ingrédient
def valid_ingredient_payload(recipe_id: str, food_id: str) -> dict:
    return {
        "recipe_id": recipe_id,
        "food_id": food_id,
        "quantity_g": 150,
    }


# Test pour vérifier l'ajout d'un ingrédient à une recette
def test_create_recipe_ingredient_success(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=headers,
    )
    assert response.status_code == 201

    ingredient = response.json()
    assert ingredient["recipe_id"] == recipe["id"]
    assert ingredient["food_id"] == food["id"]
    assert Decimal(ingredient["quantity_g"]) == Decimal("150.00")


# Test pour vérifier que la création échoue sans authentification
def test_create_recipe_ingredient_unauthorized(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
    )
    assert response.status_code == 401


# Test pour vérifier qu'un utilisateur ne peut pas ajouter un ingrédient
# à la recette d'un autre utilisateur
def test_create_recipe_ingredient_forbidden_for_other_user(client):
    owner_headers = get_auth_headers(client)

    recipe = create_recipe(client, owner_headers)
    food = create_food(client, owner_headers)

    # Enregistrement et connexion d'un autre utilisateur
    other_token = register_and_login_other_user(client)
    other_headers = auth_headers(other_token)

    response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=other_headers,
    )
    assert response.status_code == 404


# Test pour vérifier qu'une quantité nulle est refusée
def test_create_recipe_ingredient_rejects_zero_quantity(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    payload = valid_ingredient_payload(recipe["id"], food["id"])
    # Test avec une quantité nulle
    payload["quantity_g"] = 0

    response = client.post(
        ingredients_url(recipe["id"]),
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier qu'une quantité négative est refusée
def test_create_recipe_ingredient_rejects_negative_quantity(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    payload = valid_ingredient_payload(recipe["id"], food["id"])
    # Quantité négative
    payload["quantity_g"] = -10

    response = client.post(
        ingredients_url(recipe["id"]),
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier qu'un aliment inexistant est refusé
def test_create_recipe_ingredient_rejects_unknown_food(client):
    headers = get_auth_headers(client)
    recipe = create_recipe(client, headers)

    payload = {
        "food_id": "00000000-0000-0000-0000-000000000999",
        "recipe_id": recipe["id"],
        "quantity_g": 150,
    }
    # Tentative d'ajout d'un aliment inexistant à la recette
    response = client.post(
        ingredients_url(recipe["id"]),
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404


# Test pour vérifier qu'un même aliment ne peut pas être ajouté deux fois
# à la même recette
def test_create_recipe_ingredient_rejects_duplicate_food(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    payload = valid_ingredient_payload(recipe["id"], food["id"])

    first_response = client.post(
        ingredients_url(recipe["id"]),
        json=payload,
        headers=headers,
    )
    assert first_response.status_code == 201
    # Tentative d'ajout du même aliment à la même recette
    second_response = client.post(
        ingredients_url(recipe["id"]),
        json=payload,
        headers=headers,
    )
    # Vérification que la tentative d'ajout dupliqué a été refusée
    assert second_response.status_code == 409


# Test pour vérifier la récupération d'un ingrédient
def test_get_recipe_ingredient_success(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    creation_response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_ingredient = creation_response.json()
    # Récupération de l'ingrédient créé
    response = client.get(
        ingredient_url(recipe["id"], created_ingredient["id"]),
        headers=headers,
    )
    assert response.status_code == 200

    ingredient = response.json()
    assert ingredient["id"] == created_ingredient["id"]
    assert ingredient["recipe_id"] == recipe["id"]
    assert Decimal(ingredient["quantity_g"]) == Decimal("150.00")


# Test pour vérifier qu'un ingrédient inexistant retourne 404
def test_get_recipe_ingredient_not_found(client):
    headers = get_auth_headers(client)
    recipe = create_recipe(client, headers)

    response = client.get(
        ingredient_url(
            recipe["id"],
            "00000000-0000-0000-0000-000000000000",
        ),
        headers=headers,
    )
    assert response.status_code == 404


# Test pour vérifier la mise à jour de la quantité d'un ingrédient
def test_update_recipe_ingredient_success(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    creation_response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_ingredient = creation_response.json()
    # Mise à jour avec une quantité valide
    response = client.patch(
        ingredient_url(recipe["id"], created_ingredient["id"]),
        json={"quantity_g": 200},
        headers=headers,
    )
    assert response.status_code == 200

    ingredient = response.json()
    # Vérification que la quantité a bien été mise à jour
    assert Decimal(ingredient["quantity_g"]) == Decimal("200.00")
    assert ingredient["food_id"] == food["id"]


# Test pour vérifier qu'une quantité invalide est refusée lors de la mise à jour
def test_update_recipe_ingredient_rejects_invalid_quantity(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    creation_response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_ingredient = creation_response.json()
    # Tentative de mise à jour avec une quantité invalide
    response = client.patch(
        ingredient_url(recipe["id"], created_ingredient["id"]),
        json={"quantity_g": 0},
        headers=headers,
    )
    # Vérification que la mise à jour a été refusée
    assert response.status_code == 422


# Test pour vérifier la suppression d'un ingrédient
def test_delete_recipe_ingredient_success(client):
    headers = get_auth_headers(client)

    recipe = create_recipe(client, headers)
    food = create_food(client, headers)

    creation_response = client.post(
        ingredients_url(recipe["id"]),
        json=valid_ingredient_payload(recipe["id"], food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_ingredient = creation_response.json()
    # Suppression de l'ingrédient créé
    delete_response = client.delete(
        ingredient_url(recipe["id"], created_ingredient["id"]),
        headers=headers,
    )
    assert delete_response.status_code == 204

    # Vérification que l'ingrédient a bien été supprimé
    get_response = client.get(
        ingredient_url(recipe["id"], created_ingredient["id"]),
        headers=headers,
    )
    assert get_response.status_code == 404