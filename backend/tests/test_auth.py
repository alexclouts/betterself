from fastapi.testclient import TestClient
from tests.utils import registered_user
from tests.api_helpers import AUTH_URL
"""
Tests pour l'enregistrement d'un utilisateur. Ces tests vérifient que le processus d'enregistrement fonctionne correctement pour différents scénarios,
tels que l'enregistrement réussi et l'enregistrement avec un email déjà existant.
Les tests utilisent un client de test FastAPI pour effectuer des requêtes HTTP vers l'application.
"""

# Test de l'enregistrement d'un nouvel utilisateur
def test_register_user_success(client: TestClient):
    response = client.post(
        f"{AUTH_URL}/register",
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

    first_response = client.post(f"{AUTH_URL}/register", json=payload)
    second_response = client.post(f"{AUTH_URL}/register", json=payload)

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
        f"{AUTH_URL}/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )

    # Vérification que la réponse contient un token d'accès et le type de token attendu
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Test de la connexion d'un utilisateur avec un mot de passe incorrect
def test_login_wrong_password(client: TestClient, registered_user):
    response = client.post(
        f"{AUTH_URL}/login",
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
