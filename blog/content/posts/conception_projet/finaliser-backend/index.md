---
title: "Finaliser le backend"
header: ""
date: 2026-11-11T00:22:44.000Z
description: "Réflexions sur la structure du projet et début de conception du frontend."
tags:
  - Architecture
  - IA
  - Backend
  - Frontend
  - Alembic
  - Onboarding
  - Vidéo
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Finaliser le backend

Je suis maintenant rendu à finaliser les dernières composantes du backend. Celles-ci concernent surtout le processus de _Onboarding_ dans l'application. J'envisage, par exemple, de quelle manière nous allons vérifier que l'utilisateur a bien réussi son processus de Onboarding? Je suggère alors mon idée à l'IA pour qu'elle m'aide à identifier la meilleure approche pour la suite.

## Conversation avec l'IA

#### _Question :_ Je crois avoir fait le tour des fonctionnalités principales. Maintenant j'ai un questionnement concernant le processus end-to-end de l'application. Une des vérifications qui pourrait être fait pour valider que l'utilisateur a bien complété le processus de Onboarding en entier est de valider que l'utilisateur a une entrée dans la table nutrition-goal. Maintenant, de quelle façon me suggères-tu d'effectuer cette vérification?

Ne vérifie pas l’onboarding uniquement par la présence d’une ligne dans `nutrition_goals`. Cette table prouve seulement qu’un objectif a été créé; elle ne garantit pas que le profil, la première mesure et la cible nutritionnelle existent aussi. La meilleure approche est un **statut d’onboarding calculé** à partir des prérequis réels.

### Définition de l’onboarding

D’après ton modèle, l’onboarding est complet lorsque l’utilisateur possède :

- Un profil avec sexe, année de naissance, taille et niveau d’activité.
- Au moins une mesure de poids.
- Un objectif nutritionnel actif.
- Une cible nutritionnelle active associée à cet objectif.[^99_2][^99_1]

La présence d’un `NutritionGoal` seul n’est donc pas suffisante : sans profil ni mesure, l’application ne peut pas calculer une cible fiable.

### Approche recommandée

Ajoute un endpoint dédié :

```http
GET /users/me/onboarding-status
```

Il retourne un objet simple, calculé à la volée :

```json
{
  "is_complete": false,
  "missing_steps": ["profile", "body_measurement", "goal_target"],
  "steps": {
    "profile": false,
    "body_measurement": true,
    "nutrition_goal": true,
    "goal_target": false
  }
}
```

C’est preferable à un booléen stocké dans la base, car l’état peut changer : l’utilisateur peut supprimer une mesure, archiver un objectif ou modifier son profil.

## Analyse

J'ai donc orienté mon approche à partir de cette rétroaction. C'est de cette façon que j'ai construit le service de Onboarding.

# Restructuration des fichiers

D'ailleurs, en travaillant sur le service de _OnBoarding_, je me suis mis à reconsidérer certains aspects de mon architecture. Pas plus tard que dans le dernier article, j'ai réitéré que je n'allais pas ajouter un fichier _repository_ pour l'instant. Par contre, je trouvais que l'utilisation du mot `service` était peut-être inapproprié pour certains cas d'usage. J'ai donc voulu corriger cette confusion avant d'aller plus loin dans le projet.

#### _Question :_ Mon questionnement à présent concerne l'appelation de "service" pour les classes responsables de chaque objet associé à un modèle dans la base de données. Pour moi, un service est exactement ce que fait OnBoardingService ici, c'est-à-dire qu'il a une responsabilité isolé dans l'application qui a une utilité pour le frontend. Y aurait-il une meilleure appelation que Service pour, par exemple, Measurement ou NutritionGoal?

Oui, ton intuition est juste : `OnboardingService` est un **service applicatif** parce qu’il orchestre plusieurs modèles et répond à un cas d’usage concret. En revanche, `MeasurementService` ou `NutritionGoalService` sont plutôt des **services de domaine CRUD** : leur nom est acceptable, mais `Repository` ou `Manager` peut être plus précis selon le rôle que tu veux leur donner.

Pour ton projet, je garderais `Service` pour les classes qui ont une **responsabilité métier transversale**, et j’utiliserais `Repository` pour les classes principalement responsables d’un modèle.

### Architecture que je te suggère

```text
routers/
  measurements.py
  nutrition_goals.py
  onboarding.py

services/
  onboarding_service.py
  target_service.py
  consumption_service.py
  recipe_service.py

repositories/
  measurement_repository.py
  nutrition_goal_repository.py
  goal_target_repository.py
  food_repository.py
  recipe_repository.py
```

Le routeur appelle un service; le service applique les règles métier et utilise les repositories pour accéder à la base.

### Ma recommandation pratique

Pour éviter une refonte importante maintenant :

1. Garde `MeasurementService` et `NutritionGoalService` si elles contiennent déjà de la logique au-delà du CRUD.
1. Renomme en `Repository` uniquement les classes qui sont essentiellement des wrappers SQLAlchemy.
1. Réserve `Service` aux classes qui orchestrent plusieurs modèles ou implémentent une règle métier.
1. Crée `OnboardingService` comme un service distinct, sans le fusionner avec `UserService`.

Le nom `Service` n’est pas incorrect; il est simplement moins précis lorsque la classe ne fait que du CRUD. Dans ton cas, `OnboardingService`, `TargetService`, `RecipeService` et `ConsumptionService` méritent bien ce nom.

## Analyse

J'ai donc orienté mon code en conséquence. Des _repositories_ ont été créé pour les modèles avec seulement quelques opérations CRUD simples, et les services s'occupent des fonctions de logique. Cette refonte a été longue, mais c'était une itération nécessaire pour poursuivre sur de bonnes bases.

# Les erreurs contextuelles de l'IA

Je me suis rendu compte également que l'une des raisons pour laquelle c'est important de réviser le code est que l'IA oublie les conversations précédentes. Ce genre de problème est ce qui rend important notre rôle de contre-vérificateur. Par exemple, un exemple simple peut se trouver c'est le code qui m'a été suggéré :

{{< img
src="screenshot1.png"
alt="Screenshot"
caption=""
width="800">}}

Bien que l'IA m'ait aidé à concevoir la table `measurements`, elle assume qu'un paramètre `height_cm` s'y trouve alors que ce n'est pas le cas, ce qui va générer un message d'erreur lors de la compilation.

# La gestion des opérations commit

C'est une découverte que j'ai fait en analysant le code de l'IA.Pour l'implémentation du service de Onboarding, j'ai réalisé que l'opération `commit()` n'était pas présente dans les fonctions visant à sauvegarder les données transmises par le frontend. En discutant avec l'IA, elle a offert un raisonnement intéressant :

## Conversation avec l'IA

#### _Question :_ Un autre questionnement que j'ai concerne le commit. Actuellement, aucun commit() n'est fait dans la base de données par les fonctions appelées dans le service Onboarding. Pourquoi?

C’est normal — et même souhaitable — que `add()` ne fasse pas de `commit()`. Dans une architecture repository + service, le repository **prépare** les changements; la transaction est validée une seule fois à la fin de l’opération métier, idéalement dans `get_db`.

```python
def add(self, measurement: Measurement) -> Measurement:
    self.db.add(measurement)
    return measurement
```

`self.db.add(measurement)` enregistre l’objet dans la session SQLAlchemy, mais ne l’écrit pas encore durablement dans la base. Les modifications sont conservées dans la transaction en cours jusqu’à un `commit()`. Pour l’onboarding, tu veux que **profil, mesure, objectif nutritionnel et cible** soient enregistrés ensemble ou pas du tout. Le meilleur endroit est donc la dépendance `get_db`, qui encadre toute la requête HTTP.

Ainsi :

- Si `save_onboarding` réussit, les quatre enregistrements sont validés par un seul `commit()`.
- Si une erreur survient après la création du profil, tout est annulé par `rollback()`.
- Les repositories restent simples et ne connaissent pas la politique transactionnelle.

### À quelle fréquence

get_db fait **un seul** `commit()` **par requête HTTP réussie**, après que le routeur a terminé et que FastAPI a produit la réponse. Ce n’est donc pas un commit par appel de repository, ni par objet ajouté.

### Chemin logique

```
Requête HTTP arrive
        ↓
get_db() crée la session
        ↓
yield db → FastAPI injecte db dans le routeur
        ↓
Routeur appelle OnboardingService
        ↓
Repositories font add() / modifications
        ↓
Routeur retourne une réponse
        ↓
get_db() reprend après yield
        ↓
db.commit() une seule fois
        ↓
db.close()
```

## Analyse

Mon implémentation actuelle effectue les opérations `commit` directement dans les fonctions de repositories. J'ai donc apporté les modifications pour refléter ce changement, ce qui a généré un paquet d'erreur lorsque j'ai voulu exécuter à nouveau les tests unitaires.

# Le rôle de `flush`

Assez rapidement, je me suis rendu compte que des erreurs étaient générées :

```
E               fastapi.exceptions.ResponseValidationError: 2 validation errors:
E                 {'type': 'uuid_type', 'loc': ('response', 'id'), 'msg': 'UUID input should be a string, bytes or UUID object', 'input': None}
E                 {'type': 'bool_type', 'loc': ('response', 'is_active'), 'msg': 'Input should be a valid boolean', 'input': None}
E
E                 File "/home/alex/Documents/betterself/backend/src/betterself/routers/auth_router.py", line 35, in register_user
E                   POST /auth/register
```

## Les explications de l'IA

Avec `flush()`, SQLAlchemy applique les valeurs par défaut Python — `generate_uuid` et `True` — puis envoie l’`INSERT` dans la transaction. L’objet `user` possède donc immédiatement :

```
user.id        # UUID valide
user.is_active # True
```

Le `commit()` reste toutefois responsable de rendre l’insertion permanente.

## Analyse

Cette distinction m'a permis de structurer ma base de données autour de cette idée. L'ajout permanent des entrées dans la base de données se fera uniquement lorsque l'utilisateur confirmera ses choix.

# On s'attaque au frontend

C'est ici que je commence à construire mon frontend.

{{< alert info >}}
J'ai plus tard appris que plusieurs fonctionnalités du backend par rapport au service de _Onboarding_ étaient manquantes, donc j'ai dû faire quelques modifications au backend après avoir configuré les premières interfaces, mais on y reviendra !
{{< /alert >}}

# Erreur de migration Alembic

Il s'agit d'un cas de _troubleshooting_ que j'ai rencontré en testant les fonctionnalités de l'application. En essayant de me créer un compte, une erreur SQL s'est affiché quand j'ai tenté de m'inscrire.

{{< img
src="screenshot2.png"
alt="Screenshot"
caption=""
width="500">}}

Cette fonctionnalité avait déjà été testé auparavant lorsque j'ai développé les premières pages du frontend, donc j'ai questionné l'IA afin de comprendre ce qui était la cause possible. De plus, afficher publiquement une erreur SQL est une faille de sécurité que je devrai adresser lorsque le problème sera résolu.

#### _Question :_ Voici une erreur qui s'affiche lorsque je tente de me créer un compte dans l'application [...]. Ce genre d'erreur ne devrait pas s'afficher à l'utilisateur en production.

L'IA m'a expliqué que l'erreur était certainement dû au fait que la table `users` n'existe pas dans la base SQLite utilisée par l'application. Elle m'a donc suggéré de vérifier que la base était créée au démarrage avec _Alembic_. En voulant effectuer la migration, j'ai été exposé à ce problème :

{{< img
src="screenshot3.png"
alt="Screenshot"
caption=""
width="800">}}

## Conversation avec l'IA

L’erreur vient de SQLite : il ne supporte pas `ALTER TABLE ... ALTER COLUMN ... TYPE UUID`. Alembic a généré une migration PostgreSQL-style, mais ta base de développement est SQLite; il faut utiliser le mode **batch** d’Alembic, qui recrée la table plutôt que de tenter un `ALTER COLUMN`. Le mode batch recrée la table avec la nouvelle définition, copie les données, puis supprime l’ancienne table. C’est la méthode recommandée par Alembic pour SQLite.

### Si la base est de développement

Comme il s’agit d’une base SQLite locale et probablement sans données importantes, la solution la plus simple est souvent de repartir d’une base propre :

```bash
rm -f betterself.db
rm -rf alembic/versions/*
uv run alembic revision --autogenerate -m "V1_database_mvp"
uv run alembic upgrade head
```

Attention : cette dernière commande supprime l’historique de migrations. Ne le fais que sur une base de développement, jamais en production sans sauvegarde.

## Analyse

Étant donné que ma base de donnée n'avait pas encore été migré depuis que tous les modèles sont construits, j'ai opté pour la solution la plus simple, soit de supprimer les versions _Alembic_ pour repartir à neuf.
Par exemple, j'ai à nouveau rencontré un problème en voulant `commit` mes tables.

```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'recipe_ingredients.food_id' could not find table 'foods' with which to generate a foreign keyto target column 'id'
```

### Solution

Finalement, la solution à mon problème était que le modèle de `Food` n'était pas importé dans mon fichier `recipe_models.py`. Cet ajout m'a permis d'effectuer la migration de la base de données sans rencontrer d'erreur.

De plus, j'ai ajouté une fonction afin de gérer les exceptions lancées par la base de données SQL lorsqu'elle rencontre une erreur interne au lieu d'exposer des informations sensibles sur la table :

```python
@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "Database error while handling %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Une erreur interne est survenue. Réessayez plus tard."
        },
    )
```

Voilà pour cette partie du projet. Vous pouvez consulter la [Vidéo 4: Processus du Onboarding](https://www.youtube.com/watch?v=sD8Af65OU6c) pour les explications en lien avec la structure du frontend.

Les prochains articles s'attarderont à la suite du développement du frontend, où je configure Axios pour les services d'API et où j'automatise la synchronisation des endpoints entre le backend et le frontend avec OpenAPI et Orval.
