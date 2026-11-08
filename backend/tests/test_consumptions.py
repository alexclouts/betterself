from decimal import Decimal

from tests.utils import auth_headers, register_and_login, register_and_login_other_user
from tests.api_helpers import create_food, create_recipe, CONSUMPTIONS_URL


# Crée un utilisateur, le connecte et retourne ses en-têtes d'authentification
def get_auth_headers(client) -> dict:
    access_token = register_and_login(client)
    return auth_headers(access_token)


# URL d'une consommation précise
def consumption_url(consumption_id: str) -> str:
    return f"{CONSUMPTIONS_URL}/{consumption_id}"


# Données pour consommer un aliment
def food_consumption_payload(food_id: str) -> dict:
    return {
        "food_id": food_id,
        "quantity_g": 100,
        "meal_type": "breakfast",
    }


# Données pour consommer une recette
def recipe_consumption_payload(recipe_id: str) -> dict:
    return {
        "recipe_id": recipe_id,
        "quantity_g": 200,
        "meal_type": "lunch",
    }


# Test pour vérifier l'ajout d'un aliment au journal
def test_create_food_consumption_success(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert response.status_code == 201

    consumption = response.json()
    assert consumption["food_id"] == food["id"]
    assert consumption["recipe_id"] is None
    assert consumption["item_name_snapshot"] == food["name"]
    assert Decimal(consumption["quantity_g"]) == Decimal("100.00")

    # 100 g correspond exactement au poids de référence.
    assert Decimal(consumption["calories_kcal"]) == Decimal("370.00")
    assert Decimal(consumption["protein_g"]) == Decimal("20.00")
    assert Decimal(consumption["carbohydrates_g"]) == Decimal("50.00")
    assert Decimal(consumption["fat_g"]) == Decimal("10.00")


# Test pour vérifier l'ajout d'une recette au journal
def test_create_recipe_consumption_success(client):
    headers = get_auth_headers(client)
    recipe = create_recipe(client, headers)

    response = client.post(
        CONSUMPTIONS_URL,
        json=recipe_consumption_payload(recipe["id"]),
        headers=headers,
    )
    assert response.status_code == 201, response.text

    consumption = response.json()
    assert consumption["recipe_id"] == recipe["id"]
    assert consumption["food_id"] is None
    assert consumption["item_name_snapshot"] == recipe["name"]
    assert Decimal(consumption["quantity_g"]) == Decimal("200.00")


# Test pour vérifier que la création échoue sans authentification
def test_create_food_consumption_unauthorized(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
    )
    assert response.status_code == 401


# Test pour vérifier que food_id et recipe_id ne peuvent pas coexister
def test_create_consumption_rejects_food_and_recipe(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)
    recipe = create_recipe(client, headers)

    payload = food_consumption_payload(food["id"])
    payload["recipe_id"] = recipe["id"]

    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier qu'une source est obligatoire
def test_create_consumption_rejects_missing_source(client):
    headers = get_auth_headers(client)
    payload = {
        "quantity_g": 100,
        "meal_type": "breakfast",
    }
    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier qu'un aliment inexistant est refusé
def test_create_food_consumption_rejects_unknown_food(client):
    headers = get_auth_headers(client)
    payload = {
        "food_id": "00000000-0000-0000-0000-000000000999",
        "quantity_g": 100,
        "meal_type": "breakfast",
    }
    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404


# Test pour vérifier qu'une recette inexistante est refusée
def test_create_recipe_consumption_rejects_unknown_recipe(client):
    headers = get_auth_headers(client)
    payload = {
        "recipe_id": "00000000-0000-0000-0000-000000000999",
        "quantity_g": 200,
        "meal_type": "lunch",
    }
    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404


# Test pour vérifier qu'une quantité nulle est refusée
def test_create_consumption_rejects_zero_quantity(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    payload = food_consumption_payload(food["id"])
    payload["quantity_g"] = 0

    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier qu'une quantité négative est refusée
def test_create_consumption_rejects_negative_quantity(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)
    # Crée une consommation alimentaire avec une quantité négative pour le test
    payload = food_consumption_payload(food["id"])
    payload["quantity_g"] = -50

    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422


# Test pour vérifier que la nutrition est proportionnelle à la quantité
def test_create_food_consumption_calculates_scaled_nutrition(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)
    # Crée une consommation alimentaire avec une quantité spécifique
    payload = food_consumption_payload(food["id"])
    payload["quantity_g"] = 50

    response = client.post(
        CONSUMPTIONS_URL,
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201

    consumption = response.json()
    # 50 g représentent la moitié du poids de référence de 100 g.
    # Les valeurs nutritionnelles doivent être proportionnelles à la quantité (50 g sur 100 g)
    assert Decimal(consumption["calories_kcal"]) == Decimal("185.00")
    assert Decimal(consumption["protein_g"]) == Decimal("10.00")
    assert Decimal(consumption["carbohydrates_g"]) == Decimal("25.00")
    assert Decimal(consumption["fat_g"]) == Decimal("5.00")


# Test pour vérifier la récupération d'une consommation
def test_get_food_consumption_success(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    response = client.get(
        consumption_url(created_consumption["id"]),
        headers=headers,
    )
    assert response.status_code == 200

    consumption = response.json()
    assert consumption["id"] == created_consumption["id"]
    assert consumption["food_id"] == food["id"]


# Test pour vérifier qu'une consommation inexistante retourne 404
def test_get_food_consumption_not_found(client):
    headers = get_auth_headers(client)
    response = client.get(
        consumption_url("00000000-0000-0000-0000-000000000000"),
        headers=headers,
    )
    assert response.status_code == 404


# Test pour vérifier qu'un utilisateur ne peut pas lire la consommation d'un autre
def test_get_food_consumption_forbidden_for_other_user(client):
    owner_headers = get_auth_headers(client)
    food = create_food(client, owner_headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=owner_headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    other_token = register_and_login_other_user(client)
    other_headers = auth_headers(other_token)
    # Essaie de récupérer la consommation créée avec un autre utilisateur
    response = client.get(
        consumption_url(created_consumption["id"]),
        headers=other_headers,
    )
    assert response.status_code == 404


# Test pour vérifier la liste des consommations
def test_list_food_consumptions(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    # Crée deux consommations alimentaires pour le test de liste
    first_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    second_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 201
    # Récupère la liste des consommations pour l'utilisateur courant
    response = client.get(
        CONSUMPTIONS_URL,
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


# Test pour vérifier l'isolation des consommations entre utilisateurs
def test_list_food_consumptions_isolated_between_users(client):
    owner_headers = get_auth_headers(client)
    food = create_food(client, owner_headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=owner_headers,
    )
    assert creation_response.status_code == 201

    other_token = register_and_login_other_user(client)
    other_headers = auth_headers(other_token)
    # Essaie de récupérer la liste des consommations avec un autre utilisateur
    response = client.get(
        CONSUMPTIONS_URL,
        headers=other_headers,
    )
    assert response.status_code == 200
    assert response.json() == []


# Test pour vérifier la mise à jour de la quantité et du recalcul nutritionnel
def test_update_food_consumption_recalculates_nutrition(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    # Met à jour la quantité de la consommation créée
    response = client.patch(
        consumption_url(created_consumption["id"]),
        json={"quantity_g": 50},
        headers=headers,
    )
    assert response.status_code == 200
    # Vérifie que la réponse contient les nouvelles valeurs nutritionnelles recalculées
    consumption = response.json()
    assert Decimal(consumption["quantity_g"]) == Decimal("50.00")
    assert Decimal(consumption["calories_kcal"]) == Decimal("185.00")
    assert Decimal(consumption["protein_g"]) == Decimal("10.00")
    assert Decimal(consumption["carbohydrates_g"]) == Decimal("25.00")
    assert Decimal(consumption["fat_g"]) == Decimal("5.00")


# Test pour vérifier la mise à jour du type de repas
def test_update_food_consumption_meal_type(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    # Met à jour le type de repas de la consommation créée
    response = client.patch(
        consumption_url(created_consumption["id"]),
        json={"meal_type": "lunch"},
        headers=headers,
    )
    assert response.status_code == 200

    consumption = response.json()
    assert consumption["meal_type"] == "lunch"


# Test pour vérifier qu'un utilisateur ne peut pas modifier
# la consommation d'un autre utilisateur
def test_update_food_consumption_forbidden_for_other_user(client):
    owner_headers = get_auth_headers(client)
    food = create_food(client, owner_headers)

    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=owner_headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    other_token = register_and_login_other_user(client)
    other_headers = auth_headers(other_token)
    # Essaie de mettre à jour la consommation avec un autre utilisateur
    response = client.patch(
        consumption_url(created_consumption["id"]),
        json={"quantity_g": 50},
        headers=other_headers,
    )
    assert response.status_code == 404


# Test pour vérifier la suppression d'une consommation
def test_delete_food_consumption_success(client):
    headers = get_auth_headers(client)
    food = create_food(client, headers)
    # Crée une consommation alimentaire pour le test de suppression
    creation_response = client.post(
        CONSUMPTIONS_URL,
        json=food_consumption_payload(food["id"]),
        headers=headers,
    )
    assert creation_response.status_code == 201

    created_consumption = creation_response.json()
    # Supprime la consommation créée
    delete_response = client.delete(
        consumption_url(created_consumption["id"]),
        headers=headers,
    )
    assert delete_response.status_code == 204
    # Vérifie que la consommation a bien été supprimée en essayant de la récupérer
    get_response = client.get(
        consumption_url(created_consumption["id"]),
        headers=headers,
    )
    assert get_response.status_code == 404