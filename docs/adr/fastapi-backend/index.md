# ADR: Choix d'un backend FastAPI

## Contexte

Nous devons choisir une architecture afin de gérer l’authentification des utilisateurs, l’interaction avec le REST API et le traitement des requêtes de l’interface utilisateur.

Notre application nécessite un backend capable de recevoir les requêtes du frontend React, de valider les données saisies par l’utilisateur, d’appliquer la logique métier et de communiquer avec une base de données relationnelle. Le backend devra notamment gérer les comptes utilisateurs, les mesures corporelles, les objectifs nutritionnels, les aliments et les consommations alimentaires.

Il devra également permettre d’interroger l’API externe Open Food Facts afin de récupérer des informations nutritionnelles.

## Options considérées

- Node.js
- Django
- Flask
- FastAPI

## Décision

FastAPI est l'architecture Python choisie pour implémenter le backend.

FastAPI sera responsable de la définition des endpoints REST, de la validation des données entrantes avec Pydantic, de l’application de la logique métier, de l’accès à la base de données et de la sérialisation des réponses en JSON.

Le frontend React communiquera avec FastAPI par des requêtes HTTP. FastAPI recevra les données, les validera, appliquera les règles métier nécessaires, puis retournera une réponse au format JSON.

## Avantages

1. **Validation des données intégrée.** Pydantic est une bibliothèque Python utilisée par FastAPI qui facilite la validation de données complexes. Elle permet de prédéfinir la structure des données entrantes.

2. **Performance asynchrone.** FastAPI repose sur Starlette et supporte la programmation asynchrone, ce qui la rend adaptée aux API qui gèrent plusieurs requêtes simultanément.

3. **Documentation automatisée.** Les _type hints_ et Pydantic génèrent automatiquement la documentation de l'API.

4. **Facilité d'intégration.** FastAPI est plus simple à intégrer que ses alternatives, surtout pour un projet centré sur des requêtes API.

5. **Tests.** FastAPI peut être testé avec _pytest_ et _TestClient_. Cela permettra de vérifier le comportement des endpoints, la validation des données et la logique métier sans devoir tester manuellement chaque fonctionnalité dans l’interface.

## Inconvénients

1. **Fonctionnalités limitées.** Certaines composantes (système d'authentification, panneau d'administration, ORM) ne sont pas incluses dans l'architecture.

2. **Dépendance à des bibliothèques externes.** L'absence de certaines fonctionnalités requiert de recourir à des bibliothèques externes en lien avec la gestion des données et l'authentification des utilisateurs.

3. **Moins de guidance offerte.** FastAPI offre une bonne documentation, mais elle présente moins de directives entourant l'architecture (organisation des routes, services, répertoires et schémas).

4. **Sécurité à implémenter.** L’authentification, l’autorisation et la protection des données personnelles ne sont pas fournies automatiquement. Le backend devra hacher les mots de passe, émettre et valider des jetons d’authentification, puis s’assurer qu’un utilisateur ne peut accéder qu’à ses propres données.

## Alternatives rejetées

### Django

Django est un framework Python complet qui inclut plusieurs fonctionnalités prêtes à l’emploi, telles qu’un ORM, un système d’authentification, un panneau d’administration et un moteur de gabarits. Ces fonctionnalités auraient pu accélérer le développement de certaines parties de BetterSelf.

Cependant, Django est plus lourd et plus structuré que nécessaire pour un projet centré sur une API REST. L'application utilisera React pour le frontend et n’aura donc pas besoin d’un moteur de gabarits ou d’un panneau d’administration intégré. Django aurait aussi imposé davantage de conventions et de configuration pour une application dont le besoin principal est d’exposer une API REST/JSON.

### Flask

Flask est un micro-framework Python léger et flexible. Il aurait permis de créer un backend minimal sans imposer une structure particulière au projet.

Flask ne fournit pas nativement de validation de données aussi intégrée que Pydantic, ni de documentation d’API générée automatiquement. Il aurait fallu ajouter plusieurs extensions pour la validation, la documentation, l’authentification et l’accès à la base de données. FastAPI offre ces fonctionnalités de façon plus cohérente et mieux intégrée, tout en restant léger.

### Node.js

Node.js aurait permis d’utiliser JavaScript à la fois pour le frontend React et le backend. Cette option aurait pu simplifier le partage de certains types ou utilitaires entre les deux parties de l’application.

Toutefois, elle est moins cohérente avec les outils Python déjà envisagés pour le projet, notamment Pydantic, SQLAlchemy et pytest. De plus, elle n’offre pas nativement la validation structurée des données ni la documentation automatique de l’API. FastAPI correspond mieux à nos besoins, qui reposent sur la validation rigoureuse des données de santé et nutritionnelles.

## Conclusion

FastAPI est l'architecture choisie pour le backend. Malgré ses fonctionnalités limitées, son intégration intuitive et la validation de données avec Pydantic sont des avantages adaptés aux besoins de l'application.
