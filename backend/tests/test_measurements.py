from datetime import date, timedelta

"""
Tests pour la création, la récupération, la mise à jour et la suppression de mesures de poids avec et sans authentification.

Ces tests couvrent les scénarios suivants :
- Création, récupération, suppression ou mise à jour réussie d'une mesure avec authentification
- Échec de la création, de la récupération, de la suppression ou de la mise à jour d'une mesure sans authentification
- Échec de la récupération, de la mise à jour ou de la suppression d'une mesure inexistante
- Échec de la création ou de la mise à jour d'une mesure avec des champs manquants ou un poids invalide
"""

# Fonction utilitaire pour enregistrer un utilisateur et obtenir un jeton d'accès
def register_and_login(client):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    access_token = login_response.json()["access_token"]
    return access_token


"""Tests pour la création de nouvelles mesures de poids. """


# Test pour vérifier que la création d'une mesure avec authentification réussit
def test_new_measurement_success(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": 75},
        headers={"Authorization": f"Bearer {access_token}"}
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
        json={"date": str(date.today()),"weight_kg": 75}
    )
    assert response.status_code == 401


# Test pour vérifier que la création d'une mesure échoue lorsque des champs sont manquants ou invalides
def test_new_measurement_missing_fields(client):
    access_token = register_and_login(client)
    response = client.post(
        "/measurements",
        json={"date": str(date.today())},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


def test_new_measurement_invalid_fields(client):
    access_token = register_and_login(client)

    # Poids non numérique
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": "invalid-weight"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422
    
    # Poids trop grand
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": 1000},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Poids trop petit
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": 25},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Date invalide
    response = client.post(
        "/measurements",
        json={"date": "invalid-date","weight_kg": 75},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Date trop ancienne
    response = client.post(
        "/measurements",
        json={"date": "2019-12-31","weight_kg": 75},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Date future
    response = client.post(
        "/measurements",
        json={"date": str(date.today() + timedelta(days=1)), "weight_kg": 75},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


"""
Tests pour la récupération de la liste des mesures de poids par utilisateur.
"""
    
def create_measurement(client, access_token, date, weight_kg):
    response = client.post(
        "/measurements",
        json={"date": str(date),"weight_kg": weight_kg},
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



# Test pour vérifier la récupération des mesures filtrées par date
def test_list_measurements_by_date(client):
    access_token = register_and_login(client)

    # Crée plusieurs échantillons pour tester le filtrage par date
    create_measurement(client, access_token, date(2024, 6, 1), 75)
    create_measurement(client, access_token, date(2024, 8, 14), 80)
    create_measurement(client, access_token, date(2024, 9, 2), 85)

    response = client.get(
        "/measurements?start_date=2024-06-01&end_date=2024-08-16",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    measurements = response.json()

    # Vérifie que la mesure retournée correspond à la date filtrée
    assert len(measurements) == 2
    assert measurements[0]["weight_kg"] == 75
    assert measurements[0]["date"] == "2024-06-01"
    assert measurements[1]["date"] == "2024-08-14"


"""
Tests pour la récupérations d'une mesure à partir de son identifiant.
"""

def test_get_measurement_success(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    response = client.get(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    measurement = response.json()

    # Vérifie que les données de la mesure sont correctes
    assert measurement["id"] == measurement_id
    assert measurement["weight_kg"] == 75
    assert measurement["date"] == "2024-06-01"


# Test pour vérifier la récupération d'une mesure qui n'existe pas
def test_get_measurement_not_found(client):
    access_token = register_and_login(client)

    response = client.get(
        "/measurements/9999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


# Test pour vérifier l'accès non autorisé à une mesure existante
def test_get_measurement_unauthorized(client):
    response = client.get("/measurements/1")
    assert response.status_code == 401


# Test pour vérifier que l'utilisateur ne peut pas accéder à la mesure d'un autre utilisateur
def test_get_measurement_for_another_user(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Simule un autre utilisateur en s'enregistrant et en se connectant
    client.post(
        "/auth/register",
        json={"email": "another@example.com", "password": "anotherpassword"}
    )
    second_login = client.post(
        "/auth/login",
        data={"username": "another@example.com","password": "anotherpassword"},
    )
    second_token = second_login.json()["access_token"]

    # Tente de récupérer la mesure de l'utilisateur précédent avec le nouvel utilisateur
    response = client.get(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert response.status_code == 404


"""
Tests pour la suppression d'une mesure.
"""

# Tests pour la suppression d'une mesure existante
def test_delete_measurement_success(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Supprime la mesure
    response = client.delete(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    # Vérifie que la mesure a été supprimée
    response = client.get(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


# Tests pour la suppression d'une mesure qui n'existe pas
def test_delete_measurement_not_found(client):
    access_token = register_and_login(client)

    response = client.delete(
        "/measurements/9999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404


# Tests pour la suppression d'une mesure sans authentification
def test_delete_measurement_unauthorized(client):
    response = client.delete("/measurements/1")
    # Vérifie que la suppression sans authentification renvoie une erreur 401
    assert response.status_code == 401


# Tests pour la suppression d'une mesure appartenant à un autre utilisateur
def test_delete_measurement_for_another_user(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Simule un autre utilisateur en s'enregistrant et en se connectant
    client.post(
        "/auth/register",
        json={"email": "another@example.com","password": "anotherpassword"},
    )
    second_login = client.post(
        "/auth/login",
        data={"username": "another@example.com","password": "anotherpassword"},
    )
    second_token = second_login.json()["access_token"]

    # Tente de supprimer la mesure de l'utilisateur précédent avec le nouvel utilisateur
    response = client.delete(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert response.status_code == 404

"""
Tests pour la mise à jour d'une mesure.
"""

# Test pour la mise à jour d'une mesure existante
def test_update_measurement_success(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Met à jour le poids de la mesure
    response = client.patch(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"weight_kg": 76}
    )
    assert response.status_code == 200

    updated_measurement = response.json()
    assert updated_measurement["weight_kg"] == 76
    assert updated_measurement["date"] == "2024-06-01"

    # Met à jour la date de la mesure
    response = client.patch(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"date": "2024-06-02"}
    )
    assert response.status_code == 200
    
    updated_measurement = response.json()
    assert updated_measurement["date"] == "2024-06-02"
    assert updated_measurement["weight_kg"] == 76


# Test pour la mise à jour d'une mesure sans authentification
def test_update_measurement_unauthorized(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"weight_kg": 76}
    )
    assert response.status_code == 401


# Test pour la mise à jour d'une mesure inexistante
def test_update_measurement_not_found(client):
    access_token = register_and_login(client)

    response = client.patch(
        f"/measurements/9999",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"weight_kg": 76}
    )
    assert response.status_code == 404


# Test pour la mise à jour d'une mesure avec un champ invalide
def test_update_measurement_invalid_fields(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Poids non numérique
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"weight_kg": "invalid-weight"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Poids trop grand
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"weight_kg": 1000},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Poids trop petit
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"weight_kg": 25},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Date invalide
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"date": "invalid-date"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422 

    # Date trop ancienne
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"date": "2019-12-31"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Date future
    response = client.patch(
        f"/measurements/{measurement_id}",
        json={"date": str(date.today() + timedelta(days=1))},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422


# Test pour la mise à jour d'une mesure avec des champs manquants
def test_update_measurement_missing_fields(client):
    access_token = register_and_login(client)

    response = create_measurement(client, access_token, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    response = client.patch(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={}
    )
    assert response.status_code == 422


def test_update_measurement_for_another_user(client):
    access_token_user = register_and_login(client)

    response = create_measurement(client, access_token_user, date(2024, 6, 1), 75)
    assert response.status_code == 201

    measurement_id = response.json()["id"]

    # Simule un autre utilisateur en s'enregistrant et en se connectant
    client.post(
        "/auth/register",
        json={"email": "another@example.com","password": "anotherpassword"},
    )
    second_login = client.post(
        "/auth/login",
        data={"username": "another@example.com","password": "anotherpassword"},
    )
    second_token = second_login.json()["access_token"]

    # Tente de mettre à jour la mesure de l'utilisateur 1 avec le token de l'utilisateur 2
    response = client.patch(
        f"/measurements/{measurement_id}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"weight_kg": 80}
    )
    assert response.status_code == 404

 