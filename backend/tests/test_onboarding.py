from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.api_helpers import ONBOARDING_URL, NUTRITION_GOAL_URL, PROFILE_URL, TARGET_URL
from tests.utils import auth_headers, register_and_login

# Retourne le payload pour la création d'un onboarding
def make_onboarding_create_payload(
    *,
    goal_type: str = "lose_weight",
    pace: str | None = "moderate",
    current_weight_kg: float = 80.0,
    target_weight_kg: float | None = 70.0,
) -> dict:
    return {
        "goal_type": goal_type,
        "pace": pace,
        "name": "Test User",
        "birth_year": 2000,
        "sex": "male",
        "height_cm": 180,
        "current_weight_kg": current_weight_kg,
        "target_weight_kg": target_weight_kg,
        "activity_level": "moderately_active",
    }


# Teste la prévisualisation de l'objectif de perte de poids et vérifie le timeline estimé.
def test_preview_goal_weight_loss_returns_timeline(
    client: TestClient,
) -> None:
    payload = make_onboarding_create_payload(
        goal_type="lose_weight",
        pace="moderate",
        current_weight_kg=80.0,
        target_weight_kg=70.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["goal_type"] == "lose_weight"
    assert data["pace"] == "moderate"
    assert Decimal(str(data["current_weight_kg"])) == Decimal("80.0")
    assert Decimal(str(data["target_weight_kg"])) == Decimal("70.0")
    assert Decimal(str(data["estimated_weeks"])) == Decimal("22.0")
    assert date.fromisoformat(data["estimated_completion_date"]) == (date.today() + timedelta(days=154))
    assert int(data["first_target_calories_kcal"]) > 0


# Vérifie l'ajustement positif des calories pour l'objectif de gain musculaire
def test_preview_goal_muscle_gain_returns_positive_adjustment(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="gain_muscle",
        pace="moderate",
        current_weight_kg=70.0,
        target_weight_kg=80.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload
    )
    print(response.json())
    assert response.status_code == 200

    data = response.json()
    assert data["goal_type"] == "gain_muscle"
    assert data["pace"] == "moderate"
    assert Decimal(str(data["current_weight_kg"])) == Decimal("70.0")
    assert Decimal(str(data["target_weight_kg"])) == Decimal("80.0")

    assert Decimal(str(data["estimated_weeks"])) == Decimal("22.0")
    assert int(data["first_target_calories_kcal"]) > 1200


# Vérifie que l'objectif de maintien n'a pas de timeline estimée et que les calories cibles sont correctes.
def test_preview_goal_maintenance_has_no_timeline(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="maintain_weight",
        pace=None,
        current_weight_kg=80.0,
        target_weight_kg=80.0,
    )

    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["goal_type"] == "maintain_weight"
    assert data["pace"] is None
    assert data["estimated_weeks"] is None
    assert data["estimated_completion_date"] is None
    assert int(data["first_target_calories_kcal"]) > 1200


# Vérifie que la prévisualisation de l'objectif ne crée pas de profil utilisateur.
def test_preview_goal_does_not_create_profile(
    client: TestClient
) -> None:
    access_token = register_and_login(client)
    payload = make_onboarding_create_payload()

    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    # Vérifier que le profile n'a pas été créé
    response = client.get(
        PROFILE_URL,
        headers=auth_headers(access_token)
    )
    assert response.status_code == 404




# Vérifie que la prévisualisation de l'objectif ne crée pas d'objectif nutritionnel.
def test_preview_goal_does_not_create_nutrition_goal(client: TestClient) -> None:
    access_token = register_and_login(client)
    payload = make_onboarding_create_payload()

    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
        headers=auth_headers(access_token)
    )
    assert response.status_code == 200
    # Vérifier que le nutrition goal n'a pas été créé
    goal = client.get(
        f"{NUTRITION_GOAL_URL}/current",
        headers=auth_headers(access_token)
    )
    assert goal.status_code == 404


# Vérifie que la prévisualisation de l'objectif ne crée pas de cible nutritionnelle.
def test_preview_goal_does_not_create_goal_target(
    client: TestClient,
) -> None:
    access_token = register_and_login(client)
    payload = make_onboarding_create_payload()

    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    # Vérifier que le goal target n'a pas été créé
    response = client.get(
        TARGET_URL,
        headers=auth_headers(access_token)
    )
    assert response.status_code == 404


# Un objectif de perte de poids doit avoir un rythme défini.
def test_preview_goal_rejects_missing_pace_for_weight_loss(
    client: TestClient
) -> None:
    payload = make_onboarding_create_payload(
        goal_type="lose_weight",
        pace=None,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422

    data = response.json()
    assert "pace" in str(data)


# Un objectif de gain musculaire doit avoir un rythme défini.
def test_preview_goal_rejects_missing_pace_for_muscle_gain(
    client: TestClient
) -> None:
    payload = make_onboarding_create_payload(
        goal_type="gain_muscle",
        pace=None,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422

    data = response.json()
    assert "pace" in str(data)


# Un objectif de perte de poids ne peut pas avoir un poids cible égal au poids actuel.
def test_preview_goal_rejects_target_equal_to_current_for_weight_loss(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="lose_weight",
        pace="moderate",
        current_weight_kg=80.0,
        target_weight_kg=80.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422


# Un objectif de perte de poids ne peut pas avoir un poids cible supérieur au poids actuel.
def test_preview_goal_rejects_target_above_current_for_weight_loss(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="lose_weight",
        pace="moderate",
        current_weight_kg=80.0,
        target_weight_kg=90.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422


# Un objectif de gain musculaire ne peut pas avoir un poids cible inférieur au poids actuel.
def test_preview_goal_rejects_target_below_current_for_muscle_gain(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="gain_muscle",
        pace="moderate",
        current_weight_kg=80.0,
        target_weight_kg=70.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422


# Un objectif de maintien ne doit pas avoir de rythme défini.
def test_preview_goal_rejects_pace_for_maintenance(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        goal_type="maintain_weight",
        pace="moderate",
        current_weight_kg=80.0,
        target_weight_kg=80.0,
    )

    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )

    assert response.status_code == 422


# Un objectif de perte de poids doit avoir un poids actuel valide.
def test_preview_goal_rejects_invalid_current_weight(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        current_weight_kg=20.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422


# Un objectif de perte de poids doit avoir un poids cible valide.
def test_preview_goal_rejects_invalid_target_weight(client: TestClient) -> None:
    payload = make_onboarding_create_payload(
        target_weight_kg=400.0,
    )
    response = client.post(
        f"{ONBOARDING_URL}/preview",
        json=payload,
    )
    assert response.status_code == 422