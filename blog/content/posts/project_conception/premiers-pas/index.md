---
title: "Premières étapes de conception"
header: ""
date: 2026-10-23T20:04:00.000Z
description: "Début du projet: ajustements des conversations avec l'IA et enjeux d'efficacité."
tags:
  - IA
  - Incertitude
  - Backend
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Par où commencer

Maintenant que l'architecture a été choisie, je veux savoir ce qui constitue le meilleur point de départ pour débuter la conception du projet. Je crois qu'il est facile de tomber dans le "piège" de s'attaquer tout de suite au frontend, comme il s'agit d'une façon concrète de voir ma progression de jour en jour. J'ai donc demandé à l'IA de m'aider à situer les premières étapes sur lesquelles je pourrai m'appuyer pour aller de l'avant.

La prochaine section illustre une conversation condensée que j'ai eu avec _Perplexity_. Celle-ci m'offre l'option de convertir les idées échangées sous forme de fichier `Markdown`. Elle fait suite à l'implémentation de FastAPI et de la politique CORS, discuté dans la [dernière publication](https://alexclouts.github.io/betterself/posts/configuration-api/).

## Conversation avec l'IA (1)

#### Donc mon pipeline CI fonctionne et l'API parvient à se connecter au frontend. Quelle serait la prochaine étape logique?

Bravo : ta base est maintenant solide. La prochaine étape logique est d’implémenter **l’authentification des utilisateurs**, parce qu’elle débloque toutes les autres fonctionnalités : profils, mesures, objectifs et journal alimentaire devront appartenir à un utilisateur authentifié.

### Feuille de route

```text
1. Base de données et migrations
2. Inscription
3. Connexion avec JWT
4. Endpoint protégé /me
5. Profil utilisateur
6. Mesures corporelles
7. Objectifs nutritionnels
8. Aliments et journal
```

Je te recommande de ne pas passer à l’étape suivante avant que l’étape courante soit testée.
[...]

- Étape 1 : installer les dépendances
- Étape 2 : créer la configuration
- Étape 3 : créer la base de données
- Étape 4 : créer le modèle `User`
- Étape 5 : créer les schémas Pydantic
- Étape 6 : ajouter la sécurité
- Étape 7 : créer le service utilisateur
- Étape 8 : créer le routeur
- Étape 9 : enregistrer le routeur
- Étape 10 : créer la migration
- Étape 11 : tester l’inscription et la connexion
- Étape 12 : endpoint protégé `/me`
- Étape 13 : test d’authentification

{{< alert info >}}
L'IA m'a proposé le code associé à chaque étape énoncée ci-haut. Celles-ci ont été abrégées pour faciliter la lecture.
{{< /alert >}}

## Ma réflexion

J'ai aimé que l'IA me propose rapidement une feuille de route à suivre. Par contre, la suite de la conversation est trop précipitée à mon avis : elle me propose aussitôt 13 étapes afin d'implémenter les premières composantes, sans fournir les explications qui me permettraient de comprendre leur rôle au sien de l'application.

De plus, elle ne reflète pas la méthode que je désirais préconiser, soit l'approche de _Test-Driven Development_. Plutôt que de recopier aveuglement les suggestions proposées, j'ai choisi de corriger le tir en apportant des précisions :

## Conversation avec l'IA (2)

#### J'aimerais adopter une approche Test-Driven Development. Peux-tu orienter le projet en ce sens? Je ne veux pas aller trop vite. Pour le moment j'ai créé le fichier config.py avec la classe Settings. Pour commencer, je veux que tu m'aides à déclarer le fichier database.py et les fichiers unitaires pour la base de données.

Oui, c’est une excellente approche pour BetterSelf. En TDD, tu écris d’abord un test qui échoue (**rouge**), puis le minimum de code pour le faire passer (**vert**), et enfin tu améliores le code sans casser les tests. Restons sur une seule étape : créer l’infrastructure de base de données, puis vérifier qu’elle fonctionne avec un test. On n’ajoutera pas encore les utilisateurs ni les routes.

### Structure à créer

Depuis `backend/`, crée ces fichiers :

```bash
mkdir -p src/betterself/core
touch src/betterself/core/__init__.py
touch src/betterself/core/database.py

mkdir -p tests
touch tests/conftest.py
touch tests/test_database.py
```

Ta structure devrait ressembler à ceci :

```text
backend/
├── src/
│   └── betterself/
│       ├── __init__.py
│       ├── main.py
│       └── core/
│           ├── __init__.py
│           ├── config.py
│           └── database.py
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   └── test_health.py
└── pyproject.toml
```

## Ma réflexion

L'IA m'a ensuite proposé le code afin de concevoir :

1. Le fichier `database.py`, qui comprend le générateur de base de données et de session
2. Le fichier `.env`
3. Le fichier `test_database.py`, qui comprend les tests unitaires de la base de données permettant de générer une session `SQLAlchemy` et valider que la création d'un table fonctionne bien.

J'ai ensuite poursuivi ma conversation avec l'IA en conservant la structure qu'elle m'a proposée initialement. La prochaine étape était le développement du modèle de la table `User`.

### Enjeux de l'efficacité

Un défi que je rencontre régulièrement lorsque je travaille avec l'IA est qu'elle fonctionne très rapidement. Elle propose donc beaucoup, voire trop d'informations en même temps. Cela nécessite une plus grande attention pour ne pas ignorer des étapes essentielles au développement. J'ai d'ailleurs rencontré cette situation avec _Alembic_ pour la migration de la base de données. Il s'agit de l'étape 10 proposée initialement dans notre conversation. Cependant, étant donné la quantité volumineuse d'informations, la configuration de _Alembic_ m'a échappé, ce qui a d'ailleurs été mentionné dans la rétroaction du Jalon 2.

Dorénavant, je devrai prendre mon temps davantage pour compenser avec la rapidité de l'IA lors des prochanes étapes.
