import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from betterself.core.database import Base, create_db_engine, get_db
from betterself.main import app
from betterself.users.models import User 

TEST_DATABASE_URL = "sqlite:///./test.db"


"""
Pendant les tests, nous utilisons une base de données SQLite en mémoire pour isoler les tests et éviter d'affecter la base de données réelle. 


Ces fixtures sont utilisées pour configurer l'environnement de test pour l'application FastAPI. 
Elles permettent de créer une base de données en mémoire, de gérer les sessions de base de données et 
de fournir un client de test pour effectuer des requêtes HTTP vers l'application.
"""

@pytest.fixture
def test_engine():
    engine = create_db_engine(TEST_DATABASE_URL)

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_session: Session):
    def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()



"""
Ici, nous définissons une fixture `registered_user` qui enregistre un utilisateur de test avant chaque test qui en a besoin.
"""

TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword"


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