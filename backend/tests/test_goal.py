from decimal import Decimal

from tests.utils import (
    auth_headers,
    register_and_login,
    register_and_login_other_user
)

# Fonction utilitaire pour créer l'objectif nutritionnel de l'utilisateur.
def create_nutrition_goal(client, access_token: str, payload: dict):
    return client.post(
        "/nutrition-goals",
        json=payload,
        headers=auth_headers(access_token),
    )

# Fonction utilitaire pour récupérer l'objectif nutritionnel actif
def get_current_nutrition_goal(client, access_token: str):
    return client.get(
        "/nutrition-goals/current",
        headers=auth_headers(access_token),
    )



# Fonction utilitaire pour modifier l'objectif nutritionnel actif
def update_current_nutrition_goal(
    client,
    access_token: str,
    payload: dict,
):
    return client.patch(
        "/nutrition-goals/current",
        json=payload,
        headers=auth_headers(access_token),
    )


# Données valides pour créer un objectif nutritionnel
def valid_nutrition_goal_payload() -> dict:
    return {
        "goal_type": "lose_weight",
        "start_weight_kg": 85,
        "target_weight_kg": 75,
        "start_date": "2026-10-01",
        "target_date": "2026-12-01",
    }

# Test pour vérifier la création réussie de l'objectif durant le onboarding
def test_create_goal_success(client):
    access_token = register_and_login(client)

    response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )

    assert response.status_code == 201

    goal = response.json()

    assert goal["goal_type"] == "lose_weight"
    assert Decimal(goal["start_weight_kg"]) == Decimal("85.00")
    assert Decimal(goal["target_weight_kg"]) == Decimal("75.00")
    assert goal["start_date"] == "2026-10-01"
    assert goal["target_date"] == "2026-12-01"
    assert goal["status"] == "active"
    assert goal["user_id"]


# Test pour vérifier qu'un utilisateur ne peut pas créer plusieurs objectifs
def test_create_goal_already_exists(client):
    access_token = register_and_login(client)

    first_response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )

    assert first_response.status_code == 201

    second_response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )

    assert second_response.status_code == 409


# Test pour vérifier que la création échoue sans authentification
def test_create_goal_unauthorized(client):
    response = client.post(
        "/nutrition-goals",
        json=valid_nutrition_goal_payload(),
    )

    assert response.status_code == 401


# Test pour vérifier la récupération de l'objectif courant
def test_get_current_goal_success(client):
    access_token = register_and_login(client)

    creation_response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )
    assert creation_response.status_code == 201

    created_goal = creation_response.json()
    response = get_current_nutrition_goal(client, access_token)
    assert response.status_code == 200

    goal = response.json()
    assert goal["user_id"] == created_goal["user_id"]
    assert goal["goal_type"] == "lose_weight"
    assert goal["status"] == "active"


# Test pour vérifier que la récupération échoue sans authentification
def test_get_current_goal_unauthorized(client):
    response = client.get("/nutrition-goals/current")
    assert response.status_code == 401


# Test pour vérifier que la récupération échoue sans objectif créé
def test_get_current_goal_not_found(client):
    access_token = register_and_login(client)

    response = get_current_nutrition_goal(client, access_token)
    assert response.status_code == 404


# Test pour vérifier l'isolation des objectifs entre utilisateurs
def test_get_current_goal_isolated_between_users(client):
    owner_token = register_and_login(client)

    creation_response = create_nutrition_goal(
        client,
        owner_token,
        valid_nutrition_goal_payload(),
    )
    assert creation_response.status_code == 201

    other_token = register_and_login_other_user(client)
    response = get_current_nutrition_goal(client, other_token)
    assert response.status_code == 404


# Test pour vérifier la modification de l'objectif existant
def test_update_current_goal_success(client):
    access_token = register_and_login(client)

    creation_response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )
    assert creation_response.status_code == 201

    update_payload = {
        "goal_type": "maintain_weight",
        "start_weight_kg": 84,
        "target_weight_kg": 84,
        "start_date": "2026-10-01",
        "target_date": "2026-12-01",
    }
    response = update_current_nutrition_goal(
        client,
        access_token,
        update_payload,
    )
    assert response.status_code == 200

    goal = response.json()
    assert goal["goal_type"] == "maintain_weight"
    assert Decimal(goal["start_weight_kg"]) == Decimal("84.00")
    assert Decimal(goal["target_weight_kg"]) == Decimal("84.00")
    assert goal["status"] == "active"


# Test pour vérifier que la modification échoue sans authentification
def test_update_current_goal_unauthorized(client):
    response = client.patch(
        "/nutrition-goals/current",
        json=valid_nutrition_goal_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier que la modification échoue sans objectif créé
def test_update_current_goal_not_found(client):
    access_token = register_and_login(client)

    response = update_current_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )
    assert response.status_code == 404