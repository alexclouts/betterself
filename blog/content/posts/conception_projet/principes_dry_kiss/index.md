---
title: "Application les principes DRY/KISS"
header: ""
date: 2026-10-31T00:11:55.000Z
description: "Réflexions sur l'abrègement du code et du rôle joué par les classes service, models et schemas."
tags:
  - Architecture
  - FastAPI
  - IA
  - Backend
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Abrégation du code

Lors de la rencontre de mi-parcours, j'ai eu l'occasion de discuter de la structure et du rôle joué par les fichiers `schemas.py`, `service.py` et `models.py`. Il était question de déterminer si la classe _Service_ était vraiment nécessaire et répondait aux principes **DRY** et **KISS** dans l'organisation du code.

J'ai donc questionné l'IA à ce sujet, qui m'a offerte des pistes de réflexions intéressantes.

## Conversation avec l'IA

Oui : tu peux réduire la répétition, mais je te conseille de ne pas fusionner complètement le service dans le modèle. Pour BetterSelf, la meilleure solution KISS/DRY est de garder une couche service légère, de centraliser les exceptions métier dans le service, et d’utiliser des fixtures pytest pour le client de test.

Ton professeur a raison sur le principe : les requêtes CRUD peuvent être regroupées près du modèle. Mais il y a une distinction importante :

| Approche                                      | Avantages                                                                              | Inconvénients                                                                                             |
| --------------------------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Méthodes dans Measurement                     | Moins de fichiers, requêtes proches de la table, code court                            | Le modèle SQLAlchemy mélange structure de table et logique applicative; plus difficile à tester isolément |
| Service séparé                                | Séparation claire : modèle = table, service = règles métier et accès DB                | Un fichier de plus, un peu plus de code                                                                   |
| Service + méthodes utilitaires dans le modèle | Bon compromis : le modèle expose des requêtes simples, le service orchestre les règles | Légère complexité supplémentaire                                                                          |

Voici les modifications précises que je ferais. L’objectif est de garder trois responsabilités claires : `models.py` décrit la table, `service.py` applique les règles métier et accède à la base, `router.py` traduit les résultats en réponses HTTP.

### models.py

```python
    @classmethod
    def for_user(cls, user_id: UUID):
        return select(cls).where(cls.user_id == user_id)
```

**Avantage :** tu supprimes la répétition de `Measurement.user_id == user.id` dans chaque méthode.\
**Inconvénient :** si tu commences à mettre `create`, `update`, `delete`, la validation d’autorisation et les exceptions directement dans `Measurement`, la classe devient un « god object ». Ce n’est pas idéal.

## Analyse

Cette explication m'a également fait découvrir la notion de [God object](https://dev.to/wallacefreitas/understanding-god-objects-in-object-oriented-programming-5636) et l'importance que chaque classe respecte le principe _SRP (Single Responsability Principle)_. Ces responsabilités sont clairement définies par l'IA, qui explique le rôle de chaque fichier dans la structure du projet.

# Validation de données par SQLAlchemy

Durant l'entrevue, il a ensuite été question de vérifier si Pydantic était le meilleur endroit pour effectuer la validation des données. Une approche plus sûr serait d'ajouter une contrainte depuis la base de données directement. Je lui ai d'abord demandé les risques que la validation faite par Pydantic soit contourné si, par exemple, une nouvelle entrée de `Measurement` est faite à l'extérieure du répertoire. Je lui ai ensuite demandé si l'ajout d'une contrainte SQL était quelque chose de plausible et voici ce qu'elle m'a répondu :

## Conversation avec l'IA

#### _Question:_ Est-ce que le fait de valider les schémas de donnée par Pydantic peut être problématique si, par exemple, je crée un nouveau Measurement ailleurs dans le code que à partir du répertoire measurements, où le fichier schemas est situé?

Non, ce n’est pas problématique en soi — c’est même généralement souhaitable. Le point important est de distinguer validation à l’entrée de l’API et règle métier appliquée partout dans l’application.

### Deux niveaux de validation

| Niveau                                | Où le placer    | Exemple BetterSelf                                                                                                   |
| ------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------- |
| Format et validité d’une donnée       | Schéma Pydantic | weight_kg doit être un nombre, la date doit être une date, le poids doit être plausible                              |
| Cohérence avec la base ou le contexte | Service         | Un utilisateur ne peut pas avoir deux mesures à la même date, une mesure doit appartenir à l’utilisateur authentifié |

Si tu crées un `Measurement` ailleurs dans le code — par exemple depuis un futur module imports, reports ou un script d’import CSV — tu peux réutiliser le même schéma Pydantic :

```Python
from betterself.measurements.schemas import MeasurementCreate

data = MeasurementCreate(
    date=parsed_date,
    weight_kg=parsed_weight,
)

measurement = measurement_service.create_measurement(
    user=user,
    data=data,
)
```

### Le vrai risque

Le risque apparaît seulement si tu contournes le schéma et crées directement l’objet SQLAlchemy. Dans ce cas, Pydantic n’est jamais appelé. Ce n’est pas un défaut de Pydantic : c’est simplement que tu as choisi une autre porte d’entrée.

---

#### _Question:_ Est-ce qu'il ne serait pas justement préférable de conduire cette validation directement à partir de la base de données SQLAlchemy?

Oui, tu peux — et pour une règle comme « le poids doit être plausible », une contrainte SQL est même une bonne **dernière ligne de défense**. Mais je ne la recommanderais pas comme seul mécanisme de validation pour BetterSelf.

**Avantages :**

- La règle est appliquée par la base elle-même, donc elle protège toutes les sources d’écriture.
- Elle est très fiable : la base refuse l’insertion ou la mise à jour invalide.
- Elle est appropriée pour une invariant simple et stable, comme une plage de valeurs.

**Inconvénients :**

- L’erreur retournée est une `IntegrityError`, pas un message utilisateur clair.
- Elle ne produit pas automatiquement un `422` FastAPI avec le champ fautif.
- Modifier la règle demande une migration Alembic, alors qu’une règle Pydantic se modifie dans le code applicatif.
- Les contraintes SQL ne sont pas le bon outil pour les règles qui dépendent d’autres tables ou du contexte utilisateur.

### Recommandation pratique

Pour BetterSelf, je ferais **les deux**, mais avec des rôles différents :

1. **Pydantic** : validation ergonomique des entrées API et des futurs imports Python.
2. **Contrainte SQL** : protection finale de l’intégrité des données.

Donc : **oui pour une contrainte `CheckConstraint` sur le poids, mais garde aussi Pydantic**. Pydantic améliore l’expérience de l’utilisateur de l’API; la contrainte SQL garantit l’intégrité durable de tes données.

## Analyse

Cette donc précisément cette approche que j'ai choisi d'implanter au sein de mon code. Il y aura donc une double validation effectuée à la fois par _Pydantic_, qui génère un code d'erreur HTTP **422** que l'application peut interprété, et par une contrainte de _SQLAlchemy_, qui garantit que cette règle ne peut pas être brisée autrement.

# Traitement des erreurs par le routeur

La dernière validation que j'ai fait concernait le traitement des erreurs logique au sein des fonctions de routage. Actuellement, ma fonction qui me permet de récupérer une mesure est construite de la manière suivante :

```python
@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user)
):
    service = MeasurementService(db)
    measurement = service.get_measurement_by_id(user=current_user, measurement_id=measurement_id)

    if measurement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    return measurement
```

On peut voir qu'une exception HTTP est lancée si la mesure recherchée n'est pas trouvée. Durant la rencontre, nous avons établi quecette vérification devrait possiblement être faite **plus profondément dans le code**, soit au niveau du service par exemple. Voici la suggestion de l'IA:

## Conversation avec l'IA

#### _Question:_ Pour revenir à la déclaration des fonctions dans le routeur, considères-tu que c'est la méthode appropriée de lancer des exceptions directement à partir de celles-ci, ou devraient-elles plutôt être lancé à partir du service?

Oui, pour BetterSelf, je considère que **lever `HTTPException` directement dans les fonctions du routeur est approprié**, à condition que le routeur ne fasse que traduire une situation déjà détectée par le service. La version la plus propre est toutefois : le service lève une **exception métier**, et le routeur la convertit en `HTTPException`.

| Type d’erreur                                             | Où la lever                       | Exemple                                   |
| :-------------------------------------------------------- | :-------------------------------- | :---------------------------------------- |
| Requête mal formée                                        | Pydantic / FastAPI                | `weight_kg` absent, date invalide → `422` |
| Ressource introuvable ou non autorisée pour l’utilisateur | Service : exception métier        | `MeasurementNotFound`                     |
| Traduction en réponse HTTP                                | Routeur                           | `MeasurementNotFound` → `404`             |
| Erreur d’infrastructure                                   | Service ou couche base de données | Connexion DB perdue → généralement `500`  |

Le routeur est la couche qui connaît HTTP. Il est donc normal qu’il décide qu’une situation correspond à `404`, `401`, `403`, etc. Mais il ne devrait pas avoir à savoir **comment** chercher une mesure dans la base ni répéter cette logique dans chaque endpoint.

Le service détecte le problème et lève une exception métier et le routeur traduit ensuite cette exception en code HTTP :

```python
@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(
    measurement_id: int,
    current_user: User = Depends(read_current_user),
    service: MeasurementService = Depends(get_measurement_service),
):
    try:
        return service.get_measurement_by_id(
            user=current_user,
            measurement_id=measurement_id,
        )
    except MeasurementNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesure introuvable.",
        )
```

### Pourquoi ne pas mettre `HTTPException` dans le service ?

Cela fonctionnerait, mais ce n’est pas idéal :

- `MeasurementService` dépendrait alors de FastAPI, alors qu’il devrait surtout dépendre de SQLAlchemy et de tes règles métier.
- Si tu réutilises le service dans un script CLI, une tâche planifiée ou un futur import de données, il lèverait une exception HTTP alors qu’il n’y a pas de requête HTTP.
- Les tests du service devraient alors connaître FastAPI, même s’ils veulent seulement vérifier la logique métier.

### Compromis KISS

Pour trois endpoints, garde le `try/except` dans le routeur. C’est explicite, facile à lire et suffisant.

# Les tests unitaires

Finalement, je me suis servi de l'IA pour appliquer une méthodologie plus stricte concernant mes tests unitaires. Certains tests étaient responsables de valider toutes les erreurs de syntaxe et de type pour les champs `weight_kg` et `date`, et donc elles perdaient leur caractère _atomique_ :

```python
def test_new_measurement_invalid_fields(client):
    access_token = register_and_login(client)

    # Poids non numérique
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": "invalid-weight"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Poids trop grand
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": 1000},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    # Poids trop petit
    response = client.post(
        "/measurements",
        json={"date": str(date.today()),"weight_kg": 25},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    ...
```

De plus, des fonctions utilitaires ont été créées pour alléger le code. C'est le cas, par exemple, d'une fonction permettant de centraliser les requêtes sur les mesures pour `PATCH`, `DELETE` et `GET` :

```python

# Fonction utilitaire pour effectuer une requête GET, PATCH ou DELETE sur une mesure
# Cette fonction a été créée pour alléger le code des tests en centralisant les requêtes sur les mesures.
def request_measurement(client, method: str, measurement_id: int, access_token: str | None = None, json_data: dict | None = None):
    headers = auth_headers(access_token) if access_token else {}

    # GET et DELETE n'acceptent pas de corps JSON; seul PATCH en a besoin ici
    if method == "patch":
        return client.patch(
            f"/measurements/{measurement_id}",
            headers=headers,
            json=json_data,
        )
    return getattr(client, method)(
        f"/measurements/{measurement_id}",
        headers=headers,
    )
```

## Conclusion

Maintenant que le code est réorganisé de manière plus claire et structurée, il est temps de poursuivre le développement du _Backend_ et des tables figurant dans la base de données !
