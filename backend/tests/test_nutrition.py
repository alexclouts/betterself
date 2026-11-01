from decimal import Decimal

import pytest

from tests.utils import (
    auth_headers,
    register_and_login,
    register_and_login_other_user,
)


# Fonction utilitaire pour créer un objectif nutritionnel
def create_nutrition_goal(client, access_token: str, payload: dict):
    return client.post(
        "/nutrition-goals",
        json=payload,
        headers=auth_headers(access_token),
    )


# Fonction utilitaire pour récupérer l'objectif nutritionnel courant
def get_nutrition_goal(client, access_token: str):
    return client.get(
        "/nutrition-goals/current",
        headers=auth_headers(access_token),
    )


# Fonction utilitaire pour modifier l'objectif nutritionnel courant
def update_nutrition_goal(client, access_token: str, payload: dict):
    return client.patch(
        "/nutrition-goals/current",
        json=payload,
        headers=auth_headers(access_token),
    )


# Données valides réutilisées par plusieurs tests
def valid_nutrition_goal_payload() -> dict:
    return {
        "goal_type": "lose_weight",
        "start_weight_kg": 85,
        "target_weight_kg": 75,
        "start_date": "2026-10-01",
        "target_date": "2026-12-01",
    }


"""
Tests pour la création de l'objectif nutritionnel durant le onboarding.
"""


# Test pour vérifier la création réussie d'un objectif nutritionnel
def test_create_nutrition_goal_success(client):
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
def test_create_nutrition_goal_already_exists(client):
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


# Test pour vérifier la création échoue sans authentification
def test_create_nutrition_goal_unauthorized(client):
    response = client.post(
        "/nutrition-goals",
        json=valid_nutrition_goal_payload(),
    )

    assert response.status_code == 401


# Test pour vérifier la création échoue lorsque le champ goal_type est manquant
def test_create_nutrition_goal_missing_goal_type(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload.pop("goal_type")

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ start_weight_kg est manquant
def test_create_nutrition_goal_missing_start_weight(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload.pop("start_weight_kg")

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ target_weight_kg est manquant
def test_create_nutrition_goal_missing_target_weight(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload.pop("target_weight_kg")

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ start_date est manquant
def test_create_nutrition_goal_missing_start_date(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload.pop("start_date")

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le champ goal_type est invalide
def test_create_nutrition_goal_invalid_goal_type(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload["goal_type"] = "invalid_goal_type"

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le poids de départ est invalide
def test_create_nutrition_goal_invalid_start_weight(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload["start_weight_kg"] = 25

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque le poids cible est invalide
def test_create_nutrition_goal_invalid_target_weight(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload["target_weight_kg"] = 600

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


# Test pour vérifier la création échoue lorsque la date cible précède la date de début
def test_create_nutrition_goal_target_date_before_start_date(client):
    access_token = register_and_login(client)

    payload = valid_nutrition_goal_payload()
    payload["start_date"] = "2026-12-01"
    payload["target_date"] = "2026-10-01"

    response = create_nutrition_goal(client, access_token, payload)

    assert response.status_code == 422


"""
Tests pour la récupération de l'objectif nutritionnel courant.

Puisqu'un utilisateur ne possède qu'un seul objectif, celui-ci est identifié
par son utilisateur. Il n'y a donc pas de route GET /nutrition-goals ni de
route GET /nutrition-goals/{goal_id}.
"""


# Test pour vérifier la récupération réussie de l'objectif courant
def test_get_nutrition_goal_success(client):
    access_token = register_and_login(client)

    creation_response = create_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )

    assert creation_response.status_code == 201

    created_goal = creation_response.json()

    response = get_nutrition_goal(client, access_token)

    assert response.status_code == 200

    goal = response.json()

    assert goal["user_id"] == created_goal["user_id"]
    assert goal["goal_type"] == "lose_weight"
    assert goal["status"] == "active"


# Test pour vérifier que la récupération échoue sans authentification
def test_get_nutrition_goal_unauthorized(client):
    response = client.get("/nutrition-goals/current")

    assert response.status_code == 401


# Test pour vérifier que la récupération échoue lorsqu'aucun objectif n'existe
def test_get_nutrition_goal_not_found(client):
    access_token = register_and_login(client)

    response = get_nutrition_goal(client, access_token)

    assert response.status_code == 404


# Test pour vérifier que chaque utilisateur ne peut accéder qu'à son objectif
def test_get_nutrition_goal_isolated_between_users(client):
    owner_token = register_and_login(client)

    creation_response = create_nutrition_goal(
        client,
        owner_token,
        valid_nutrition_goal_payload(),
    )

    assert creation_response.status_code == 201

    other_token = register_and_login_other_user(client)

    response = get_nutrition_goal(client, other_token)

    assert response.status_code == 404


"""
Tests pour la modification de l'objectif nutritionnel courant.

L'utilisateur ne crée pas un nouvel objectif : il modifie celui créé durant
le onboarding. La règle « un utilisateur = un objectif » est donc préservée.
"""


# Test pour vérifier la modification réussie de l'objectif courant
def test_update_nutrition_goal_success(client):
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

    response = update_nutrition_goal(
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
def test_update_nutrition_goal_unauthorized(client):
    response = client.patch(
        "/nutrition-goals/current",
        json=valid_nutrition_goal_payload(),
    )

    assert response.status_code == 401


# Test pour vérifier que la modification échoue lorsqu'aucun objectif n'existe
def test_update_nutrition_goal_not_found(client):
    access_token = register_and_login(client)

    response = update_nutrition_goal(
        client,
        access_token,
        valid_nutrition_goal_payload(),
    )

    assert response.status_code == 404