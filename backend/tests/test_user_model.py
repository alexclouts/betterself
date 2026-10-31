import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from betterself.core.database import Base, create_db_engine
from betterself.users.models import User



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