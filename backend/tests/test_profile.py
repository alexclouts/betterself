from datetime import date

from tests.utils import auth_headers, register_and_login, register_and_login_other_user


PROFILE_URL = "/users/me/profile"


# Données valides pour créer ou mettre à jour un profil utilisateur
def valid_user_profile_payload() -> dict:
    return {
        "first_name": "Alex",
        "year_of_birth": 1996,
        "sex": "male",
        "height_cm": 175,
        "activity_level": "moderately_active",
    }


# Test pour vérifier qu'aucun profil n'existe initialement
def test_get_user_profile_not_found(client):
    access_token = register_and_login(client)

    response = client.get(
        PROFILE_URL,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 404


# Test pour vérifier que la consultation échoue sans authentification
def test_get_user_profile_unauthorized(client):
    response = client.get(PROFILE_URL)
    assert response.status_code == 401


# Test pour vérifier la création initiale du profil
def test_create_user_profile_success(client):
    access_token = register_and_login(client)
    response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
        headers=auth_headers(access_token),
    )
    assert response.status_code == 201

    profile = response.json()
    assert profile["first_name"] == "Alex"
    assert profile["year_of_birth"] == 1996
    assert profile["sex"] == "male"
    assert profile["height_cm"] == "175"
    assert profile["activity_level"] == "moderately_active"
    assert profile["user_id"]


# Test pour vérifier que la création échoue sans authentification
def test_create_user_profile_unauthorized(client):
    response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier qu'un utilisateur ne peut avoir qu'un seul profil
def test_create_user_profile_only_once(client):
    access_token = register_and_login(client)

    first_response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
        headers=auth_headers(access_token),
    )
    assert first_response.status_code == 201

    second_response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
        headers=auth_headers(access_token),
    )
    # Le endpoint utilise PUT : un deuxième appel doit mettre à jour
    # le profil existant, pas créer un doublon.
    assert second_response.status_code == 200

    profile = second_response.json()
    assert profile["first_name"] == "Alex"


# Test pour vérifier la mise à jour complète du profil
def test_update_user_profile_success(client):
    access_token = register_and_login(client)
    creation_response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    update_payload = {
        "first_name": "Marie-Claire",
        "year_of_birth": 1990,
        "sex": "female",
        "height_cm": 168,
        "activity_level": "lightly_active",
    }
    response = client.put(
        PROFILE_URL,
        json=update_payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    profile = response.json()
    assert profile["first_name"] == "Marie-Claire"
    assert profile["year_of_birth"] == 1990
    assert profile["sex"] == "female"
    assert profile["height_cm"] == "168"
    assert profile["activity_level"] == "lightly_active"


# Test pour vérifier que la modification échoue sans authentification
def test_update_user_profile_unauthorized(client):
    response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier que le prénom accepte les accents et tirets
def test_user_profile_accepts_valid_first_names(client):
    access_token = register_and_login(client)

    valid_names = [
        "René",
        "Élodie",
        "Marie-Claire",
        "D'Angelo",
        "O'Brien",
        "Anne Marie",
    ]

    for first_name in valid_names:
        payload = valid_user_profile_payload()
        payload["first_name"] = first_name

        response = client.put(
            PROFILE_URL,
            json=payload,
            headers=auth_headers(access_token),
        )
        print("Response: ", response.json())
        assert response.status_code in (200, 201)
        assert response.json()["first_name"] == first_name


# Test pour vérifier que le prénom ne peut pas contenir de chiffres
def test_user_profile_rejects_first_name_with_digits(client):
    access_token = register_and_login(client)

    payload = valid_user_profile_payload()
    payload["first_name"] = "Alex123"

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que le prénom refuse les caractères spéciaux interdits
def test_user_profile_rejects_invalid_first_name_characters(client):
    access_token = register_and_login(client)

    invalid_names = [
        "Alex!",
        "Alex?",
        "Alex*",
        "Alex&",
        'Alex"',
        "Alex/",
        "Alex$",
        "Alex%",
        "Alex#",
        "Alex@",
    ]
    for first_name in invalid_names:
        payload = valid_user_profile_payload()
        payload["first_name"] = first_name

        response = client.put(
            PROFILE_URL,
            json=payload,
            headers=auth_headers(access_token),
        )
        assert response.status_code == 422


# Test pour vérifier que le prénom ne dépasse pas la limite de caractères
def test_user_profile_rejects_first_name_too_long(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["first_name"] = "A" * 101

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que le prénom facultatif peut être absent
def test_user_profile_accepts_missing_first_name(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload.pop("first_name")

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 201

    profile = response.json()
    assert profile["first_name"] is None


# Test pour vérifier que le sexe accepte uniquement M, F ou X
def test_user_profile_rejects_invalid_sex(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["sex"] = "Z"

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que l'année de naissance ne peut pas être future
def test_user_profile_rejects_future_birth_year(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["year_of_birth"] = date.today().year + 1

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que l'année de naissance ne peut pas être trop récente
def test_user_profile_rejects_recent_birth_year(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["year_of_birth"] = date.today().year - 5

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que l'année de naissance ne peut pas être trop ancienne
def test_user_profile_rejects_old_birth_year(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["year_of_birth"] = 1899

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que la taille respecte la limite minimale
def test_user_profile_rejects_height_too_small(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["height_cm"] = 99

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que la taille respecte la limite maximale
def test_user_profile_rejects_height_too_large(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["height_cm"] = 251

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que le niveau d'activité accepte uniquement les valeurs valides
def test_user_profile_rejects_invalid_activity_level(client):
    access_token = register_and_login(client)
    payload = valid_user_profile_payload()
    payload["activity_level"] = "extreme"

    response = client.put(
        PROFILE_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier l'isolation des profils entre utilisateurs
def test_user_profile_isolated_between_users(client):
    owner_token = register_and_login(client)
    creation_response = client.put(
        PROFILE_URL,
        json=valid_user_profile_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    other_token = register_and_login_other_user(client)
    response = client.get(
        PROFILE_URL,
        headers=auth_headers(other_token),
    )
    assert response.status_code == 404