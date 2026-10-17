---
title: "Les choix de l'architecture"
header: ""
date: 2026-10-17T16:30:00.000Z
description: "Les décisions architecturales derrière BetterSelf : React, FastAPI, SQL et la séparation des responsabilités."
tags:
  - Architecture
  - React
  - FastAPI
  - SQL
categories:
  - Architecture et données
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Une architecture complète

Dans ma [publication précédente](https://alexclouts.github.io/betterself/posts/data-schema/), j’ai présenté la manière dont je souhaitais structurer les données de BetterSelf. J’y ai expliqué la séparation entre les utilisateurs, leurs profils, leurs mesures corporelles, leurs objectifs et leurs consommations alimentaires.

Au cours des dernières semaines, j'ai écrit plusieurs publications décrivant les raisons derrières l'architecture choisie pour la conception de ce projet. Vous pouvez consulter un résumé de ces choix sur [cette page](https://alexclouts.github.io/betterself/posts/technical_choices/architecture-globale/).

## L'organisation du code

La décision la plus importante que j’ai prise entoure l'organisation du code. Il consiste à séparer clairement le frontend du backend. Une explication plus exhausive de cette démarche se trouve dans la documentation [ADR: Choix de l’organisation du code](https://github.com/alexclouts/betterself/tree/main/docs/adr/code-organisation).

BetterSelf sera composé de trois parties principales.

```text
React (frontend)
    ↓ HTTP / JSON
FastAPI (backend)
    ↓
Base de données relationnelle SQL
```

React sera responsable de l’interface utilisateur, qui comprend les formulaires, les graphiques, les listes d’aliments et l’affichage des résultats. FastAPI exposera une API qui recevra les requêtes du frontend, validera les données, appliquera la logique métier et communiquera avec la base de données.

Cette séparation est importante parce que le frontend doit pouvoir afficher dynamiquement des informations comme le poids actuel, les calories consommées dans la journée ou les macronutriments d’un repas.

Une [architecture API-first](https://www.postman.com/api-first/) correspond donc bien à ce besoin.

### Une alternative rejetée : MVVM global

Au départ, j’envisageais d’utiliser MVVM comme architecture globale, puisque je l’avais déjà utilisée pour une application mobile. Toutefois, MVVM est surtout un patron de présentation. Il organise la relation entre une vue, son état et sa logique de présentation.

React ne propose pas de liaison de données native comme certains frameworks. Plutôt que de forcer une structure MVVM complète, j’ai choisi une approche plus naturelle pour React : **des composants de présentation et des hooks personnalisés**.

### Le contexte de cette décision

Le contexte de l'application a influencé plusieurs de mes choix. D'abord, l’application doit gérer des données provenant de plusieurs sources: poids, grandeur, année de naissance, objectifs caloriques et consommation alimentaire.

De plus, l’application devra interroger l’API Open Food Facts pour récupérer des informations nutritionnelles. Le backend doit donc pouvoir effectuer des requêtes externes, valider les données reçues et les intégrer au reste du système **sans exposer directement cette complexité au frontend**.

## React + FastAPI

Le choix de ces architectures a été expliqué dans ma publication portant sur [Mes choix techniques](https://alexclouts.github.io/betterself/posts/technical_choices/choix-techniques/), où je décris d'ailleurs ce qui les démarque des autres solutions.

Vous pouvez également retrouvé un comparatif de mon choix avec les alternatives que j'ai envisagé pour la conception de ce projet dans la documentation [ADR: Choix d'un frontend React](https://github.com/alexclouts/betterself/tree/main/docs/adr/react-frontend) et [ADR: Choix d'un backend FastAPI](https://github.com/alexclouts/betterself/tree/main/docs/adr/fastapi-backend).

React et FastAPI forment un combo gagnant pour BetterSelf parce qu’ils permettent une séparation claire entre l’interface et la logique métier. Le frontend envoie les requêtes, le backend applique les règles métier, interroge Open Food Facts et accède à la base SQL. Cette architecture découplée facilite les tests, la maintenance et l’évolution progressive de l’application.

## Python pour la victoire

Le choix de FastAPI entraîne naturellement le choix de Python comme langage backend. C'est ce pourquoi je n'ai pas envisagé d'autre alternative à ce choix technique. J'ai tout de même conçu une [ADR: Choix du language Python](https://github.com/alexclouts/betterself/tree/main/docs/adr/python-language) afin d'évaluer si ce language est véritablement adapté à mes besoins.

Python est adapté à BetterSelf parce qu’il est utilisé à la fois pour le développement Web, l’analyse de données et l’apprentissage machine. Sa syntaxe lisible facilite la maintenance du code, et son écosystème offre plusieurs bibliothèques pertinentes pour le projet.

## SQL pour la persistance

Pour la base de données, j’ai choisi une approche relationnelle SQL. Ce choix est d'ailleurs bien expliqué dans [cette publication](https://alexclouts.github.io/betterself/posts/technical_choices/choix-sql-hebergement/) portant sur les solutions d'hébergement.

Comme décrit plus haut, les données de l'application sont fortement structurées et liées entre elles. Un utilisateur possède un profil, plusieurs mesures corporelles, plusieurs objectifs et plusieurs consommations alimentaires. Une base relationnelle permet de représenter ces relations avec des clés primaires, des clés étrangères et des contraintes de validation.

### Alternatives rejetées

Comme expliqué dans ma publication portant sur [les alternatives](https://alexclouts.github.io/betterself/posts/technical_choices/autres-alternatives/), d'autres solutions ont d'ailleurs été envisagées. J’ai considéré MongoDB, mais je l’ai rejeté parce que les données de BetterSelf sont fortement relationnelles.

J’ai aussi envisagé Firebase, qui permettrait un déploiement rapide. Par contre, cette solution offre moins de contrôle sur le modèle relationnel et sur les requêtes complexes. Pour un projet où je souhaite comprendre et maîtriser l’architecture des données, une base SQL est plus appropriée.

## L’authentification avec JWT

Pour l’authentification, j’ai choisi des jetons JWT (JSON Web Tokens). Vous pouvez consulter mon [ADR: Choix d’une méthode d’authentification](https://github.com/alexclouts/betterself/tree/main/docs/adr/authentication).

Les explications plus complètes à ce sujet sont d'ailleurs abordé dans ma publication portant sur le [processus d'authentification](https://alexclouts.github.io/betterself/posts/authentication/).

Lorsqu’un utilisateur se connecte, le backend valide son courriel et son mot de passe. Si les identifiants sont corrects, FastAPI génère un jeton signé et le retourne au frontend. React conservera ensuite ce jeton et l’inclura dans les requêtes protégées.

## Un obstacle concret

L’obstacle de conception le plus concret que j’ai rencontré concernait le poids de l’utilisateur.

Au départ, il me semblait normal de **stocker le poids directement dans le profil utilisateur**, avec la grandeur et l'année de naissance. Toutefois, ces informations n’ont pas le même comportement dans le temps: le poids change fréquemment.

Si le poids était stocké uniquement dans `user_profiles`, chaque nouvelle pesée écraserait la précédente. L’application perdrait alors l’historique nécessaire pour afficher une progression, calculer une moyenne ou comparer le poids actuel avec l’objectif.

### La solution

J’ai résolu ce problème en créant une table `body_measurements`. Chaque mesure contient l’identifiant de l’utilisateur, la date et l’heure de la mesure, ainsi que le poids enregistré. Le poids actuel devient simplement la mesure la plus récente.

```text
body_measurements
-----------------
id
user_id
measured_at
weight_kg
```

Cette décision permet de conserver l’historique complet, d’afficher un graphique d’évolution et de recalculer les objectifs nutritionnels lorsqu’un nouveau poids est enregistré.

## Ce qui reste à faire

La prochaine étape sera de passer de la conception à l’implémentation. Je devrai créer la structure initiale du projet React et FastAPI, configurer la connexion à la base de données et implémenter les premiers endpoints liés à l’authentification et aux mesures corporelles.

Les décisions présentées dans cet article ne sont pas figées. Elles constituent toutefois une base pour développer l'application sans devoir réorganiser complètement le projet à chaque nouvelle fonctionnalité.

[Retour](https://alexclouts.github.io/betterself/posts/)
