"""
Resources pour les tests, y compris les utilisateurs de test et les fonctions utilitaires pour l'authentification.
"""
import re

import pytest
from sqlalchemy import select

from betterself.core.email import get_email_sender
from betterself.models.user_models import User

# Adresse électronique et mot de passe utilisés pour le premier utilisateur de test
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"

# Adresse électronique et mot de passe utilisés pour le second utilisateur de test
OTHER_USER_EMAIL = "another@example.com"
OTHER_USER_PASSWORD = "anotherpassword"


# Utilisateur inscrit dont l'adresse courriel est confirmée
@pytest.fixture
def registered_user(client, test_session):
    register_and_verify(client, TEST_USER_EMAIL, TEST_USER_PASSWORD)

    user = test_session.scalar(select(User).where(User.email == TEST_USER_EMAIL))
    return {"id": str(user.id), "email": user.email, "is_active": user.is_active}


# Retourne le jeton du dernier lien de vérification envoyé à l'adresse.
# Les courriels sont lus dans le faux expéditeur installé par le client de test (conftest.py).
def last_verification_token(client, email: str) -> str:
    sender = client.app.dependency_overrides[get_email_sender]()
    for message in reversed(sender.sent):
        match = re.search(r"verify-email\?token=([\w-]+)", message["body"])
        if message["to"] == email and match:
            return match.group(1)
    raise AssertionError(f"Aucun lien de vérification envoyé à {email}")


# Inscrit un utilisateur et confirme son adresse en suivant le lien reçu par courriel.
def register_and_verify(client, email: str, password: str) -> None:
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 202

    token = last_verification_token(client, email)
    response = client.post("/auth/verify-email", json={"token": token})
    assert response.status_code == 200


# Fonction utilitaire pour construire les en-têtes d'authentification
def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


# Fonction utilitaire pour enregistrer un utilisateur et obtenir un jeton d'accès
def register_and_login(client, email: str = TEST_USER_EMAIL, password: str = TEST_USER_PASSWORD) -> str:
    register_and_verify(client, email, password)
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
