from decimal import Decimal

import pytest
from sqlalchemy import func, select

from betterself.core.config import settings
from betterself.core.exceptions import CatalogUnavailable
from betterself.models.food_models import Food, FoodSource
from betterself.repos.off_catalog_repo import OffCatalogRepository
from tests.api_helpers import FOODS_URL, RECIPES_URL
from tests.utils import auth_headers, register_and_login, register_and_login_other_user

CATALOG_URL = f"{FOODS_URL}/catalog"

@pytest.fixture
def catalog(catalog_path):
    return OffCatalogRepository(str(catalog_path))


def names(products):
    return [product.name for product in products]


# --- Recherche dans le catalogue ---


def test_search_prefers_exact_then_leading_word_then_popularity(catalog):
    assert names(catalog.search("lait")) == [
        "Lait",                            # nom exact
        "Lait 2 %",                        # commence par le mot entier
        "Petit écolier chocolat au lait",  # contient le mot entier, plus populaire
        "Boisson au lait",                 # contient le mot entier
        "Laitue romaine",                  # seulement un préfixe de mot
    ]


@pytest.mark.parametrize("query", ["creme glacee", "CRÈME GLACÉE", "crème gla"])
def test_search_ignores_accents_and_case(catalog, query):
    assert names(catalog.search(query)) == ["Crème glacée"]


def test_search_matches_brand_and_name_together(catalog):
    assert names(catalog.search("natrel boisson")) == ["Boisson au lait"]


# La syntaxe FTS5 saisie par l'utilisateur ne doit jamais être interprétée.
@pytest.mark.parametrize(
    "query",
    ['"', "lait\"", "lait OR creme", "NEAR(", "lait*", "name:lait", "l'érable", "2 %", "-", "()", "   ", "", "\x00"],
)
def test_search_never_fails_on_special_characters(catalog, query):
    assert isinstance(catalog.search(query), list)


def test_search_treats_operators_as_words(catalog):
    assert catalog.search("lait OR creme") == []


def test_search_handles_apostrophes(catalog):
    assert names(catalog.search("l'erable")) == ["Biscuits à l'érable"]


def test_search_respects_limit(catalog):
    assert len(catalog.search("lait", limit=2)) == 2


# Un code-barres UPC (12 chiffres) correspond au code EAN-13 du catalogue.
@pytest.mark.parametrize("query", ["0055653170259", "055653170259", "55653170259"])
def test_search_by_barcode(catalog, query):
    assert names(catalog.search(query)) == ["Biscuits à l'érable"]


def test_get_by_code(catalog):
    product = catalog.get("0000000000031")
    assert product.name == "Lait 2 %"
    assert product.serving_g == 250
    assert catalog.get("9999999999999") is None


# Un catalogue absent ne doit pas être confondu avec une recherche sans résultat.
def test_missing_catalog_is_unavailable(tmp_path):
    for path in (None, "", str(tmp_path / "absent.sqlite")):
        catalog = OffCatalogRepository(path)
        with pytest.raises(CatalogUnavailable):
            catalog.search("lait")
        with pytest.raises(CatalogUnavailable):
            catalog.get("0000000000024")
    assert not (tmp_path / "absent.sqlite").exists()


def test_corrupted_catalog_is_unavailable(tmp_path):
    path = tmp_path / "off.sqlite"
    path.write_bytes(b"ceci n'est pas une base SQLite" * 100)
    with pytest.raises(CatalogUnavailable):
        OffCatalogRepository(str(path)).search("lait")


# --- Routes ---


def test_import_without_catalog(client, monkeypatch):
    monkeypatch.setattr(settings, "off_catalog_path", None)
    headers = auth_headers(register_and_login(client))
    response = client.post(f"{CATALOG_URL}/0000000000024/import", headers=headers)
    assert response.status_code == 503


def test_import_creates_food(client, configured_catalog):
    token = register_and_login(client)
    response = client.post(
        f"{CATALOG_URL}/0000000000055/import", headers=auth_headers(token)
    )
    assert response.status_code == 201
    food = response.json()
    assert food["name"] == "Crème glacée"
    assert food["brand"] == "Coaticook"
    assert food["source"] == "open_food_facts"
    assert food["external_reference_id"] == "0000000000055"
    assert food["created_by_user_id"] is None
    assert Decimal(food["reference_weight_g"]) == 100
    assert Decimal(food["calories_kcal"]) == Decimal("207.12")
    assert client.get(f"{FOODS_URL}/{food['id']}").status_code == 200


# Deux utilisateurs qui choisissent le même produit partagent le même aliment.
def test_import_is_idempotent(client, configured_catalog, test_session):
    first = client.post(
        f"{CATALOG_URL}/0000000000024/import",
        headers=auth_headers(register_and_login(client)),
    )
    second = client.post(
        f"{CATALOG_URL}/0000000000024/import",
        headers=auth_headers(register_and_login_other_user(client)),
    )
    assert (first.status_code, second.status_code) == (201, 200)
    assert first.json()["id"] == second.json()["id"]
    assert test_session.scalar(select(func.count()).select_from(Food)) == 1


# Un produit retiré du catalogue reste utilisable s'il a déjà été importé.
def test_import_returns_existing_food_without_catalog(client, configured_catalog, monkeypatch):
    headers = auth_headers(register_and_login(client))
    url = f"{CATALOG_URL}/0000000000024/import"
    first = client.post(url, headers=headers)
    monkeypatch.setattr(settings, "off_catalog_path", None)
    second = client.post(url, headers=headers)
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]


# La portion du fabricant est conservée avec l'aliment.
def test_import_keeps_serving(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    food = client.post(f"{CATALOG_URL}/0000000000024/import", headers=headers).json()
    assert Decimal(food["serving_g"]) == 250
    # Les valeurs nutritives restent exprimées pour 100 g.
    assert Decimal(food["reference_weight_g"]) == 100

    # Elle est aussi retournée par la lecture et par la recherche.
    read = client.get(f"{FOODS_URL}/{food['id']}").json()
    (found,) = client.get(FOODS_URL, params={"query": "lait"}).json()
    assert Decimal(read["serving_g"]) == Decimal(found["serving_g"]) == 250


def test_import_without_serving(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    food = client.post(f"{CATALOG_URL}/0000000000048/import", headers=headers).json()
    assert food["serving_g"] is None


# Les données participatives contiennent des portions invraisemblables.
@pytest.mark.parametrize(
    ("code", "expected"),
    [("0000000000079", None), ("0000000000086", None), ("0000000000093", 1000), ("0000000000055", 66)],
)
def test_implausible_servings_are_ignored(catalog, code, expected):
    assert catalog.get(code).serving_g == expected


# --- Unités ---


def test_get_reads_unit(catalog):
    product = catalog.get("0000000000017")
    assert (product.unit_name, product.unit_name_plural, product.unit_g) == ("biscuit", "biscuits", 12.5)
    assert product.weight_is_estimated is False


def test_product_without_unit(catalog):
    product = catalog.get("0000000000048")
    assert (product.unit_name, product.unit_name_plural, product.unit_g) == (None, None, None)
    assert product.weight_is_estimated is False


# Une portion en volume (« 250 ml ») est estimée même sans unité.
def test_volume_serving_is_estimated(catalog):
    product = catalog.get("0000000000031")
    assert product.unit_name is None
    assert product.weight_is_estimated is True


def test_import_keeps_unit(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    food = client.post(f"{CATALOG_URL}/0000000000024/import", headers=headers).json()
    assert (food["unit_name"], food["unit_name_plural"]) == ("tasse", "tasses")
    assert Decimal(food["unit_g"]) == 250
    assert food["weight_is_estimated"] is True

    # Elle est aussi retournée par la lecture et par la recherche.
    read = client.get(f"{FOODS_URL}/{food['id']}").json()
    (found,) = client.get(FOODS_URL, params={"query": "lait"}).json()
    assert read["unit_name"] == found["unit_name"] == "tasse"
    assert read["weight_is_estimated"] is found["weight_is_estimated"] is True


# Le résultat de recherche d'un produit pas encore importé porte aussi l'unité.
def test_search_result_has_unit(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    results = client.get(f"{FOODS_URL}/search", params={"query": "ecolier"}, headers=headers).json()
    result = results["results"][0]
    assert result["catalog_code"] == "0000000000017"
    assert (result["unit_name"], Decimal(result["unit_g"])) == ("biscuit", Decimal("12.5"))
    assert result["weight_is_estimated"] is False


def test_import_unknown_product(client, configured_catalog):
    response = client.post(
        f"{CATALOG_URL}/9999999999999/import",
        headers=auth_headers(register_and_login(client)),
    )
    assert response.status_code == 404


def test_import_requires_authentication(client, configured_catalog):
    assert client.post(f"{CATALOG_URL}/0000000000024/import").status_code == 401


# Un aliment manuel portant le même code ne doit pas être confondu avec le produit.
def test_import_ignores_manual_food_with_same_reference(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    manual = client.post(
        FOODS_URL,
        headers=headers,
        json={
            "name": "Mon lait", "reference_weight_g": 100, "calories_kcal": 60,
            "protein_g": 3, "carbohydrates_g": 5, "fat_g": 3,
            "external_reference_id": "0000000000024",
        },
    )
    assert manual.status_code == 201
    response = client.post(f"{CATALOG_URL}/0000000000024/import", headers=headers)
    assert response.status_code == 201
    assert response.json()["id"] != manual.json()["id"]


# Deux imports simultanés : la contrainte unique tranche, sans erreur 500.
def test_import_survives_concurrent_insert(test_session, catalog, monkeypatch):
    from betterself.repos.food_repo import FoodRepository

    repository = FoodRepository(test_session)
    product = catalog.get("0000000000024")
    existing, created = repository.get_or_import_product(product)
    assert created is True

    # Simule une vérification initiale faite juste avant l'insertion concurrente.
    real_lookup = repository.get_by_external_reference
    calls = []

    def stale_lookup(code):
        calls.append(code)
        return None if len(calls) == 1 else real_lookup(code)

    monkeypatch.setattr(repository, "get_by_external_reference", stale_lookup)
    food, created = repository.get_or_import_product(product)
    assert created is False
    assert food.id == existing.id
    assert food.source is FoodSource.OPEN_FOOD_FACTS


# L'aliment importé s'utilise dans le journal comme les autres.
def test_imported_food_can_be_consumed(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    food = client.post(f"{CATALOG_URL}/0000000000024/import", headers=headers).json()
    response = client.post(
        "/food-consumptions",
        headers=headers,
        json={"food_id": food["id"], "quantity_g": 250, "meal_type": "breakfast"},
    )
    assert response.status_code == 201
    assert Decimal(response.json()["calories_kcal"]) == 150


# L'ingrédient d'une recette garde l'unité de l'aliment importé.
def test_recipe_ingredient_has_unit(client, configured_catalog):
    headers = auth_headers(register_and_login(client))
    food = client.post(f"{CATALOG_URL}/0000000000017/import", headers=headers).json()
    recipe = client.post(
        RECIPES_URL,
        json={"name": "Collation", "servings": 1, "ingredients": [{"food_id": food["id"], "quantity_g": 25}]},
        headers=headers,
    ).json()
    ingredient_food = recipe["ingredients"][0]["food"]
    assert (ingredient_food["unit_name"], Decimal(ingredient_food["unit_g"])) == ("biscuit", Decimal("12.5"))
    assert ingredient_food["weight_is_estimated"] is False
