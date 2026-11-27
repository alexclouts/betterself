import os
import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from betterself.core.config import settings
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


# (code, nom, marque, portion, kcal, protéines, glucides, lipides, popularité)
PRODUCTS = [
    ("0000000000017", "Petit écolier chocolat au lait", "LU", 25, 498, 6, 66, 23, 900),
    ("0000000000024", "Lait", "Natrel", 250, 60, 3.2, 4.8, 3.25, 1),
    ("0000000000031", "Lait 2 %", "Québon", 250, 50, 3.3, 4.8, 2, 50),
    ("0000000000048", "Laitue romaine", None, None, 17, 1.2, 3.3, 0.3, 700),
    ("0000000000055", "Crème glacée", "Coaticook", 66, 207.123, 3.5, 24, 11, 10),
    ("0000000000062", "Boisson au lait", "Natrel", 250, 70, 3, 9, 2, 80),
    ("0000000000079", "Poudre portion trop petite", None, 0.5, 350, 10, 70, 3, 0),
    ("0000000000086", "Poudre portion trop grande", None, 2500, 350, 10, 70, 3, 0),
    ("0000000000093", "Poudre portion limite", None, 1000, 350, 10, 70, 3, 0),
    ("0055653170259", "Biscuits à l'érable", "Dare", 20, 470.588, 5, 70, 19, 5),
]

# Unités tirées de `serving_size` : code → (unité, pluriel, poids, poids estimé).
PRODUCT_UNITS = {
    "0000000000017": ("biscuit", "biscuits", 12.5, 0),  # « 2 cookies (25 g) »
    "0000000000024": ("tasse", "tasses", 250, 1),        # « 1 cup (250 ml) »
    "0000000000031": (None, None, None, 1),              # « 250 ml »
}


# Construit un petit catalogue ayant le même schéma que build_catalog.py.
# Le dossier contient une espace, comme le disque externe.
@pytest.fixture
def catalog_path(tmp_path):
    folder = tmp_path / "USB Externe"
    folder.mkdir()
    path = folder / "off.sqlite"

    db = sqlite3.connect(path)
    db.executescript("""
    CREATE TABLE products (
      code TEXT PRIMARY KEY, name TEXT NOT NULL, brands TEXT, categories_tags TEXT,
      serving_g REAL, unit_name TEXT, unit_name_plural TEXT, unit_g REAL,
      weight_is_estimated INTEGER NOT NULL DEFAULT 0,
      kcal_100g REAL, protein_100g REAL, carbs_100g REAL,
      fat_100g REAL, scans INTEGER, modified INTEGER);
    CREATE VIRTUAL TABLE products_fts USING fts5(
      name, brands, content='products', tokenize='unicode61 remove_diacritics 2');
    """)
    db.executemany(
        "INSERT INTO products (code, name, brands, serving_g, kcal_100g, protein_100g, "
        "carbs_100g, fat_100g, scans, unit_name, unit_name_plural, unit_g, weight_is_estimated) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(*product, *PRODUCT_UNITS.get(product[0], (None, None, None, 0))) for product in PRODUCTS],
    )
    db.execute("INSERT INTO products_fts(products_fts) VALUES ('rebuild')")
    db.commit()
    db.close()
    return path


# Configure l'application pour utiliser le catalogue de test.
@pytest.fixture
def configured_catalog(monkeypatch, catalog_path):
    monkeypatch.setattr(settings, "off_catalog_path", str(catalog_path))
    return catalog_path
