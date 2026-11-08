import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from betterself.core.database import Base, create_db_engine
from betterself.models.user_models import User
from tests.api_helpers import USERS_URL, AUTH_URL
from tests.utils import registered_user



# Teste la création d'un utilisateur
def test_create_user(test_session):
    # Crée un nouvel utilisateur
    user = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    # Ajoute l'utilisateur à la session et commit les changements
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    # Vérifie que l'utilisateur a été créé avec succès
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.pwd_hash == "securepassword"
    assert user.is_active is True


# Teste le id de l'utilisateur pour s'assurer qu'il est de type UUID
def test_user_id_is_uuid(test_session):
    # Crée un nouvel utilisateur
    user = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    # Ajoute l'utilisateur à la session et commit les changements
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)


# Teste la contrainte d'unicité sur l'email de l'utilisateur
def test_unique_email_constraint(test_session):
    # Crée un premier utilisateur avec un email spécifique
    user1 = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    test_session.add(user1)
    test_session.commit()
    test_session.refresh(user1)

    # Crée un deuxième utilisateur avec le même email
    user2 = User(
        email="test@example.com",
        pwd_hash="anotherpassword",
    )
    test_session.add(user2)

    # Vérifie que l'insertion du deuxième utilisateur lève une erreur d'intégrité
    with pytest.raises(IntegrityError):
        test_session.commit()


"""
Tests pour la récupération des informations de l'utilisateur connecté. Ces tests vérifient que l'utilisateur peut obtenir ses informations correctement lorsqu'il est authentifié, 
et que les tentatives non autorisées ou avec un jeton invalide échouent comme prévu.
"""

def test_get_user(client, registered_user):
    # Connexion de l'utilisateur enregistré pour obtenir un jeton d'accès
    login_response = client.post(
        f"{AUTH_URL}/login",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Récupération des informations de l'utilisateur connecté
    response = client.get(
        f"{USERS_URL}/me",
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
    response = client.get(f"{USERS_URL}/me")
    assert response.status_code == 401


def test_get_user_invalid_token(client):
    # Tentative de récupération des informations de l'utilisateur avec un jeton invalide
    response = client.get(
        f"{USERS_URL}/me",
        headers={"Authorization": "Bearer jeton invalide"},
    )
    assert response.status_code == 401
