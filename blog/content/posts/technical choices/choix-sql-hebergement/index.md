---
title: "Hébergement & stockage"
header: ""
date: 2026-09-25T08:40:00.000Z
description: "La stratégie d'hébergement et la base de données comme solution de stockage."
tags:
  - SQL
  - Hébergement
categories:
  - Cadrage et recherche
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="600">}}

## Pourquoi SQL?

Pour stocker les données locales (utilisateurs, aliments, repas, consommations, objectifs), j’ai choisi la base de données relationnelle (**SQL**). Une fois de plus, j'ai déjà utilisé cette technologie précédemment, donc je suis familié avec son fonctionnement et sa syntaxe pour effectuer le traitement de données. Le modèle relationnel comprend plusieurs avantages pour les cas d'utilisation de `BetterSelf`.

### Des données liées entre elles

D'abord, les informations à stocker sont naturellement liées. On y retrouve par exemple :

- les utilisateurs;
- les aliments;
- les repas;
- les consommations;
- les objectifs nutritionnels.

Ainsi, les aliments consommés par un utilisateur sont associés à une date précise et à un moment précis (déjeuner, dîner, souper, collation, etc.). Un repas peut contenir plusieurs aliments, et un aliment peut être consigné à plusieurs endroits. Une base relationnelle permet de représenter efficacement ces relations.

De plus, l'agrégation des données est également facile à réaliser depuis les requêtes SQL, ce qui permet de calculer le nombre de macronutriments ou de calories consommés quotidiennement. Son intégration avec Python est facile: plusieurs outils et bibliothèques existent déjà au sein de la communauté. Pour mon application, je compte utiliser `SQLAlchemy`, un logiciel gratuit et open-source qui offre un accès flexible aux fonctionnalités de SQL.

Un exemple de la structure de base de données qui pourrait se trouver au sein du projet:

```text
users
  │
  ├── goals
  │
  └── meals
        │
        └── consumptions
              │
              └── foods
```

## Comment BetterSelf sera-t-il hébergé?

Pour le choix d'hébergement, **Railway** est envisagé comme option d'hébergement provisoire du backend et du framework **FastAPI**. Le plan gratuit offre jusqu'à 0,5 Go d'espace disque par projet, permettant un hébergement à faible coût, et offre un support natif pour les applications Python. Cette plateforme permet également d'héberger la base de données dans le même environnement. Selon les besoins grandissants de l'application, il se pourrait que cette décision soit révisée ultérieurement. L'objectif est de maintenir les coûts aussi bas que possible pendant le développement tout en conservant une architecture qui pourra évoluer si l'application gagne des utilisateurs.

### Frontend: GitHub Pages

Pour ce qui est du frontend React, celui-ci sera hébergé sur `GitHub Pages` afin de minimiser les coûts associés à Railway. Cette solution a l'inconvénient d'augmenter la complexité de gestion puisqu'elle nécessite le déploiement du projet sur deux plateformes différentes. Il faudra donc gérer correctement les communications entre les deux services, les variables de configuration, les politiques mises en place et les différentes étapes de déploiement. À ce stade, la solution idéale n'est pas encore fixée. La complexité de sa mise en oeuvre et les coûts d'implémentation pourraient apporter des changements aux choix d'hébergement.

L'architecture serait alors :

```text
Utilisateur
    │
    ├──────────────► GitHub Pages
    │                 React / PWA
    │
    └──────────────► Railway
                      FastAPI
                         │
                         ▼
                    Base de données
```

## Une décision encore provisoire

Pour résumé, le choix de Railway et GitHub Pages n'est donc pas considéré comme définitif. Je devrai essayer de trouver un compromis entre simplicité, coût et capacité d'évolution.

Avant le déploiement final, je devrai notamment évaluer:

- les coûts;
- la facilité de configuration;
- la persistance des données;
- les performances;
- la facilité de déploiement;
- les possibilités de migration;
- la complexité générale de l'architecture.

[Retour](http://localhost:1313/posts/)
