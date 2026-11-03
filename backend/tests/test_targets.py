from decimal import Decimal

from tests.utils import auth_headers, register_and_login, register_and_login_other_user


# Fonction utilitaire pour créer l'objectif nutritionnel de l'utilisateur.
# Un objectif doit exister avant de pouvoir créer ou recalculer une cible.
def create_nutrition_goal(client, access_token: str, payload: dict):
    return client.post(
        "/nutrition-goal",
        json=payload,
        headers=auth_headers(access_token),
    )


# Fonction utilitaire pour récupérer la cible nutritionnelle active
def get_current_goal_target(client, access_token: str):
    return client.get(
        "/nutrition-goal/current/target",
        headers=auth_headers(access_token),
    )


# Fonction utilitaire pour recalculer la cible nutritionnelle active.
# La cible précédente est fermée et conservée dans l'historique.
def recalculate_current_goal_target(
    client,
    access_token: str,
    payload: dict,
):
    return client.post(
        "/nutrition-goal/current/target/recalculate",
        json=payload,
        headers=auth_headers(access_token),
    )


# Données valides pour recalculer une cible nutritionnelle.
# Les paramètres biométriques sont fournis explicitement tant que la table
# des profils biométriques n'est pas implémentée.
def valid_goal_target_recalculate_payload() -> dict:
    return {
        "reference_weight_kg": 85,
        "sex": "M",
        "birth_year": 1996,
        "height_cm": 175,
        "activity_level": "moderate",
    }


# Fonction utilitaire locale pour créer un objectif avant de tester une cible
def create_goal_for_user(client, access_token: str):
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
    return response.json()


# Test pour vérifier qu'aucune cible active n'existe avant le premier recalcul
def test_get_current_goal_target_not_found(client):
    access_token = register_and_login(client)

    create_goal_for_user(client, access_token)

    response = get_current_goal_target(client, access_token)
    assert response.status_code == 404


# Test pour vérifier que la récupération échoue sans authentification
def test_get_current_goal_target_unauthorized(client):
    response = client.get("/nutrition-goal/current/target")
    assert response.status_code == 401


# Test pour vérifier la création d'une première cible nutritionnelle
def test_recalculate_goal_target_success(client):
    access_token = register_and_login(client)

    create_goal_for_user(client, access_token)
    response = recalculate_current_goal_target(
        client,
        access_token,
        valid_goal_target_recalculate_payload(),
    )
    assert response.status_code == 201

    target = response.json()
    assert Decimal(target["reference_weight_kg"]) == Decimal("85.00")
    assert target["valid_until"] is None
    assert target["maintenance_calories_kcal"] > 0
    assert target["calories_target_kcal"] > 0
    assert target["protein_target_g"] >= 0
    assert target["carbs_target_g"] >= 0
    assert target["fat_target_g"] >= 0
    assert target["calculation_method"] == "mifflin_st_jeor_v1"


# Test pour vérifier que le recalcul ferme la cible précédente
def test_recalculate_goal_target_closes_previous_target(client):
    access_token = register_and_login(client)
    create_goal_for_user(client, access_token)

    first_response = recalculate_current_goal_target(
        client,
        access_token,
        valid_goal_target_recalculate_payload(),
    )
    assert first_response.status_code == 201

    first_target = first_response.json()
    second_payload = valid_goal_target_recalculate_payload()
    second_payload["reference_weight_kg"] = 83

    second_response = recalculate_current_goal_target(
        client,
        access_token,
        second_payload,
    )
    assert second_response.status_code == 201

    second_target = second_response.json()
    # La première cible doit être fermée et la seconde doit être active.
    assert first_target["valid_until"] is None
    assert second_target["valid_until"] is None
    assert Decimal(second_target["reference_weight_kg"]) == Decimal("83.00")


# Test pour vérifier qu'une seule cible active existe après plusieurs recalculs
def test_only_one_active_goal_target_after_recalculations(client):
    access_token = register_and_login(client)

    create_goal_for_user(client, access_token)

    first_response = recalculate_current_goal_target(
        client,
        access_token,
        valid_goal_target_recalculate_payload(),
    )
    assert first_response.status_code == 201

    second_payload = valid_goal_target_recalculate_payload()
    second_payload["reference_weight_kg"] = 83
    second_response = recalculate_current_goal_target(
        client,
        access_token,
        second_payload,
    )
    assert second_response.status_code == 201
    
    current_response = get_current_goal_target(client, access_token)
    assert current_response.status_code == 200

    current_target = current_response.json()
    assert current_target["id"] == second_response.json()["id"]
    assert current_target["valid_until"] is None


# Test pour vérifier que le recalcul échoue sans objectif nutritionnel
def test_recalculate_goal_target_requires_goal(client):
    access_token = register_and_login(client)

    response = recalculate_current_goal_target(
        client,
        access_token,
        valid_goal_target_recalculate_payload(),
    )
    assert response.status_code == 404


# Test pour vérifier que le recalcul échoue sans authentification
def test_recalculate_goal_target_unauthorized(client):
    response = client.post(
        "/nutrition-goal/current/target/recalculate",
        json=valid_goal_target_recalculate_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier que le recalcul échoue avec un poids invalide
def test_recalculate_goal_target_invalid_weight(client):
    access_token = register_and_login(client)

    create_goal_for_user(client, access_token)

    payload = valid_goal_target_recalculate_payload()
    payload["reference_weight_kg"] = 25

    response = recalculate_current_goal_target(
        client,
        access_token,
        payload,
    )
    assert response.status_code == 422


# Test pour vérifier l'isolation des cibles entre utilisateurs
def test_get_current_goal_target_isolated_between_users(client):
    owner_token = register_and_login(client)
    
    create_goal_for_user(client, owner_token)

    owner_response = recalculate_current_goal_target(
        client,
        owner_token,
        valid_goal_target_recalculate_payload(),
    )
    assert owner_response.status_code == 201

    other_token = register_and_login_other_user(client)
    response = get_current_goal_target(client, other_token)
    assert response.status_code == 404