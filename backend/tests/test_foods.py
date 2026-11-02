from decimal import Decimal

from tests.utils import auth_headers, register_and_login, register_and_login_other_user


FOODS_URL = "/foods"


# Données valides pour créer un aliment manuellement.
# Calories cohérentes : 20 * 4 + 50 * 4 + 10 * 9 = 250 kcal.
def valid_food_payload() -> dict:
    return {
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
    }


# Test pour vérifier la création d'un aliment manuel
def test_create_food_success(client):
    access_token = register_and_login(client)

    response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert response.status_code == 201

    food = response.json()
    assert food["name"] == "Yogourt grec nature"


# Test pour vérifier que la création échoue sans authentification
def test_create_food_unauthorized(client):
    response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier que les calories incohérentes sont refusées
def test_create_food_rejects_inconsistent_calories(client):
    access_token = register_and_login(client)

    payload = valid_food_payload()
    payload["calories_kcal"] = 1000

    response = client.post(
        FOODS_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que les calories proches du calcul sont acceptées
def test_create_food_accepts_calorie_tolerance(client):
    access_token = register_and_login(client)

    payload = valid_food_payload()
    payload["calories_kcal"] = 380

    response = client.post(
        FOODS_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 201


# Test pour vérifier qu'un poids de référence invalide est refusé
def test_create_food_rejects_invalid_reference_weight(client):
    access_token = register_and_login(client)

    payload = valid_food_payload()
    payload["reference_weight_g"] = 0

    response = client.post(
        FOODS_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que les macros négatives sont refusées
def test_create_food_rejects_negative_macros(client):
    access_token = register_and_login(client)

    payload = valid_food_payload()
    payload["protein_g"] = -1

    response = client.post(
        FOODS_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier qu'une catégorie invalide est refusée
def test_create_food_rejects_invalid_category(client):
    access_token = register_and_login(client)

    payload = valid_food_payload()
    payload["category"] = "unknown_category"

    response = client.post(
        FOODS_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier la récupération d'un aliment
def test_get_food_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    response = client.get(
        f"{FOODS_URL}/{created_food['id']}",
    )
    assert response.status_code == 200

    food = response.json()
    assert food["id"] == created_food["id"]
    assert food["name"] == "Yogourt grec nature"


# Test pour vérifier qu'un aliment inexistant retourne 404
def test_get_food_not_found(client):
    response = client.get(
        f"{FOODS_URL}/00000000-0000-0000-0000-000000000000",
    )
    assert response.status_code == 404


# Test pour vérifier la recherche par nom
def test_search_foods_by_name(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    response = client.get(
        FOODS_URL,
        params={"query": "yogourt"},
    )
    assert response.status_code == 200

    foods = response.json()
    assert len(foods) >= 1
    assert any("Yogourt grec nature" == food["name"] for food in foods)


# Test pour vérifier la recherche par marque
def test_search_foods_by_brand(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    response = client.get(
        FOODS_URL,
        params={"query": "Leclerc"},
    )
    assert response.status_code == 200

    foods = response.json()
    assert len(foods) >= 1
    assert any(food["brand"] == "Leclerc" for food in foods)


# Test pour vérifier le filtre par catégorie
def test_search_foods_by_category(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    response = client.get(
        FOODS_URL,
        params={"category": "dairy"},
    )
    assert response.status_code == 200

    foods = response.json()
    assert len(foods) >= 1
    assert all(food["category"] == "dairy" for food in foods)


# Test pour vérifier que la recherche ne retourne pas de résultat inexistant
def test_search_foods_no_result(client):
    response = client.get(
        FOODS_URL,
        params={"query": "aliment-inexistant-12345"},
    )
    assert response.status_code == 200
    assert response.json() == []


# Test pour vérifier la pagination avec limit et offset
def test_search_foods_pagination(client):
    access_token = register_and_login(client)

    for index in range(3):
        payload = valid_food_payload()
        payload["name"] = f"Yogourt grec nature {index + 1}"

        creation_response = client.post(
            FOODS_URL,
            json=payload,
            headers=auth_headers(access_token),
        )
        assert creation_response.status_code == 201

    first_page = client.get(
        FOODS_URL,
        params={"query": "Yogourt grec nature", "limit": 2, "offset": 0},
    )
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2

    second_page = client.get(
        FOODS_URL,
        params={"query": "Yogourt grec nature", "limit": 2, "offset": 2},
    )
    assert second_page.status_code == 200
    assert len(second_page.json()) == 1

# Test pour vérifier la modification des informations descriptives
def test_update_food_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    update_payload = {
        "name": "Yogourt grec nature 2 %",
        "brand": "Nouvelle marque",
        "description": "Description mise à jour",
    }
    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json=update_payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    food = response.json()
    assert food["name"] == "Yogourt grec nature 2 %"
    assert food["brand"] == "Nouvelle marque"
    assert food["description"] == "Description mise à jour"

    # Les valeurs nutritionnelles doivent rester immuables.
    assert food["reference_weight_g"] == created_food["reference_weight_g"]
    assert food["calories_kcal"] == created_food["calories_kcal"]
    assert food["protein_g"] == created_food["protein_g"]
    assert food["carbohydrates_g"] == created_food["carbohydrates_g"]
    assert food["fat_g"] == created_food["fat_g"]


# Test pour vérifier qu'une valeur nutritionnelle non modifiable est ignorée
def test_update_food_immutable_value(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json={
            "calories_kcal": 999,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    food = response.json()
    # La valeur envoyée doit être ignorée.
    assert food["calories_kcal"] == created_food["calories_kcal"]
    assert food["calories_kcal"] != 999


# Test pour vérifier que le nom ne peut pas être vide
def test_update_food_rejects_empty_name(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json={"name": "   "},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour partielle conserve les autres champs
def test_update_food_partial_update(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json={"description": "Seule la description change."},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    food = response.json()
    assert food["name"] == created_food["name"]
    assert food["brand"] == created_food["brand"]
    assert food["description"] == "Seule la description change."


# Test pour vérifier qu'un utilisateur ne peut pas modifier l'aliment d'un autre
def test_update_food_forbidden_for_other_user(client):
    owner_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    other_token = register_and_login_other_user(client)

    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json={"name": "Nom non autorisé"},
        headers=auth_headers(other_token),
    )
    assert response.status_code == 403


# Test pour vérifier que la modification échoue sans authentification
def test_update_food_unauthorized(client):
    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(register_and_login(client)),
    )

    assert creation_response.status_code == 201

    created_food = creation_response.json()

    response = client.patch(
        f"{FOODS_URL}/{created_food['id']}",
        json={"name": "Nom non autorisé"},
    )

    assert response.status_code == 401


# Test pour vérifier qu'un aliment inexistant retourne 404
def test_update_food_not_found(client):
    access_token = register_and_login(client)

    response = client.patch(
        f"{FOODS_URL}/00000000-0000-0000-0000-000000000000",
        json={"name": "Aliment inexistant"},
        headers=auth_headers(access_token),
    )

    assert response.status_code == 404


# Test pour vérifier la suppression d'un aliment manuel
def test_delete_food_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    delete_response = client.delete(
        f"{FOODS_URL}/{created_food['id']}",
        headers=auth_headers(access_token),
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"{FOODS_URL}/{created_food['id']}",
    )
    assert get_response.status_code == 404


# Test pour vérifier qu'un utilisateur ne peut pas supprimer l'aliment d'un autre
def test_delete_food_forbidden_for_other_user(client):
    owner_token = register_and_login(client)
    
    creation_response = client.post(
        FOODS_URL,
        json=valid_food_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    created_food = creation_response.json()
    other_token = register_and_login_other_user(client)

    delete_response = client.delete(
        f"{FOODS_URL}/{created_food['id']}",
        headers=auth_headers(other_token),
    )
    assert delete_response.status_code == 403