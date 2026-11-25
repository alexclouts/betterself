import pytest
from sqlalchemy import func, select

from betterself.core.config import settings
from betterself.models.food_models import Food
from tests.api_helpers import FOODS_URL
from tests.test_food_search import consume, create_food, import_product
from tests.utils import auth_headers, register_and_login, register_and_login_other_user

"""
Tests de la recherche d'un aliment par code-barres scanné (GET /foods/barcode/{code}).
"""

BARCODE_URL = f"{FOODS_URL}/barcode"

# Produits du catalogue de test (tests/conftest.py).
CATALOG_CODE = "0000000000024"  # Lait, Natrel
UPC_A_CODE = "055653170259"  # Biscuits à l'érable, enregistré en EAN-13 : 0055653170259
UNKNOWN_CODE = "4006381333931"


@pytest.fixture
def headers(client, configured_catalog):
    return auth_headers(register_and_login(client))


@pytest.fixture
def other_headers(client, configured_catalog):
    return auth_headers(register_and_login_other_user(client))


def find(client, headers, code):
    return client.get(f"{BARCODE_URL}/{code}", headers=headers)


def count_foods(test_session) -> int:
    return test_session.scalar(select(func.count()).select_from(Food))


def test_barcode_requires_authentication(client, configured_catalog):
    assert find(client, {}, CATALOG_CODE).status_code == 401


# Un produit du catalogue est retourné sans être importé.
def test_barcode_finds_catalog_product_without_importing(client, headers, test_session):
    before = count_foods(test_session)

    response = find(client, headers, CATALOG_CODE)

    assert response.status_code == 200
    result = response.json()
    assert result["food_id"] is None
    assert result["catalog_code"] == CATALOG_CODE
    assert result["source"] == "open_food_facts"
    assert result["name"] == "Lait"
    assert result["in_history"] is False
    assert count_foods(test_session) == before


# Un UPC-A (12 chiffres, produits nord-américains) est trouvé sous sa forme EAN-13.
def test_barcode_accepts_upc_a(client, headers):
    response = find(client, headers, UPC_A_CODE)

    assert response.status_code == 200
    assert response.json()["catalog_code"] == "0" + UPC_A_CODE


# Un produit déjà importé est retourné comme aliment de la base.
def test_barcode_finds_imported_food(client, headers):
    food = import_product(client, headers, CATALOG_CODE)

    result = find(client, headers, CATALOG_CODE).json()

    assert result["food_id"] == food["id"]
    assert result["catalog_code"] is None


# Un aliment créé avec un code-barres (produit absent du catalogue) est retrouvé au scan suivant.
def test_barcode_finds_manual_food(client, headers):
    food = create_food(client, headers, "Hummus maison", external_reference_id=UNKNOWN_CODE)

    result = find(client, headers, UNKNOWN_CODE).json()

    assert result["food_id"] == food["id"]
    assert result["source"] == "manual"
    assert result["in_history"] is True


# Un aliment créé avec un UPC-A (12 chiffres) est retrouvé quand le lecteur rapporte
# le même code sous sa forme EAN-13 (0 en tête).
def test_barcode_finds_upc_a_food_from_ean13_scan(client, headers):
    food = create_food(client, headers, "Crème à café", external_reference_id="041271025682")

    assert find(client, headers, "0041271025682").json()["food_id"] == food["id"]


# Si plusieurs aliments portent le code, celui de l'historique de l'utilisateur l'emporte.
def test_barcode_prefers_user_history(client, headers, other_headers):
    imported = import_product(client, other_headers, CATALOG_CODE)
    own = create_food(client, headers, "Mon lait", external_reference_id=CATALOG_CODE)

    assert find(client, headers, CATALOG_CODE).json()["food_id"] == own["id"]
    # L'autre utilisateur n'a pas cet aliment dans son historique : le produit importé l'emporte.
    assert find(client, other_headers, CATALOG_CODE).json()["food_id"] == imported["id"]

    # Après l'avoir consigné, le produit importé fait partie de l'historique de l'autre utilisateur.
    consume(client, other_headers, imported)
    assert find(client, other_headers, CATALOG_CODE).json()["food_id"] == imported["id"]


# Sans historique, le produit Open Food Facts importé passe avant l'aliment manuel d'un autre utilisateur.
def test_barcode_prefers_imported_product_over_other_users_manual_food(client, headers, other_headers):
    create_food(client, other_headers, "Lait d'un autre", external_reference_id=CATALOG_CODE)
    imported = import_product(client, other_headers, CATALOG_CODE)

    assert find(client, headers, CATALOG_CODE).json()["food_id"] == imported["id"]


def test_barcode_unknown(client, headers):
    response = find(client, headers, UNKNOWN_CODE)

    assert response.status_code == 404
    assert response.json()["detail"] == "Aucun aliment ne correspond à ce code-barres."


@pytest.mark.parametrize("code", ["1234567", "123456789012345", "12345abc", "0000-0000"])
def test_barcode_invalid_format(client, headers, code):
    assert find(client, headers, code).status_code == 422


# Sans catalogue, un code inconnu de la base répond 503 : le client peut proposer
# de créer l'aliment sans affirmer que le produit n'existe pas.
def test_barcode_without_catalog(client, headers, monkeypatch):
    food = create_food(client, headers, "Hummus maison", external_reference_id=UNKNOWN_CODE)
    monkeypatch.setattr(settings, "off_catalog_path", None)

    # Les aliments de la base restent disponibles.
    assert find(client, headers, UNKNOWN_CODE).json()["food_id"] == food["id"]

    response = find(client, headers, CATALOG_CODE)
    assert response.status_code == 503
