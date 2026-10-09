# Modèle de données — Better Self

Ce document porte décrit le modèle de conception utilisé pour la version 1.0. Il décrit les données que l’application prévoit gérer ainsi que les relations qui relient les différentes structures de données.

## 1. Objectif

Ce modèle porte sur les comptes utilisateurs, les profils nécessaires aux calculs nutritionnels, l’historique du poids, les objectifs, les aliments, les recettes composées et le journal alimentaire. Les photos de progression, le suivi des entraînements, le partage public avancé d’aliments et les résumés quotidiens pré-calculés sont reportés à une version ultérieure.

Le modèle aborde les concepts suivants :

- **Objectif nutritionnel (`nutrition_goals`)** : intention à moyen ou long terme, comme perdre du poids ou maintenir son poids.
- **Cible nutritionnelle (`goal_targets`)** : recommandations de calories et de macronutriments valables pendant une période donnée.
- **Aliment (`foods`)** : aliment de référence avec des valeurs nutritionnelles normalisées.
- **Recette (`recipes`)** : composition d'aliments réutilisable appartenant à un utilisateur.
- **Consommation (`food_consumptions`)** : aliment ou recette consommé à un moment précis.

## 2. Relations principales

```text
users 1 ─── 1 user_profiles
users 1 ─── N body_measurements
users 1 ─── N nutrition_goals
nutrition_goals 1 ─── N goal_targets
users 1 ─── N recipes
recipes 1 ─── N recipe_ingredients N ─── 1 foods
users 1 ─── N food_consumptions
food_consumptions N ─── 0..1 foods
food_consumptions N ─── 0..1 recipes
```

Pour résumé, chaque consommation fait référence à un aliment ou une recette. Une recette contient plusieurs ingrédients; un aliment peut apparaître dans plusieurs recettes.

## 3. Conventions

- Les identifiants sont des UUID.
- Les clés étrangères assurent la cohérence des relations.
- Les poids sont en kilogrammes pour les mesures corporelles et en grammes pour les aliments et recettes.
- Les valeurs nutritives sont en kcal ou en grammes selon leur nom.
- `TIMESTAMPTZ` sert aux instants précis; `DATE` sert aux dates civiles sans heure.
- `NUMERIC` est privilégié pour les quantités décimales et les valeurs nutritionnelles.
- Les valeurs nutritionnelles de `foods` sont exprimées par quantité de référence, normalement 100 g.
- Les colonnes `*_snap` dans le journal conservent l’état affiché au moment de la consommation, même si l’aliment ou la recette change ensuite.

## 4. Tables

### 4.1 `users` — authentification de l'utilisateur

Cette table contient uniquement les données nécessaires au compte. Le mot de passe n’est jamais stocké en clair : `password_hash` contient un hash produit par une fonction adaptée au stockage des mots de passe.

| Champ           | Type suggéré | Contraintes et description                                               |
| --------------- | ------------ | ------------------------------------------------------------------------ |
| `id`            | UUID         | Clé primaire                                                             |
| `email`         | VARCHAR(255) | Obligatoire, unique; normaliser la casse selon la stratégie de connexion |
| `password_hash` | TEXT         | Obligatoire; hash du mot de passe                                        |
| `created_at`    | TIMESTAMPTZ  | Obligatoire, date de création                                            |
| `updated_at`    | TIMESTAMPTZ  | Obligatoire, dernière modification                                       |

### 4.2 `user_profiles` — profil utilisateur

Informations utilisées pour personnaliser les calculs et l’expérience. Le profil est séparé du compte d’authentification.

| Champ            | Type suggéré | Contraintes et description                                  |
| ---------------- | ------------ | ----------------------------------------------------------- |
| `user_id`        | UUID         | Clé primaire et clé étrangère vers `users.id`; relation 1:1 |
| `first_name`     | VARCHAR(100) | Facultatif, prénom d’affichage                              |
| `year_of_birth`  | SMALLINT     | Année seulement pour mesurer le BMR                         |
| `sex`            | VARCHAR(1)   | Valeur requise par la formule BMR retenue; M, F ou X        |
| `height_cm`      | NUMERIC(5,2) | Taille en centimètres                                       |
| `activity_level` | VARCHAR(30)  | Niveau d’activité sélectionné; valeurs admises à définir    |
| `updated_at`     | TIMESTAMPTZ  | Date de mise à jour                                         |

L’âge est calculé depuis l’année de naissance et l’année courante; il n’est pas conservé comme valeur fixe, puisqu'il faudrait la mettre à jour.
Le poids courant est obtenu à partir de la dernière mesure de `body_measurements`, et non de ce profil.

### 4.3 `body_measurements` — historique du poids

Une ligne correspond à une mesure réelle. Cette table permet de représenter l’évolution du poids sans écraser les mesures précédentes.

| Champ         | Type suggéré | Contraintes et description                 |
| ------------- | ------------ | ------------------------------------------ |
| `id`          | UUID         | Clé primaire                               |
| `user_id`     | UUID         | Clé étrangère vers `users.id`, obligatoire |
| `weight_kg`   | NUMERIC(5,2) | Obligatoire, strictement supérieur à zéro  |
| `measured_at` | TIMESTAMPTZ  | Moment de la mesure                        |
| `created_at`  | TIMESTAMPTZ  | Moment d’enregistrement                    |

Les photos associées aux mesures ne seront pas incluses dans la version 1.0.

### 4.4 `nutrition_goals` — objectif général

Cette table décrit l’objectif de l’utilisateur sur une période. Une nouvelle mesure de poids entraîne un recalcul des cibles associées à l’objectif actif, sans définir un nouvel objectif en soi.

| Champ                | Type suggéré           | Contraintes et description                                     |
| -------------------- | ---------------------- | -------------------------------------------------------------- |
| `id`                 | UUID                   | Clé primaire                                                   |
| `user_id`            | UUID                   | Clé étrangère vers `users.id`, obligatoire                     |
| `goal_type`          | VARCHAR(30)            | Par exemple `weight_loss`, `muscle_gain` ou `maintenance`      |
| `starting_weight_kg` | NUMERIC(5,2)           | Poids de référence au début de l’objectif                      |
| `target_weight_kg`   | NUMERIC(5,2), nullable | Poids visé; peut être nul pour un objectif sans cible de poids |
| `start_date`         | DATE                   | Date de début                                                  |
| `target_date`        | DATE, nullable         | Date visée; peut être nulle pour un objectif sans échéance     |
| `status`             | VARCHAR(20)            | Par exemple `active`, `completed`, `cancelled`                 |
| `created_at`         | TIMESTAMPTZ            | Date de création                                               |
| `updated_at`         | TIMESTAMPTZ            | Date de modification                                           |

La recomposition corporelle et le suivi des entraînements ne sont pas inclus dans la version 1.0.

### 4.5 `goal_targets` — cibles nutritionnelles évolutives

Cette table conserve les recommandations nutritionnelles en cours. Lorsque le poids ou une autre donnée pertinente change, une nouvelle ligne peut être créée et l’ancienne conservée pour l’historique.

| Champ                       | Type suggéré   | Contraintes et description                                      |
| --------------------------- | -------------- | --------------------------------------------------------------- |
| `id`                        | UUID           | Clé primaire                                                    |
| `goal_id`                   | UUID           | Clé étrangère vers `nutrition_goals.id`, obligatoire            |
| `valid_from`                | DATE           | Début de validité, obligatoire                                  |
| `valid_until`               | DATE, nullable | Fin de validité; nul signifie que la période est encore ouverte |
| `reference_weight_kg`       | NUMERIC(5,2)   | Poids utilisé pour le calcul                                    |
| `maintenance_calories_kcal` | INTEGER        | Estimation des calories de maintien                             |
| `calorie_target_kcal`       | INTEGER        | Apport quotidien cible                                          |
| `calorie_adjustment_kcal`   | INTEGER        | Écart par rapport au maintien                                   |
| `protein_target_g`          | NUMERIC(6,2)   | Cible quotidienne de protéines                                  |
| `carbs_target_g`            | NUMERIC(6,2)   | Cible quotidienne de glucides                                   |
| `fat_target_g`              | NUMERIC(6,2)   | Cible quotidienne de lipides                                    |
| `calculation_method`        | VARCHAR(50)    | Formule ou méthode utilisée                                     |
| `created_at`                | TIMESTAMPTZ    | Date de création de la cible                                    |

Validation : assurer que `valid_until` est NULL ou plus grand que `valid_from`. L’application devrait éviter deux cibles simultanément valides pour un même objectif.

### 4.6 `foods` — aliments et nutrition de référence

Pour la version 1.0, l’identité de l’aliment et son profil nutritionnel sont réunis dans une table afin de conserver un modèle simple. Les nutriments et les calories sont rapportés à `reference_weight_g`, généralement 100 g.

| Champ                | Type suggéré           | Contraintes et description                                            |
| -------------------- | ---------------------- | --------------------------------------------------------------------- |
| `id`                 | UUID                   | Clé primaire                                                          |
| `name`               | VARCHAR(255)           | Nom obligatoire                                                       |
| `description`        | TEXT, nullable         | Description ou précision                                              |
| `category`           | VARCHAR(100), nullable | Catégorie, par exemple fruit ou céréale                               |
| `reference_weight_g` | NUMERIC(8,2)           | Quantité nutritionnelle de référence, supérieure à zéro               |
| `calories_kcal`      | NUMERIC(8,2)           | Calories pour la quantité de référence                                |
| `protein_g`          | NUMERIC(8,2)           | Protéines pour la quantité de référence                               |
| `carbohydrates_g`    | NUMERIC(8,2)           | Glucides pour la quantité de référence                                |
| `fat_g`              | NUMERIC(8,2)           | Lipides pour la quantité de référence                                 |
| `source`             | VARCHAR(100), nullable | Source des données                                                    |
| `external_reference` | VARCHAR(255), nullable | Identifiant dans la source externe                                    |
| `created_by_user_id` | UUID, nullable         | Clé étrangère vers `users.id` pour un aliment créé par un utilisateur |
| `created_at`         | TIMESTAMPTZ            | Date de création                                                      |
| `updated_at`         | TIMESTAMPTZ            | Date de modification                                                  |

La validation de la propriété d'un aliment et l’accès aux aliments privés se fait côté API pour assurer une sécurité accrue. Le partage public est reporté à une version ultérieure.

### 4.7 `recipes` — recettes de l’utilisateur

Contient les informations générales d’une recette. Une recette archivée reste conservée et peut rester consultable dans les anciennes entrées du journal.

| Champ            | Type suggéré           | Contraintes et description                  |
| ---------------- | ---------------------- | ------------------------------------------- |
| `id`             | UUID                   | Clé primaire                                |
| `user_id`        | UUID                   | Clé étrangère vers `users.id`, propriétaire |
| `name`           | VARCHAR(255)           | Nom obligatoire                             |
| `description`    | TEXT, nullable         | Description ou instructions                 |
| `total_weight_g` | NUMERIC(10,2)          | Poids préparé, supérieur à zéro             |
| `servings`       | NUMERIC(6,2), nullable | Nombre de portions, si renseigné            |
| `is_archived`    | BOOLEAN                | Masquer des choix courants sans supprimer   |
| `created_at`     | TIMESTAMPTZ            | Date de création                            |
| `updated_at`     | TIMESTAMPTZ            | Date de modification                        |

### 4.8 `recipe_ingredients` — aliments composant une recette

Table de liaison entre les recettes et les aliments. Elle permet à une recette de contenir plusieurs aliments et à un aliment d’être utilisé dans plusieurs recettes.

| Champ        | Type suggéré  | Contraintes et description                       |
| ------------ | ------------- | ------------------------------------------------ |
| `id`         | UUID          | Clé primaire                                     |
| `recipe_id`  | UUID          | Clé étrangère vers `recipes.id`, obligatoire     |
| `food_id`    | UUID          | Clé étrangère vers `foods.id`, obligatoire       |
| `quantity_g` | NUMERIC(10,2) | Quantité utilisée, strictement supérieure à zéro |
| `created_at` | TIMESTAMPTZ   | Date d’ajout                                     |

La suppression d’une recette entraînera la suppression des lignes d’ingrédients en cascade. Pour cette raison, l'archivage est une option plus sûr. Un aliment ne devrait pas être supprimé physiquement sans traiter les recettes qui le référencent non plus.

### 4.9 `food_consumptions` — entrées du journal alimentaire

Une ligne représente un aliment ou une recette consommée. Le nom et les nutriments sont conservés sous forme de _snapshot_ pour que l’historique ne change pas si la ressource est modifiée ultérieurement.

| Champ                | Type suggéré   | Contraintes et description                                                               |
| -------------------- | -------------- | ---------------------------------------------------------------------------------------- |
| `id`                 | UUID           | Clé primaire                                                                             |
| `user_id`            | UUID           | Clé étrangère vers `users.id`, obligatoire                                               |
| `food_id`            | UUID, nullable | Clé étrangère vers `foods.id` si aliment simple                                          |
| `recipe_id`          | UUID, nullable | Clé étrangère vers `recipes.id` si recette                                               |
| `item_name_snapshot` | VARCHAR(255)   | Nom affiché au moment de la consommation                                                 |
| `quantity_g`         | NUMERIC(10,2)  | Quantité consommée, supérieure à zéro                                                    |
| `calories_kcal`      | NUMERIC(8,2)   | Calories de la quantité consommée                                                        |
| `protein_g`          | NUMERIC(8,2)   | Protéines consommées                                                                     |
| `carbohydrates_g`    | NUMERIC(8,2)   | Glucides consommés                                                                       |
| `fat_g`              | NUMERIC(8,2)   | Lipides consommés                                                                        |
| `meal_type`          | VARCHAR(30)    | Type de repas; valeurs admises à définir, par exemple déjeuner, dîner, souper, collation |
| `consumed_at`        | TIMESTAMPTZ    | Date et heure de consommation                                                            |
| `notes`              | TEXT, nullable | Note facultative                                                                         |
| `created_at`         | TIMESTAMPTZ    | Date de création de l’entrée                                                             |
| `updated_at`         | TIMESTAMPTZ    | Date de modification                                                                     |

Contrainte essentielle : seul l'un ou l'autre de `food_id` ou `recipe_id` doit être présent. Les valeurs nutritionnelles enregistrées correspondent à `quantity_g`, et non aux valeurs de référence. Elles sont calculées au moment de l’ajout ou de la modification de l’entrée, puis conservées comme instantané pour les protéger des modifications ultérieures.

## 5. Calculs et journal quotidien

Pour calculer l'apport en nutriments pour un aliment dont les valeurs sont exprimées par quantité de référence (100 g par exemple), on effectue un produit croisé :

```text
nutriment consommé = nutriment de référence × quantité consommée / quantité de référence
```

Pour une recette, l’application additionne les nutriments des ingrédients selon leurs quantités, puis calcule la portion consommée selon le poids de la recette. Le résultat calculé est copié dans `food_consumptions`.

Le journal d’une journée est obtenu en filtrant `food_consumptions` par utilisateur et par intervalle de temps, puis en triant par `consumed_at`.

### 5.1 Calcul des totaux

Les totaux quotidiens (calories et macronutriments) sont calculés par agrégation sur ces entrées (une table de résumé qui précalcule les totaux n’est pas nécessaire pour la première version).

Pour faire cette lecture, on pourra créer un index:

```sql
CREATE INDEX idx_food_consumptions_daily_journal
    ON food_consumptions (user_id, consumed_at, id);
```

Il faut transmettre un intervalle quotidien pour récupérer les données de consommation, qui sera calculé selon le fuseau horaire de l'utilisateur.

## 6. Règles d’intégrité importantes

- `users.email` doit être unique.
- Les valeurs de poids et de quantité doivent être strictement positives.
- Les quantités et nutriments ne doivent pas être négatifs.
- Une consommation référence exactement un aliment ou une recette, jamais les deux.
- Les dates de validité d’une cible doivent être cohérentes.
- Les utilisateurs peuvent uniquement consulter ou modifier leurs propres profils, mesures, objectifs, recettes et entrées de journal; ces contrôles sont appliqués côté **serveur**.
- Les valeurs instantanées du journal ne sont pas recalculées lorsque les données de référence changent.

## 7. Évolutions possibles

Les besoins suivants pourront faire évoluer le modèle :

- Créer `food_servings` pour offrir de choisir des portions en unités courantes (une pomme, une tasse, etc.)
- `progress_photos` pour associer des fichiers aux mesures corporelles
- Une section qui effectue le suivi des entraînements pour mesurer la recomposition corporelle
- Des résumés quotidiens pré-calculés, si besoin il y a
- Des sessions ou des jetons de renouvellement si le processus d’authentification les exige.
