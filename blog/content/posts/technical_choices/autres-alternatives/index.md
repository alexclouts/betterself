---
title: "Quoi d'autre ?"
header: ""
date: 2026-09-25T08:45:00.000Z
description: "Les principales technologies envisagées avant de retenir React, FastAPI et la base de données SQL."
tags:
  - Alternative
  - NoSQL
categories:
  - Fondations
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="600">}}

## Frontend

### Application native Android (Kotlin/Java)

L'utilisation de Kotlin, en particulier la technologie Kotlin Multiplatform est une solution intéressante. Pour l'avoir déjà utilisé dans le passé, elle est très complexe à mettre en place et récente. Certaines librairies ne sont pas encore compatibles avec cette technologie, ce qui exige une double implémentation (soit en Kotlin pour Android et en Swift pour iOs). Dans le cadre du travail, on nous demande de concevoir une application Web, et cette solution ne répond pas à ce critère, ce pourquoi elle n'a pas été envisagée plus sérieusement.

### Vue.js

Pour avoir déjà entendu parler de React, j'avais déjà un intérêt à utiliser ce framework avant même de considérer les alternatives. Après m'être renseigné davantage, j'ai su que Vue.js serait une alternative intéressante pour ce projet. Par contre, je conserve mon choix initial puisqu'il est très répandu au sein de la communauté et qu'il y a une abondance de ressources et d'exemples d'utilisation pour un projet comme celui-ci.

## Backend

### Node.js (Express / NestJS)

Cette alternative aurait été intéressant pour avoir un seul langage (JavaScript/TypeScript) à la fois pour le frontend et le backend. Cependant, je crois que mes connaissances actuelles en Python me permettront de comprendre, d'écrire et de déboguer plus facilement le code utilisé pour construire la logique de l'application. La courbe d'apprentissage sera moins prononcée lors de son développement.

### Django

Ce framework Python est très complet (ORM, authentification, admin, etc.) et offre des fonctionnalités plus avancées que FastAPI. Malgré cela, mon choix a été fait en tenant compte de la grande flexibilité offerte par FastAPI, par le biais d'**interactions en temps réel** avec des fonctionnalités via des `WebSockets`. D'ailleurs, l'option choisie est également plus facile à apprendre et à intégrer que Django, bien que ce dernier soit plus mature et mieux documenté. Dans le contexte où FastAPI aura une architecture frontend/backend séparée, la flexibilité de FastAPI est une priorité selon moi.

Source: https://blog.jetbrains.com/pycharm/2023/12/django-vs-fastapi-which-is-the-best-python-web-framework/

### Flask

`Flask` est également une alternative très simple et légère. J'ai choisi FastAPI puisque la validation des données et la documentation interactive de l’API répondent directement à mes besoins : je devrai définir clairement les données échangées entre React et le backend, puis tester mes routes pendant le développement. Avec Flask, la gestion des extensions et des librairies peut devenir laborieuse lorsque l'application augmente en complexité et que plusieurs fonctionnalités doivent être ajoutées.

## Base de données

### Base de données NoSQL (MongoDB)

Une base de données `NoSQL`, comme `MongoDB`, pourrait stocker les informations sous forme de **documents**. Cependant, SQL correspond très bien aux données utilisées par mon application, comme mentionné dans une autre publication. Par exemple, un utilisateur enregistre des aliments et des repas à des moments spécifiques, plusieurs aliments peuvent composer un repas, etc. Le modèle relationnel facilite la création de ces liens et le calcul des bilans alimentaires. Dans une base de données NoSQL, les requêtes d'agrégation sont plus complexes à mettre en place.

### PostgreSQL dès le Jour 1

PostgreSQL est une autre possibilité parmi les bases SQL. Je ne l’écarte pas, mais son utilisation dès le début du projet nécessite la configuration et l’hébergement d’un serveur de base de données, ce qui augmente rapidement la complexité du projet. Je préfère commencer avec SQLite pour développer et tester les premières fonctionnalités de l'application et réévaluer ce choix avant le déploiement. Je devrai également vérifier que l’hébergement choisi offre un stockage persistant pour conserver l'historique des utilisateurs d'une session à l'autre.

[Retour](https://alexclouts.github.io/betterself/posts/)
