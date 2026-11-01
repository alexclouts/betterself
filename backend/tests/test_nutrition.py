from decimal import Decimal

from tests.utils import register_and_login, auth_headers, register_and_login_other_user
import pytest



# Fonction utilitaire pour créer un objectif nutritionnel
def create_nutrition_goal(client, access_token: str, payload: dict):
    return client.post(
        "/nutrition-goals",
        json=payload,
        headers=auth_headers(access_token),
    )


# Test pour vérifier la création réussie d'un objectif nutritionnel
def test_create_nutrition_goal_success(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 201

    goal = response.json()
    assert goal["goal_type"] == "lose_weight"

    assert Decimal(goal["start_weight_kg"]) == Decimal("85.00")
    assert Decimal(goal["target_weight_kg"]) == Decimal("75.00")

    assert goal["status"] == "active"
    assert goal["start_date"] == "2026-10-01"
    assert goal["target_date"] == "2026-12-01"


# Test pour vérifier la création échoue sans authentification
def test_create_nutrition_goal_unauthorized(client):
    response = client.post(
        "/nutrition-goals",
        json={
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75, 
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 401


# Test pour vérifier la création échoue lorsque le champ goal_type est manquant
def test_create_nutrition_goal_missing_goal_type(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ starting_weight_kg est manquant
def test_create_nutrition_goal_missing_starting_weight(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "weight_loss",
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ target_weight_kg est manquant
def test_create_nutrition_goal_missing_target_weight(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "weight_loss",
            "start_weight_kg": 85,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ start_date est manquant
def test_create_nutrition_goal_missing_start_date(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "weight_loss",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ goal_type est invalide
def test_create_nutrition_goal_invalid_goal_type(client):
    access_token = register_and_login(client)
    response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "invalid_goal_type",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    assert response.status_code == 422


"""
Tests pour la récupération des objectifs nutritionnels.
"""

# Test pour vérifier la récupération des objectifs nutritionnels réussit
def test_list_nutrition_goals_success(client):
    access_token = register_and_login(client)
    create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    response = client.get(
        "/nutrition-goals",
        headers=auth_headers(access_token)
    )
    assert response.status_code == 200
    goals = response.json()

    assert len(goals) == 1
    assert goals[0]["goal_type"] == "lose_weight"
    assert goals[0]["status"] == "active"


# Test pour vérifier la récupération des objectifs nutritionnels échoue lorsque l'utilisateur n'est pas authentifié
def test_list_nutrition_goals_unauthorized(client):
    response = client.get(
        "/nutrition-goals"
    )
    assert response.status_code == 401


# Test pour la récupération d'un seul objectif nutritionnel
def test_get_nutrition_goal_success(client):
    access_token = register_and_login(client)
    create_response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    goal_id = create_response.json()["id"]
    response = client.get(
        f"/nutrition-goals/{goal_id}",
        headers=auth_headers(access_token)
    )
    assert response.status_code == 200
    assert response.json()["id"] == goal_id


# Test pour vérifier la récupération d'un objectif nutritionnel par un autre utilisateur
def test_get_nutrition_goal_for_another_user(client):
    access_token = register_and_login(client)
    create_response = create_nutrition_goal(
        client,
        access_token,
        {
            "goal_type": "lose_weight",
            "start_weight_kg": 85,
            "target_weight_kg": 75,
            "start_date": "2026-10-01",
            "target_date": "2026-12-01",
        },
    )
    goal_id = create_response.json()["id"]
    other_access_token = register_and_login_other_user(client)
    response = client.get(
        f"/nutrition-goals/{goal_id}",
        headers=auth_headers(other_access_token)
    )
    assert response.status_code == 404


# Test pour vérifier la récupération d'un objectif nutritionnel inexistant
def test_get_nutrition_goal_not_found(client):
    access_token = register_and_login(client)
    response = client.get(
        "/nutrition-goals/9999",
        headers=auth_headers(access_token)
    )
    assert response.status_code == 404