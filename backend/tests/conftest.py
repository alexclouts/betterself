import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from betterself.core.database import Base, create_db_engine, get_db
from betterself.main import app
from betterself.models.user_models import User

"""
Pendant les tests, nous utilisons une base de données PostgreSQL dédiée (betterself_test),
distincte de la base de développement. Tester sur le même moteur qu'en production évite
les différences de comportement (types, longueurs, contraintes) qu'on aurait avec SQLite.

Isolation : le schéma est créé une seule fois pour toute la session de tests. Chaque test
s'exécute ensuite dans une transaction annulée à la fin du test, ce qui le rend rapide et
garantit qu'aucune donnée ne fuit d'un test à l'autre. Les commit() effectués pendant un
test (par le code ou par le test lui-même) deviennent des SAVEPOINT à l'intérieur de cette
transaction, grâce à join_transaction_mode="create_savepoint".

Ces fixtures fournissent aussi un client de test pour effectuer des requêtes HTTP vers l'application.
"""

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://betterself:betterself@localhost:5432/betterself_test",
)


@pytest.fixture(scope="session")
def test_engine():
    engine = create_db_engine(TEST_DATABASE_URL)

    # Repart d'un schéma propre, même si une session précédente a été interrompue.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    db = Session(
        bind=connection,
        autoflush=True,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield db
    finally:
        db.close()
        # Annule tout ce que le test a écrit dans la base.
        transaction.rollback()
        connection.close()


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
