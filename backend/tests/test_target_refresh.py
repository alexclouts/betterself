from datetime import date, timedelta
from decimal import Decimal

from tests.api_helpers import MEASUREMENTS_URL, ONBOARDING_URL, PROFILE_URL, TARGET_URL
from tests.test_onboarding import make_onboarding_create_payload
from tests.utils import auth_headers, register_and_login

"""
Tests du recalcul automatique de la cible nutritionnelle :
- après l'enregistrement d'un nouveau poids (le plus récent) ;
- après une modification du profil qui influence le calcul.
"""

# Profil identique à celui créé par make_onboarding_create_payload().
BASE_PROFILE = {
    "first_name": "Test",
    "year_of_birth": 2000,
    "sex": "male",
    "height_cm": 180,
    "activity_level": "moderately_active",
}


# Crée un utilisateur ayant terminé l'onboarding (profil, objectif, cible et mesure à 80 kg).
def onboarded_headers(client) -> dict:
    headers = auth_headers(register_and_login(client))
    response = client.post(ONBOARDING_URL, json=make_onboarding_create_payload(), headers=headers)
    assert response.status_code in (200, 201), response.text
    return headers


def active_target(client, headers: dict) -> dict:
    response = client.get(TARGET_URL, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def add_measurement(client, headers: dict, measurement_date: date, weight_kg: float):
    response = client.post(
        MEASUREMENTS_URL,
        json={"date": str(measurement_date), "weight_kg": weight_kg},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def update_profile(client, headers: dict, **changes):
    response = client.put(PROFILE_URL, json={**BASE_PROFILE, **changes}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


# Un nouveau poids devient le poids de référence de la cible active.
def test_new_measurement_recalculates_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    created = add_measurement(client, headers, date.today(), 75)

    after = active_target(client, headers)
    assert Decimal(str(after["reference_weight_kg"])) == Decimal("75")
    # La réponse indique au client l'ancienne et la nouvelle cible.
    assert created["target_update"] == {
        "status": "updated",
        "previous_calories_target_kcal": before["calories_target_kcal"],
        "calories_target_kcal": after["calories_target_kcal"],
        "message": None,
    }
    assert after["id"] != before["id"]
    assert after["calories_target_kcal"] < before["calories_target_kcal"]


# Une mesure antérieure à la plus récente ne change pas la cible.
def test_backdated_measurement_keeps_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    created = add_measurement(client, headers, date.today() - timedelta(days=10), 90)

    assert active_target(client, headers)["id"] == before["id"]
    assert created["target_update"] is None


# Changer seulement le prénom ne recalcule pas la cible.
def test_profile_first_name_change_keeps_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    updated = update_profile(client, headers, first_name="Autre")

    assert active_target(client, headers)["id"] == before["id"]
    assert updated["target_update"] is None


# Changer la taille recalcule la cible avec le dernier poids connu.
def test_profile_height_change_recalculates_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    updated = update_profile(client, headers, height_cm=170)

    after = active_target(client, headers)
    assert updated["target_update"]["status"] == "updated"
    assert updated["target_update"]["calories_target_kcal"] == after["calories_target_kcal"]
    assert after["id"] != before["id"]
    assert after["maintenance_calories_kcal"] < before["maintenance_calories_kcal"]
    assert Decimal(str(after["reference_weight_kg"])) == Decimal("80")


# Changer le niveau d'activité recalcule aussi la cible.
def test_profile_activity_change_recalculates_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    update_profile(client, headers, activity_level="very_active")

    after = active_target(client, headers)
    assert after["maintenance_calories_kcal"] > before["maintenance_calories_kcal"]


# Un profil donnant moins de 1200 kcal : le profil est enregistré, la cible est
# conservée et la réponse explique l'échec.
def test_profile_change_with_failed_recalculation_keeps_target(client):
    headers = onboarded_headers(client)
    before = active_target(client, headers)

    updated = update_profile(
        client, headers, sex="female", year_of_birth=1930, height_cm=100, activity_level="sedentary"
    )

    assert updated["height_cm"] in (100, "100", "100.00")
    assert updated["target_update"]["status"] == "failed"
    assert updated["target_update"]["calories_target_kcal"] == before["calories_target_kcal"]
    assert "1200" in updated["target_update"]["message"]
    assert active_target(client, headers)["id"] == before["id"]


# Sans objectif (onboarding incomplet), la mesure est enregistrée sans erreur.
def test_measurement_without_goal_still_created(client):
    headers = auth_headers(register_and_login(client))
    created = add_measurement(client, headers, date.today(), 75)
    assert created["target_update"] is None
    assert client.get(TARGET_URL, headers=headers).status_code == 404
