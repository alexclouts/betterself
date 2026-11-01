import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from betterself.core.database import Base, create_db_engine, get_db
from betterself.main import app
from betterself.users.models import User 

TEST_DATABASE_URL = "sqlite://"

"""
Pendant les tests, nous utilisons une base de données SQLite en mémoire pour isoler les tests et éviter d'affecter la base de données réelle. 


Ces fixtures sont utilisées pour configurer l'environnement de test pour l'application FastAPI. 
Elles permettent de créer une base de données en mémoire, de gérer les sessions de base de données et 
de fournir un client de test pour effectuer des requêtes HTTP vers l'application.
"""

@pytest.fixture
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        )

    Base.metadata.create_all(bind=engine)

    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    # Crée une session de base de données pour les tests
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_session):
    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    # Remplace la dépendance de base de données de l'application par la session de test
    app.dependency_overrides[get_db] = override_get_db

    # Crée un client de test pour l'application FastAPI avec la session de test
    with TestClient(app) as test_client:
        yield test_client

    # Réinitialise les overrides des dépendances de l'application après chaque test
    app.dependency_overrides.clear()