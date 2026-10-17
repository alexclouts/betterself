# ADR: Choix de l’organisation du code

## Contexte

Nous devons
décider comment organiser le code afin de séparer clairement les responsabilités. L’organisation du code doit permettre de :

- séparer l’interface utilisateur de la logique métier
- séparer la logique métier de l’accès aux données
- regrouper le code par domaine
- faciliter les tests unitaires et les tests d’API
- ajouter de nouvelles fonctionnalités sans modifier l’ensemble du projet
- garder une structure simple adaptée à la taille du projet

## Options considérées

- Code unique, sans séparation des responsabilités
- Organisation par type de fichier
- Architecture en couches organisée par domaine

## Décision

Nous utiliserons une **architecture en couches organisée par domaine**.

Le frontend React sera organisé autour de composants de présentation, de hooks personnalisés et de services d’appel à l’API. Le backend FastAPI sera organisé en routes, schémas Pydantic, services et repositories.

### Organisation du frontend React

```text
frontend/src/
├── components/
│   ├── WeightForm.jsx
│   ├── WeightChart.jsx
│   └── NutritionGoalCard.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useWeightMeasurement.js
│   └── useNutritionGoals.js
├── services/
│   ├── apiClient.js
│   ├── measurementService.js
│   └── nutritionService.js
├── pages/
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   └── WeightPage.jsx
└── App.jsx
```

Les composants de présentation afficheront les données et déclencheront des événements. Les hooks personnalisés géreront l’état local, la validation d’affichage et les appels à l’API. Les services regrouperont les requêtes HTTP vers le backend FastAPI.

### Organisation du backend FastAPI

```text
backend/app/
├── users/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── repository.py
├── measurements/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── repository.py
├── nutrition/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── repository.py
├── foods/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── repository.py
└── main.py
```

Les routes recevront les requêtes HTTP et appelleront les services. Les schémas Pydantic valideront les données entrantes et sortantes. Les services contiendront la logique métier, comme le calcul du métabolisme de repos ou la vérification des objectifs. Les repositories isoleront l’accès à la base de données.

## Avantages

- **Séparation claire des responsabilités.** Chaque couche a un rôle précis : l’interface affiche les données, les hooks gèrent l’état et les appels API, les routes reçoivent les requêtes, les services appliquent la logique métier et les repositories accèdent à la base de données.

- **Code facile à maintenir.** Les fonctionnalités sont regroupées par domaine. Par exemple, toutes les modifications liées aux mesures corporelles seront concentrées dans le module `measurements`, ce qui réduira le risque de modifier accidentellement d’autres parties de l’application.

- **Meilleure testabilité.** Les services backend pourront être testés indépendamment des routes et de la base de données. Les hooks React pourront également être testés séparément des composants visuels.

- **Réutilisation du code.** Les composants React, les hooks et les services pourront être réutilisés dans plusieurs pages. Par exemple, un hook `useAuth` pourra servir à la connexion, à la protection des pages et à la récupération du profil utilisateur.

- **Évolutivité.** De nouveaux domaines pourront être ajoutés sans restructurer l’ensemble du projet. Si l'application ajoute des fonctionnalités supplémentaires, chacune pourra devenir un module distinct.

- **Cohérence frontend et backend.** La séparation entre présentation, logique métier et accès aux données reflète la séparation entre React, FastAPI et PostgreSQL.

## Inconvénients

- **Plus de fichiers et de dossiers.** Cette organisation demande de créer plusieurs fichiers pour une même fonctionnalité, par exemple un routeur, un schéma, un service et un repository.

- **Risque de sur-ingénierie.** Pour un petit projet, une séparation trop rigide peut ralentir le développement. Il faudra donc éviter de créer des couches ou des abstractions inutiles.

- **Coordination nécessaire entre les couches.** Une modification du modèle de données peut nécessiter des changements dans le schéma Pydantic, le service, le repository, le hook React et le composant d’affichage.

## Alternatives rejetées

### Code unique sans séparation

Cette approche consisterait à placer la logique d’interface, les appels API, les règles métier et l’accès à la base de données dans un nombre limité de fichiers. Elle serait plus rapide au début, mais deviendrait difficile à maintenir lorsque l'application comprendra plusieurs domaines fonctionnels.

Elle a été rejetée parce qu’elle rendrait les tests plus difficiles et augmenterait le risque de duplication du code.

### Organisation par type de fichier

Cette approche consisterait à regrouper tous les contrôleurs, tous les modèles, tous les services et tous les repositories dans des dossiers séparés, sans les associer à un domaine fonctionnel.

Elle peut convenir à de petits projets, mais elle rend plus difficile la localisation de toutes les parties d’une fonctionnalité. Il est plus clair de regrouper les fichiers liés aux utilisateurs, aux mesures ou à la nutrition dans des modules distincts.

## Conclusion

Nous utiliserons une architecture en couches organisée par domaine fonctionnel. Cette organisation permettra de séparer l’interface utilisateur, l’état de présentation, la logique métier, l’accès aux données et la persistance.

Côté React, les composants de présentation seront séparés des hooks personnalisés et des services d’appel à l’API. Côté FastAPI, les routes, les schémas Pydantic, les services et les repositories auront des responsabilités distinctes. Cette structure correspond bien à la taille actuelle de BetterSelf, tout en facilitant l’ajout progressif de nouvelles fonctionnalités.
