from datetime import date

"""
Tests pour la création de nouvelles mesures de poids avec et sans authentification.
Ces tests couvrent les scénarios suivants :
- Création réussie d'une mesure avec authentification
- Échec de la création d'une mesure sans authentification
- Échec de la création d'une mesure avec des champs manquants
- Échec de la création d'une mesure avec un poids invalide
"""

# Fonction utilitaire pour enregistrer un utilisateur et obtenir un jeton d'accès
def register_and_login(client):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    access_token = login_response.json()["access_token"]
    return access_token


# Test pour vérifier que la création d'une mesure avec authentification réussit
def test_new_measurement_success(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={
            "date": str(date.today()),
            "weight_kg": 75,
            },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201

    measurement_data = response.json()

    assert measurement_data["weight_kg"] == 75
    assert measurement_data["date"] == str(date.today())
    assert "id" in measurement_data  # Vérifie que l'ID de la mesure est présent dans la réponse
    assert "user_id" in measurement_data  # Vérifie que l'ID de l'utilisateur est présent dans la réponse


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


# Test pour vérifier que la création d'une mesure échoue lorsque des champs sont manquants ou invalides
def test_new_measurement_missing_fields(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={
            "date": str(date.today()),
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422  # Vérifie que la requête échoue avec un code 422 pour les champs manquants


def test_new_measurement_invalid_weight(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={
            "date": str(date.today()),
            "weight_kg": -5,  # Poids invalide
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422  # Vérifie que la requête échoue avec un code 422 pour un poids invalide



"""
Tests pour la récupération de la liste des mesures de poids avec authentification.
Ces tests couvrent les scénarios suivants :
- Récupération réussie de la liste des mesures avec authentification
- Échec de la récupération de la liste des mesures sans authentification
"""
    
def create_measurement(client, access_token, date, weight_kg):
    response = client.post(
        "/measurements",
        json={
            "date": str(date),
            "weight_kg": weight_kg,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return response


# Test pour vérifier que la récupération de la liste des mesures avec authentification réussie
def test_list_measurements(client):
    access_token = register_and_login(client)
    create_measurement(client, access_token, date.today(), 75)
    create_measurement(client, access_token, date.today(), 80)

    response = client.get(
        "/measurements",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    
    measurements = response.json()
    
    assert len(measurements) == 2
    assert measurements[0]["weight_kg"] == 75
    assert measurements[1]["weight_kg"] == 80


# Tests pour la récupération non autorisée de la liste des mesures
def test_list_measurements_unauthorized(client):
    response = client.get("/measurements")
    assert response.status_code == 401


# Test pour vérifier que la récupération de la liste des mesures renvoie une liste vide lorsque l'utilisateur n'a pas encore créé de mesures
def test_list_measurements_empty(client):
    access_token = register_and_login(client)

    response = client.get(
        "/measurements",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    measurements = response.json()
    assert len(measurements) == 0

