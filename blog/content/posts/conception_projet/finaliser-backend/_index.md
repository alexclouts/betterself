{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

1. Parler des tests d'intégration.
2. Service de On Boarding pour vérifier que l'utilisateur l'a terminé et mettre a jour les données dans les tables.
3. L'enjeu de travailler avec l'IA: Exemple de contre-vérification du code - screenshot1
4. Gestion de l'opération commit() dans ma base de données.

#### _Question :_ Je crois avoir fait le tour des fonctionnalités principales. Maintenant j'ai un questionnement concernant le processus end-to-end de l'application. Une des vérifications qui pourrait être fait pour valider que l'utilisateur a bien complété le processus de on boarding en entier est de valider que l'utilisateur a une entrée dans la table nutrition-goal. Maintenant, de quelle façon me suggères-tu d'effectuer cette vérification?

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

# Restructuration des fichiers

En travaillant sur le service de _OnBoarding_, je me suis mis à reconsidérer certains aspects de mon architecture. Je trouvais que l'utilisation du mot `service` était peut-être inapproprié pour certains cas d'usage. J'ai donc voulu corriger cette confusion avant d'aller plus loin dans le projet.

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

# Les erreurs contextuelles de l'IA

Je me suis rendu compte que l'IA me génère du travail puisqu'elle oublie les conversations précédentes. Ce genre de problème est ce qui rend important mon rôle de contre-vérificateur du code qu'elle propose. Par exemple, c'est le cas pour l'implémentation suivante qui m'a été suggéré. Bien que l'IA m'ait aidé à concevoir la table `measurements`, elle assume qu'un paramètre `height_cm` s'y trouve alors que ce n'est pas le cas, ce qui va générer un message d'erreur lors de la compilation.

{{< img
src="screenshot1.png"
alt="Screenshot"
caption=""
width="800">}}

# La gestion des opérations commit

En analysant le code que l'IA m'a suggéré pour l'implémentation du service de Onboarding, j'ai réalisé que l'opération `commit()` n'était pas présente dans les fonctions visant à sauvegarder les données transmises par le frontend. En discutant avec l'IA, elle a offert un raisonnement intéressant :

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

Mon implémentation actuelle effectue les opérations `commit` directement dans les fonctions de repositories. J'ai donc apporté les modifications pour refléter ce changement.

### Le rôle de `flush`

En exécutant mes tests unitaires, je me suis rendu compte que des erreurs étaient générées :

```
E               fastapi.exceptions.ResponseValidationError: 2 validation errors:
E                 {'type': 'uuid_type', 'loc': ('response', 'id'), 'msg': 'UUID input should be a string, bytes or UUID object', 'input': None}
E                 {'type': 'bool_type', 'loc': ('response', 'is_active'), 'msg': 'Input should be a valid boolean', 'input': None}
E
E                 File "/home/alex/Documents/betterself/backend/src/betterself/routers/auth_router.py", line 35, in register_user
E                   POST /auth/register
```

#### Les explications de l'IA

Avec `flush()`, SQLAlchemy applique les valeurs par défaut Python — `generate_uuid` et `True` — puis envoie l’`INSERT` dans la transaction. L’objet `user` possède donc immédiatement :

```
user.id        # UUID valide
user.is_active # True
```

Le `commit()` reste toutefois responsable de rendre l’insertion permanente.
