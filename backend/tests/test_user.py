from fastapi.testclient import TestClient

"""
Tests pour l'enregistrement d'un utilisateur. Ces tests vérifient que le processus d'enregistrement fonctionne correctement pour différents scénarios,
tels que l'enregistrement réussi et l'enregistrement avec un email déjà existant.
Les tests utilisent un client de test FastAPI pour effectuer des requêtes HTTP vers l'application.
"""

# Test de l'enregistrement d'un nouvel utilisateur
def test_register_user_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 201

    body = response.json()

    # Vérification que la réponse contient les informations attendues
    assert "id" in body
    assert body["email"] == "test@example.com"
    assert body["is_active"] is True
    assert "pwd_hash" not in body  # Le mot de passe haché ne doit pas être exposé dans la réponse


# Test de l'enregistrement d'un utilisateur avec un email déjà existant
def test_register_user_existing_email(client: TestClient):

    payload = {"email": "test@example.com", "password": "testpassword"}

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    # Vérification que la première requête réussit et que la seconde échoue avec le code d'erreur attendu
    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Les informations entrées sont invalides."}


"""
Tests pour la connexion d'un utilisateur. Ces tests vérifient que l'authentification fonctionne correctement pour différents scénarios, 
tels que la connexion réussie, la connexion avec un mot de passe incorrect et la connexion avec un email inconnu. 
Les tests utilisent un utilisateur enregistré pour valider le processus de connexion.
"""

# Test de la connexion d'un utilisateur avec des informations correctes
def test_login_success(client: TestClient, registered_user):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )

    # Vérification que la réponse contient un token d'accès et le type de token attendu
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Test de la connexion d'un utilisateur avec un mot de passe incorrect
def test_login_wrong_password(client: TestClient, registered_user):
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )

    # Vérification que la réponse contient un message d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "Les informations entrées sont invalides."}


# Test de la connexion d'un utilisateur avec un email inconnu
def test_login_unknown_email(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "unknown@example.com", "password": "testpassword"}
    )

    # Vérification que la réponse contient un message d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "Les informations entrées sont invalides."}



"""
Tests pour la récupération des informations de l'utilisateur connecté. Ces tests vérifient que l'utilisateur peut obtenir ses informations correctement lorsqu'il est authentifié, 
et que les tentatives non autorisées ou avec un jeton invalide échouent comme prévu.
"""

def test_get_user(client, registered_user):
    # Connexion de l'utilisateur enregistré pour obtenir un jeton d'accès
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Récupération des informations de l'utilisateur connecté
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    user_data = response.json()


    assert user_data["email"] == "test@example.com"
    assert user_data["id"] == registered_user["id"]
    assert user_data["is_active"] is True
    assert "pwd_hash" not in user_data  # Le mot de passe haché ne doit pas être exposé dans la réponse

def test_get_user_unauthorized(client):
    # Tentative de récupération des informations de l'utilisateur sans jeton d'accès
    response = client.get("/auth/me")

    assert response.status_code == 401

def test_get_user_invalid_token(client):
    # Tentative de récupération des informations de l'utilisateur avec un jeton invalide
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer jeton invalide"},
    )

    assert response.status_code == 401
