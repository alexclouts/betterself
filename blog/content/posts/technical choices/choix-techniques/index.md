---
title: "On se lançe !"
header: ""
date: 2026-09-25T08:35:00.000Z
description: "Présentation des choix du framework et des technologies frontend / backend."
tags:
  - Frontend
  - Backend
  - Architecture
  - Validation
categories:
  - Cadrage et recherche
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="600">}}

## Frontend : Pourquoi React et PWA ?

Le premier choix technologique important concerne l'interface utilisateur de `BetterSelf`. J’ai choisi d’utiliser **React**, une bibliothèque _JavaScript_ très répandue pour construire des interfaces web interactives. L'un de ses principaux avantages est son modèle basé sur des composants. Une interface comme celle de notre application peut être divisée en plusieurs éléments indépendants: recherche d'aliments, lecteur de code-barres, journal alimentaire, objectifs nutritionnels, tableau de bord, etc. Ces composants peuvent ensuite être réutilisés à différents endroits de l'application. React offre également un vaste éventail de bibliothèques et une grande quantité d'explications et d'exemples. Comme il s'agit d'une technologie très répandue, il sera relativement facile de trouver de l'information lorsque je rencontrerai un problème pendant le développement.

Cette technologie, combinée avec l'approche des **PWA** (Progressive Web App), permettra à l'application de se comporter comme s'il s'agissait d'une application native. L'utilisateur pourra donc utiliser ses fonctionnalités à partir de son téléphone cellulaire directement sans avoir à se connecter à une interface Web à chaque fois.

### Un frontend partagé

Un autre avantage important du choix de ces technologies est la possibilité d'utiliser la même application sur ordinateur, tablette et téléphone. L'ordinateur restera particulièrement utile pour le développement et les tests, tandis que le téléphone constituera probablement le principal appareil utilisé par les utilisateurs afin de consigner les aliments au quotidien. Le choix d'une application Web permet donc de cibler ces différentes plateformes sans devoir maintenir plusieurs applications natives.

### Coûts et distribution

Une autre motivation derrière ce choix est de limiter la dépendance aux plateformes d'applications telles que `Google Play` et l'`App Store`. Une application native doit notamment respecter les exigences de ces plateformes, ce qui augmente la complexité de son développement. Avec une application Web, l'utilisateur peut simplement accéder au site à partir de son navigateur. PWA représente donc une alternative intéressante pour ces raisons.

## Backend : Pourquoi Python et FastAPI ?

Côté backend, j’ai choisi d'utiliser le language **Python**, combiné au framework **FastAPI**. D'abord, je suis déjà familié avec la syntaxe de Python pour l'avoir déjà utilisé au sein de divers projets. Je considère que la syntaxe est simple et bien adaptée à ce projet et à ses besoins en terme d'infrastructures. Python est également un language qui intègre bien des fonctionnalités clés de l'application, telles que la gestion des bases de données, l'authentification d'un utilisateur et les appels à des API externes (comme Open Food Facts dans notre cas).

Je ne suis pas encore familier avec FastAPI, mais j'ai tout de même choisi ce framework pour la construction d'un API Web afin d'acheminer les requêtes du frontend au bases de données intégrées. Selon mes recherches, cette technologie est facile à exécuter localement et à déployer dans un conteneur Docker. Afin de permettre la communication entre les différentes composantes de l'application, mon backend exposera des endpoints via le protocole HTTP. Voici des exemples de requête :

    `GET /api/foods?search=...` – rechercher des aliments;
    `GET /api/foods/by-barcode?barcode=...` – obtenir les infos d’un produit via son code-barres;
    `POST /api/consumptions` – enregistrer un aliment consommé;
    `GET /api/consumptions?date=...` – consulter l’historique d’une journée;
    `GET /api/goals, PUT /api/goals` – gérer les objectifs caloriques et protéiques.

### La structure de FastAPI

Le frontend ne communiquera donc pas directement avec la base de données. L'architecture de FastAPI sera donc séparée en plusieurs couches:

```text
Utilisateur
    ↓
React / PWA
    ↓ HTTP
FastAPI
    ↓
Logique de l'application
    ↓
Base de données
```

Cette séparation permet de centraliser la logique métier et les règles de validation dans le backend. Elle crée également une séparation nette entre le contrôle des interactions de l'utilisateur et la gestion des données.

## Validation avec Pydantic

FastAPI utilisera **Pydantic** pour définir et valider les données échangées avec l'API. Cet outil sera particulièrement utile puisque plusieurs types de données devront être transmis entre le frontend et le backend. Par exemple, quand un utilisateur enregistre une consommation, le backend devra vérifier que les informations reçues correspondent bien au format attendu. La validation côté serveur constitue également une protection importante: le frontend ne doit pas être considéré comme une source de données fiable simplement parce qu'il contrôle les champs présentés à l'utilisateur.

[Retour](http://localhost:1313/posts/)
