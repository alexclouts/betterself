from decimal import Decimal

import pytest
from sqlalchemy import func, select

from betterself.core.config import settings
from betterself.models.food_models import Food
from tests.api_helpers import FOODS_URL
from tests.utils import auth_headers, register_and_login, register_and_login_other_user

SEARCH_URL = f"{FOODS_URL}/search"


@pytest.fixture
def headers(client, configured_catalog):
    return auth_headers(register_and_login(client))


@pytest.fixture
def other_headers(client, configured_catalog):
    return auth_headers(register_and_login_other_user(client))


def search(client, headers, query="", **params):
    response = client.get(SEARCH_URL, params={"query": query, **params}, headers=headers)
    assert response.status_code == 200
    return response.json()["results"]


def names(results):
    return [result["name"] for result in results]


def create_food(client, headers, name, **values):
    payload = {
        "name": name, "reference_weight_g": 100, "calories_kcal": 60,
        "protein_g": 3, "carbohydrates_g": 5, "fat_g": 3, **values,
    }
    response = client.post(FOODS_URL, json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def import_product(client, headers, code):
    return client.post(f"{FOODS_URL}/catalog/{code}/import", headers=headers).json()


def consume(client, headers, food, consumed_at="2026-01-01T12:00:00Z"):
    response = client.post(
        "/food-consumptions",
        headers=headers,
        json={
            "food_id": food["id"], "quantity_g": 100,
            "meal_type": "lunch", "consumed_at": consumed_at,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_search_requires_authentication(client, configured_catalog):
    assert client.get(SEARCH_URL, params={"query": "lait"}).status_code == 401


# Les aliments de la base et du catalogue sont triés ensemble, sans égard à la provenance.
def test_results_are_ranked_together(client, headers, other_headers):
    create_food(client, other_headers, "Lait de chèvre")
    create_food(client, other_headers, "Café au lait")

    assert names(search(client, headers, "lait")) == [
        "Lait",                            # catalogue, nom exact
        "Lait 2 %",                        # catalogue, commence par le mot
        "Lait de chèvre",                  # base, commence par le mot
        "Petit écolier chocolat au lait",  # catalogue, plus populaire
        "Boisson au lait",                 # catalogue
        "Café au lait",                    # base
        "Laitue romaine",                  # catalogue, préfixe
    ]


def test_result_content(client, headers):
    result = search(client, headers, "lait")[0]
    assert result["food_id"] is None
    assert result["catalog_code"] == "0000000000024"
    assert result["source"] == "open_food_facts"
    assert result["brand"] == "Natrel"
    assert result["in_history"] is False
    assert Decimal(result["serving_g"]) == 250
    assert Decimal(result["reference_weight_g"]) == 100


# Rechercher ne copie rien dans `foods`.
def test_search_does_not_import(client, headers, test_session):
    search(client, headers, "lait")
    assert test_session.scalar(select(func.count()).select_from(Food)) == 0


# --- Historique ---


def test_consumed_food_comes_first(client, headers):
    food = import_product(client, headers, "0000000000048")
    consume(client, headers, food)

    results = search(client, headers, "lait")
    assert names(results)[:2] == ["Laitue romaine", "Lait"]
    assert [r["in_history"] for r in results] == [True] + [False] * 4
    assert results[0]["food_id"] == food["id"]


# Un aliment créé par l'utilisateur fait partie de son historique avant d'être consommé.
def test_created_food_is_in_history(client, headers):
    create_food(client, headers, "Café au lait")
    results = search(client, headers, "lait")
    assert names(results)[0] == "Café au lait"
    assert results[0]["in_history"] is True
    assert results[0]["catalog_code"] is None


# L'historique d'un utilisateur ne doit jamais apparaître chez un autre.
def test_history_is_private(client, headers, other_headers):
    food = import_product(client, other_headers, "0000000000048")
    consume(client, other_headers, food)
    create_food(client, other_headers, "Café au lait")

    results = search(client, headers, "lait")
    assert not any(r["in_history"] for r in results)
    assert names(results)[0] == "Lait"
    assert search(client, headers) == []


# Un produit importé, puis jamais consigné, garde sa place normale.
def test_imported_food_keeps_its_rank(client, headers):
    before = names(search(client, headers, "lait"))
    food = import_product(client, headers, "0000000000017")
    results = search(client, headers, "lait")
    assert names(results) == before
    (imported,) = [r for r in results if r["food_id"]]
    assert imported["food_id"] == food["id"]
    assert imported["in_history"] is False


def test_matching_history_is_sorted_by_relevance_then_recency(client, headers):
    for code, day in [("0000000000062", 3), ("0000000000017", 9), ("0000000000024", 1)]:
        consume(client, headers, import_product(client, headers, code), f"2026-01-0{day}T12:00:00Z")

    assert names(search(client, headers, "lait"))[:3] == [
        "Lait", "Petit écolier chocolat au lait", "Boisson au lait",
    ]


# L'historique ne doit pas masquer les nouveaux produits.
def test_history_on_top_is_limited(client, headers):
    for index in range(7):
        create_food(client, headers, f"Mon lait {index}")

    results = search(client, headers, "lait")
    assert [r["in_history"] for r in results[:6]] == [True] * 5 + [False]
    assert results[5]["name"] == "Lait"
    # Les autres restent trouvables et identifiés.
    assert sum(r["in_history"] for r in results) == 7


def test_deleted_consumption_leaves_history(client, headers):
    food = import_product(client, headers, "0000000000048")
    entry = consume(client, headers, food)
    client.delete(f"/food-consumptions/{entry['id']}", headers=headers)
    assert search(client, headers) == []


# Sans terme, l'historique est proposé du plus récent au plus ancien.
@pytest.mark.parametrize("query", ["", "   ", "%"])
def test_empty_query_returns_recent_history(client, headers, query):
    old = import_product(client, headers, "0000000000024")
    recent = import_product(client, headers, "0000000000055")
    import_product(client, headers, "0000000000031")  # jamais consigné
    consume(client, headers, recent, "2026-01-05T12:00:00Z")
    consume(client, headers, recent, "2026-01-01T12:00:00Z")
    consume(client, headers, old, "2026-01-03T12:00:00Z")

    results = search(client, headers, query)
    assert names(results) == ["Crème glacée", "Lait"]
    assert all(r["in_history"] for r in results)
    assert names(search(client, headers, query, limit=1)) == ["Crème glacée"]


# --- Correspondance ---


@pytest.mark.parametrize("query", ["creme brulee", "CRÈME BRÛLÉE", "brul crem", "maison crème"])
def test_local_search_ignores_accents_order_and_case(client, headers, query):
    create_food(client, headers, "Crème brûlée", brand="Maison")
    assert names(search(client, headers, query)) == ["Crème brûlée"]


@pytest.mark.parametrize("query", ['"', "lait OR creme", "_", "\\", "l'", "()", "100%"])
def test_special_characters_never_fail(client, headers, query):
    create_food(client, headers, "Pain")
    search(client, headers, query)


def test_barcode_finds_imported_food(client, headers):
    food = import_product(client, headers, "0055653170259")
    (result,) = search(client, headers, "055653170259")
    assert result["food_id"] == food["id"]


def test_limit(client, headers):
    create_food(client, headers, "Café au lait")
    assert len(search(client, headers, "lait", limit=3)) == 3


# Sans catalogue, les aliments de la base restent disponibles.
def test_search_without_catalog(client, headers, monkeypatch):
    create_food(client, headers, "Café au lait")
    available = client.get(SEARCH_URL, params={"query": "lait"}, headers=headers).json()
    assert available["catalog_available"] is True

    monkeypatch.setattr(settings, "off_catalog_path", None)
    body = client.get(SEARCH_URL, params={"query": "lait"}, headers=headers).json()
    assert body["catalog_available"] is False
    assert names(body["results"]) == ["Café au lait"]
