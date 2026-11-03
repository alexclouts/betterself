from decimal import Decimal

from tests.utils import auth_headers, register_and_login, register_and_login_other_user


RECIPES_URL = "/recipes"


# Données valides pour créer une recette
def valid_recipe_payload() -> dict:
    return {
        "name": "Bol de poulet et riz",
        "description": "Faire cuire le riz, puis ajouter le poulet et les légumes.",
        "total_weight_g": 800,
        "servings": 4,
    }


# Test pour vérifier la création d'une recette
def test_create_recipe_success(client):
    access_token = register_and_login(client)

    response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert response.status_code == 201

    recipe = response.json()
    assert recipe["name"] == "Bol de poulet et riz"


# Test pour vérifier que la création échoue sans authentification
def test_create_recipe_unauthorized(client):
    response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
    )
    assert response.status_code == 401


# Test pour vérifier qu'un nom vide est refusé
def test_create_recipe_rejects_empty_name(client):
    access_token = register_and_login(client)

    payload = valid_recipe_payload()
    payload["name"] = "   "

    response = client.post(
        RECIPES_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier qu'un poids total invalide est refusé
def test_create_recipe_rejects_invalid_total_weight(client):
    access_token = register_and_login(client)

    payload = valid_recipe_payload()
    payload["total_weight_g"] = 0

    response = client.post(
        RECIPES_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier qu'un nombre de portions invalide est refusé
def test_create_recipe_rejects_invalid_servings(client):
    access_token = register_and_login(client)

    payload = valid_recipe_payload()
    payload["servings"] = 0

    response = client.post(
        RECIPES_URL,
        json=payload,
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier la récupération d'une recette
def test_get_recipe_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Récupération de la recette créée par son ID
    response = client.get(
        f"{RECIPES_URL}/{created_recipe['id']}",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["id"] == created_recipe["id"]
    assert recipe["name"] == "Bol de poulet et riz"


# Test pour vérifier qu'une recette inexistante retourne 404
def test_get_recipe_not_found(client):
    access_token = register_and_login(client)

    response = client.get(
        f"{RECIPES_URL}/00000000-0000-0000-0000-000000000000",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 404


# Test pour vérifier qu'un utilisateur ne peut pas lire la recette d'un autre
def test_get_recipe_forbidden_for_other_user(client):
    owner_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Tentative de récupération de la recette par un autre utilisateur (non autorisé)
    other_token = register_and_login_other_user(client)
    response = client.get(
        f"{RECIPES_URL}/{created_recipe['id']}",
        headers=auth_headers(other_token),
    )
    assert response.status_code == 404


# Test pour vérifier que la liste ne retourne que les recettes de l'utilisateur
def test_list_recipes_isolated_between_users(client):
    owner_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    # Vérification que la liste des recettes pour l'autre utilisateur est vide
    other_token = register_and_login_other_user(client)
    response = client.get(
        RECIPES_URL,
        headers=auth_headers(other_token),
    )
    assert response.status_code == 200
    assert response.json() == []


# Test pour vérifier la pagination des recettes
def test_list_recipes_pagination(client):
    access_token = register_and_login(client)

    # Création de plusieurs recettes pour tester la pagination
    for index in range(3):
        payload = valid_recipe_payload()
        payload["name"] = f"Recette {index + 1}"

        creation_response = client.post(
            RECIPES_URL,
            json=payload,
            headers=auth_headers(access_token),
        )
        assert creation_response.status_code == 201

    # Vérification que la première page contient les deux premières recettes
    first_page = client.get(
        RECIPES_URL,
        params={"limit": 2, "offset": 0},
        headers=auth_headers(access_token),
    )
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2

    # Vérification que la deuxième page contient la recette restante
    second_page = client.get(
        RECIPES_URL,
        params={"limit": 2, "offset": 2},
        headers=auth_headers(access_token),
    )
    assert second_page.status_code == 200
    assert len(second_page.json()) == 1


# Test pour vérifier que les recettes archivées sont masquées par défaut
def test_list_recipes_hides_archived_by_default(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    # Archivage de la recette créée par l'utilisateur
    created_recipe = creation_response.json()
    archive_response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}/archive",
        json={"is_archived": True},
        headers=auth_headers(access_token),
    )
    assert archive_response.status_code == 200

    # Vérification que la recette archivée n'apparaît pas dans la liste par défaut
    # Récupération de la liste des recettes sans paramètre include_archived
    list_response = client.get(
        RECIPES_URL,
        headers=auth_headers(access_token),
    )
    assert list_response.status_code == 200
    assert list_response.json() == []


# Test pour vérifier que les recettes archivées peuvent être incluses
def test_list_recipes_can_include_archived(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Archivage de la recette créée par l'utilisateur
    archive_response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}/archive",
        json={"is_archived": True},
        headers=auth_headers(access_token),
    )
    assert archive_response.status_code == 200

    # Vérification que la recette archivée est incluse dans la liste lorsque include_archived est True
    list_response = client.get(
        RECIPES_URL,
        params={"include_archived": True},
        headers=auth_headers(access_token),
    )
    assert list_response.status_code == 200

    recipes = list_response.json()
    assert len(recipes) == 1
    assert recipes[0]["is_archived"] is True


# Test pour vérifier la mise à jour partielle d'une recette
def test_update_recipe_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Mise à jour partielle de la recette existante
    response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}",
        json={
            "name": "Bol de boeuf haché",
            "servings": 3,
        },
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["name"] == "Bol de boeuf haché"
    assert recipe["servings"] == 3


# Test pour vérifier qu'un nom vide est refusé lors de la mise à jour
def test_update_recipe_rejects_empty_name(client):
    access_token = register_and_login(client)

    # Création d'une recette initiale pour l'utilisateur
    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Tentative de mise à jour avec un nom vide, ce qui devrait être refusé
    response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}",
        json={"name": "   "},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 422


# Test pour vérifier qu'un utilisateur ne peut pas modifier la recette d'un autre
def test_update_recipe_forbidden_for_other_user(client):
    owner_token = register_and_login(client)

    # Création d'une recette par l'utilisateur propriétaire
    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    other_token = register_and_login_other_user(client)

    # Mise à jour de la recette par un autre utilisateur (non autorisé)
    response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}",
        json={"name": "Nom non autorisé"},
        headers=auth_headers(other_token),
    )
    assert response.status_code == 404


# Test pour vérifier l'archivage d'une recette
def test_archive_recipe_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    # Archivage de la recette
    response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}/archive",
        json={"is_archived": True},
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    recipe = response.json()
    assert recipe["is_archived"] is True


# Test pour vérifier le désarchivage d'une recette
def test_unarchive_recipe_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    archive_response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}/archive",
        json={"is_archived": True},
        headers=auth_headers(access_token),
    )
    assert archive_response.status_code == 200

    unarchive_response = client.patch(
        f"{RECIPES_URL}/{created_recipe['id']}/archive",
        json={"is_archived": False},
        headers=auth_headers(access_token),
    )
    assert unarchive_response.status_code == 200

    recipe = unarchive_response.json()
    assert recipe["is_archived"] is False


# Test pour vérifier la suppression d'une recette
def test_delete_recipe_success(client):
    access_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(access_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    delete_response = client.delete(
        f"{RECIPES_URL}/{created_recipe['id']}",
        headers=auth_headers(access_token),
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"{RECIPES_URL}/{created_recipe['id']}",
        headers=auth_headers(access_token),
    )
    assert get_response.status_code == 404


# Test pour vérifier qu'un utilisateur ne peut pas supprimer la recette d'un autre
def test_delete_recipe_forbidden_for_other_user(client):
    owner_token = register_and_login(client)

    creation_response = client.post(
        RECIPES_URL,
        json=valid_recipe_payload(),
        headers=auth_headers(owner_token),
    )
    assert creation_response.status_code == 201

    created_recipe = creation_response.json()
    other_token = register_and_login_other_user(client)

    delete_response = client.delete(
        f"{RECIPES_URL}/{created_recipe['id']}",
        headers=auth_headers(other_token),
    )
    assert delete_response.status_code == 404