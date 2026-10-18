import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from betterself.core.database import Base, create_db_engine
from betterself.users.models import User


@pytest.fixture
def db_session():
    # Crée un moteur de base de données pour les tests
    engine = create_db_engine("sqlite:///./test.db")

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)


# Teste la création d'un utilisateur
def test_create_user(db_session):
    # Crée un nouvel utilisateur
    user = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    # Ajoute l'utilisateur à la session et commit les changements
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Vérifie que l'utilisateur a été créé avec succès
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.pwd_hash == "securepassword"
    assert user.is_active is True


# Teste le id de l'utilisateur pour s'assurer qu'il est de type UUID
def test_user_id_is_uuid(db_session):
    # Crée un nouvel utilisateur
    user = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    # Ajoute l'utilisateur à la session et commit les changements
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.id, uuid.UUID)


# Teste la contrainte d'unicité sur l'email de l'utilisateur
def test_unique_email_constraint(db_session):
    # Crée un premier utilisateur avec un email spécifique
    user1 = User(
        email="test@example.com",
        pwd_hash="securepassword",
    )
    db_session.add(user1)
    db_session.commit()
    db_session.refresh(user1)

    # Crée un deuxième utilisateur avec le même email
    user2 = User(
        email="test@example.com",
        pwd_hash="anotherpassword",
    )
    db_session.add(user2)

    # Vérifie que l'insertion du deuxième utilisateur lève une erreur d'intégrité
    with pytest.raises(IntegrityError):
        db_session.commit()