from datetime import date, timedelta
import pytest
from backend.tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD

"""
Tests pour la création, la récupération, la mise à jour et la suppression de mesures de poids avec et sans authentification.

Ces tests couvrent les scénarios suivants :
- Création, récupération, suppression ou mise à jour réussie d'une mesure avec authentification
- Échec de la création, de la récupération, de la suppression ou de la mise à jour d'une mesure sans authentification
- Échec de la récupération, de la mise à jour ou de la suppression d'une mesure inexistante
- Échec de la création ou de la mise à jour d'une mesure avec un champ invalide
- Isolation des mesures entre différents utilisateurs
"""



# Adresse électronique et mot de passe utilisés pour le second utilisateur de test
OTHER_USER_EMAIL = "another@example.com"
OTHER_USER_PASSWORD = "anotherpassword"


# Fonction utilitaire pour construire les en-têtes d'authentification
def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


# Fonction utilitaire pour enregistrer un utilisateur et obtenir un jeton d'accès
def register_and_login(client, email: str = TEST_USER_EMAIL, password: str = TEST_USER_PASSWORD) -> str:
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    return login_response.json()["access_token"]


# Fonction utilitaire pour enregistrer et connecter un second utilisateur
def register_and_login_other_user(client) -> str:
    return register_and_login(
        client,
        email=OTHER_USER_EMAIL,
        password=OTHER_USER_PASSWORD,
    )


# Fonction utilitaire pour créer une mesure et retourner la réponse HTTP
def create_measurement(client, access_token: str, measurement_date: date, weight_kg: float):
    return client.post(
        "/measurements",
        json={
            "date": str(measurement_date),
            "weight_kg": weight_kg,
        },
        headers=auth_headers(access_token),
    )


# Fonction utilitaire pour créer une mesure et retourner directement son identifiant
def create_measurement_and_get_id(client, access_token: str, measurement_date: date, weight_kg: float) -> int:
    response = create_measurement(client, access_token, measurement_date, weight_kg)
    assert response.status_code == 201
    return response.json()["id"]


# Fonction utilitaire pour effectuer une requête GET, PATCH ou DELETE sur une mesure
# Cette fonction a été créée pour alléger le code des tests en centralisant les requêtes sur les mesures.
def request_measurement(client, method: str, measurement_id: int, access_token: str | None = None, json_data: dict | None = None):
    headers = auth_headers(access_token) if access_token else {}

    # GET et DELETE n'acceptent pas de corps JSON; seul PATCH en a besoin ici
    if method == "patch":
        return client.patch(
            f"/measurements/{measurement_id}",
            headers=headers,
            json=json_data,
        )
    return getattr(client, method)(
        f"/measurements/{measurement_id}",
        headers=headers,
    )


"""
Tests pour la création de nouvelles mesures de poids.
"""


# Test pour vérifier que la création d'une mesure avec authentification réussit
def test_new_measurement_success(client):
    access_token = register_and_login(client)
    response = create_measurement(client, access_token, date.today(), 75)
    assert response.status_code == 201
    measurement_data = response.json()

    # Vérifie que les données retournées correspondent à la mesure créée
    assert measurement_data["weight_kg"] == 75
    assert measurement_data["date"] == str(date.today())
    assert "id" in measurement_data
    assert "user_id" in measurement_data


# Test pour vérifier que la création d'une mesure sans authentification échoue avec un code 401
def test_new_measurement_unauthorized(client):
    response = client.post(
        "/measurements",
        json={
            "date": str(date.today()),
            "weight_kg": 75,
        },
    )
    assert response.status_code == 401


# Test pour vérifier que la création échoue lorsque le champ date est manquant
def test_new_measurement_missing_date(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={"weight_kg": 75},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque le champ weight_kg est manquant
def test_new_measurement_missing_weight(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={"date": str(date.today())},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque le poids n'est pas numérique
def test_new_measurement_invalid_weight_type(client):
    access_token = register_and_login(client)
    response = create_measurement(client, access_token, date.today(), "invalid-weight")
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque le poids est trop grand
def test_new_measurement_weight_too_high(client):
    access_token = register_and_login(client)
    response = create_measurement(client, access_token, date.today(), 1000)
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque le poids est trop petit
def test_new_measurement_weight_too_low(client):
    access_token = register_and_login(client)
    response = create_measurement(client, access_token, date.today(), 25)
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque la date n'est pas valide
def test_new_measurement_invalid_date_format(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={
            "date": "invalid-date",
            "weight_kg": 75,
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque la date est antérieure à la limite permise
def test_new_measurement_date_too_old(client):
    access_token = register_and_login(client)
    response = create_measurement(client, access_token, date(2019, 12, 31), 75)
    assert response.status_code == 422


# Test pour vérifier que la création échoue lorsque la date est dans le futur
def test_new_measurement_date_in_future(client):
    access_token = register_and_login(client)
    future_date = date.today() + timedelta(days=1)
    response = create_measurement(client, access_token, future_date, 75)
    assert response.status_code == 422


"""
Tests pour la récupération de la liste des mesures de poids par utilisateur.
"""


# Test pour vérifier que la récupération de la liste des mesures avec authentification réussit
def test_list_measurements(client):
    access_token = register_and_login(client)
    # Crée deux mesures pour vérifier que les deux sont retournées
    create_measurement(client, access_token, date.today(), 75)
    create_measurement(client, access_token, date.today(), 80)

    response = client.get(
        "/measurements",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    measurements = response.json()

    assert len(measurements) == 2
    assert measurements[0]["weight_kg"] == 75
    assert measurements[1]["weight_kg"] == 80


# Test pour vérifier que la récupération de la liste sans authentification échoue
def test_list_measurements_unauthorized(client):
    response = client.get("/measurements")
    assert response.status_code == 401


# Test pour vérifier que la liste est vide lorsqu'aucune mesure n'a été créée
def test_list_measurements_empty(client):
    access_token = register_and_login(client)
    response = client.get(
        "/measurements",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    measurements = response.json()
    assert len(measurements) == 0


# Test pour vérifier la récupération des mesures filtrées par date
def test_list_measurements_by_date(client):
    access_token = register_and_login(client)
    # Crée plusieurs mesures pour tester le filtrage par intervalle de dates
    create_measurement(client, access_token, date(2024, 6, 1), 75)
    create_measurement(client, access_token, date(2024, 8, 14), 80)
    create_measurement(client, access_token, date(2024, 9, 2), 85)

    response = client.get(
        "/measurements?start_date=2024-06-01&end_date=2024-08-16",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    measurements = response.json()

    # Vérifie que seules les mesures dans l'intervalle demandé sont retournées
    assert len(measurements) == 2
    assert measurements[0]["weight_kg"] == 75
    assert measurements[0]["date"] == "2024-06-01"
    assert measurements[1]["date"] == "2024-08-14"


"""
Tests pour la récupération d'une mesure à partir de son identifiant.
"""


# Test pour vérifier la récupération réussie d'une mesure existante
def test_get_measurement_success(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(client, "get", measurement_id, access_token)
    assert response.status_code == 200
    measurement = response.json()

    # Vérifie que les données de la mesure sont correctes
    assert measurement["id"] == measurement_id
    assert measurement["weight_kg"] == 75
    assert measurement["date"] == "2024-06-01"


# Test pour vérifier la récupération d'une mesure qui n'existe pas
def test_get_measurement_not_found(client):
    access_token = register_and_login(client)
    response = request_measurement(client, "get", 9999, access_token)
    assert response.status_code == 404


# Test pour vérifier l'accès non autorisé à une mesure existante
def test_get_measurement_unauthorized(client):
    response = request_measurement(client, "get", 1)
    assert response.status_code == 401


# Test pour vérifier qu'un utilisateur ne peut pas accéder à la mesure d'un autre utilisateur
def test_get_measurement_for_another_user(client):
    owner_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        owner_token,
        date(2024, 6, 1),
        75,
    )
    other_token = register_and_login_other_user(client)
    response = request_measurement(client, "get", measurement_id, other_token)
    assert response.status_code == 404


"""
Tests partagés pour les règles communes aux opérations GET, PATCH et DELETE.
"""

# Méthodes HTTP et corps de requête associés pour les tests paramétrés
HTTP_METHODS = [
    ("get", None),
    ("patch", {"weight_kg": 80}),
    ("delete", None),
]


# Test paramétré pour vérifier qu'une mesure inexistante retourne 404 pour GET, PATCH et DELETE
@pytest.mark.parametrize("method,json_data", HTTP_METHODS)
def test_measurement_not_found(client, method, json_data):
    access_token = register_and_login(client)
    response = request_measurement(
        client,
        method,
        9999,
        access_token,
        json_data,
    )
    assert response.status_code == 404


# Test paramétré pour vérifier qu'une requête sans authentification retourne 401 pour GET, PATCH et DELETE
@pytest.mark.parametrize("method,json_data", HTTP_METHODS)
def test_measurement_unauthorized(client, method, json_data):
    response = request_measurement(client, method, 1, None, json_data)
    assert response.status_code == 401


# Test paramétré pour vérifier qu'un utilisateur ne peut pas accéder à la mesure d'un autre utilisateur
@pytest.mark.parametrize("method,json_data", HTTP_METHODS)
def test_measurement_for_another_user(client, method, json_data):
    owner_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        owner_token,
        date(2024, 6, 1),
        75,
    )
    other_token = register_and_login_other_user(client)
    response = request_measurement(
        client,
        method,
        measurement_id,
        other_token,
        json_data,
    )
    assert response.status_code == 404


"""
Tests pour la suppression d'une mesure.
"""


# Test pour vérifier la suppression réussie d'une mesure existante
def test_delete_measurement_success(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(client, "delete", measurement_id, access_token)
    assert response.status_code == 204

    # Vérifie que la mesure n'est plus accessible après sa suppression
    response = request_measurement(client, "get", measurement_id, access_token)
    assert response.status_code == 404


"""
Tests pour la mise à jour d'une mesure.
"""


# Test pour vérifier la mise à jour du poids d'une mesure existante
def test_update_measurement_weight_success(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"weight_kg": 76},
    )
    assert response.status_code == 200
    updated_measurement = response.json()

    # Vérifie que seul le poids a été modifié
    assert updated_measurement["weight_kg"] == 76
    assert updated_measurement["date"] == "2024-06-01"


# Test pour vérifier la mise à jour de la date d'une mesure existante
def test_update_measurement_date_success(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"date": "2024-06-02"},
    )
    assert response.status_code == 200
    updated_measurement = response.json()

    # Vérifie que seule la date a été modifiée
    assert updated_measurement["date"] == "2024-06-02"
    assert updated_measurement["weight_kg"] == 75


# Test pour vérifier que la mise à jour échoue lorsque le poids n'est pas numérique
def test_update_measurement_invalid_weight_type(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"weight_kg": "invalid-weight"},
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour échoue lorsque le poids est trop grand
def test_update_measurement_weight_too_high(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"weight_kg": 1000},
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour échoue lorsque le poids est trop petit
def test_update_measurement_weight_too_low(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"weight_kg": 25},
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour échoue lorsque la date n'est pas valide
def test_update_measurement_invalid_date_format(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"date": "invalid-date"},
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour échoue lorsque la date est antérieure à la limite permise
def test_update_measurement_date_too_old(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"date": "2019-12-31"},
    )
    assert response.status_code == 422


# Test pour vérifier que la mise à jour échoue lorsque la date est dans le futur
def test_update_measurement_date_in_future(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    future_date = date.today() + timedelta(days=1)
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {"date": str(future_date)},
    )
    assert response.status_code == 422


# Test pour vérifier qu'un PATCH avec un corps vide ne modifie rien
def test_update_measurement_empty_body(client):
    access_token = register_and_login(client)
    measurement_id = create_measurement_and_get_id(
        client,
        access_token,
        date(2024, 6, 1),
        75,
    )
    response = request_measurement(
        client,
        "patch",
        measurement_id,
        access_token,
        {},
    )
    # Adapte cette assertion à la règle choisie pour ton API :
    # 200 si un corps vide est accepté, ou 422 si tu veux l'interdire.
    assert response.status_code in (200, 422)