"""
Resources pour les tests, y compris les utilisateurs de test et les fonctions utilitaires pour l'authentification.
"""
import pytest

# Adresse électronique et mot de passe utilisés pour le premier utilisateur de test
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"

# Adresse électronique et mot de passe utilisés pour le second utilisateur de test
OTHER_USER_EMAIL = "another@example.com"
OTHER_USER_PASSWORD = "anotherpassword"


@pytest.fixture
def registered_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 201

    return response.json()


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
