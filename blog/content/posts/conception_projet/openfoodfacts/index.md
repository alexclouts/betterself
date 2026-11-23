---
title: "Intégrer OpenFoodFacts"
header: ""
date: 2026-11-22T20:04:00.000Z
description: "Comment j'ai surmonté les limites de l'API OpenFoodFacts et optimisation du processus pour rechercher des aliments."
tags:
  - IA
  - Frontend
  - Aliments
  - OpenFoodFacts
  - Script Bash
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Intégrer OpenFoodFacts

La prochaine étape de mon projet était de modifier mon backend pour que la recherche des aliments effectue une requête à **OpenFoodFacts**, une base de données _open source_ qui regroupe des aliments déjà créés par la communauté. J'ai aussitôt fait face à un imprévu : un _rate limit_ de 10 requêtes/min par adresse IP. Dans ce cas, tous les utilisateurs de mon application partagent la même adresse IP, ce qui rend cette solution inapplicable. Leur [site](https://openfoodfacts.github.io/openfoodfacts-server/api/) mentionne également: **don't use it for a search-as-you-type feature, you would be blocked very quickly.**

Si je consulte la documentation, je vois que la méthode recommandée pour ce genre d'utilisation est de télécharger les données localement en tant que fichier `CSV` ou `JSON`. J'aurai la responsabilité de :

1. Télécharger le jeu de données depuis OpenFoodFacts.
2. Filtrer les données avec DuckDB afin de conserver celles qui correspondent à mes critères de sélection (produits complets, pays).
3. Exporter le résultat sous forme de CSV compressé.
4. Se connecter à la base de production et mettre à jour les données existantes.

{{< alert info >}}
Dans une prochaine version, le traitement des données est une tâche que je vais relayer à mon Raspberry Pi. Je vais donc créer un cronjob qui exécutera automatiquement, à chaque semaine, mon script d'importation afin de mettre à jour les données accessibles par BetterSelf.
{{< /alert >}}

### Pour l'instant

Pour le MVP, je vais me concentrer à écrire le script pour qu'il soit **exécuté localement**. La prochaine itération de développement s'attardera à la configuration du Raspberry Pi.

## Adoption de PostgreSQL

Actuellement, _SQLite_ est la technologie utilisée pour ma base de données. J'avais déjà l'intention d'adopter une configuration PostgreSQL en cours de développement, mais cette nouvelle étape entraîne la migration plus tôt que prévu. En effet, **pg_trgm** et **COPY** n'existent que dans PostgreSQL, alors que ces opérations sont nécessaires pour l'importation et la recherche dans le catalogue de OpenFoodFacts. J'ai donc décidé d'effectuer la migration tout de suite pour mieux progresser plus tard. Tel que suggéré par Claude, nous utiliserons _psycopg_ comme adapteur Python pour PostgreSQL. Pour sauver du temps, Claude s'est chargé d'apporter les modifications au projet, qui comprend la création d'un fichier `docker-compose.yml` et le changement du _URL_ de la base de données utilisé pour les tests et en production.

## Télécharger les données localement

Claude m'a proposé un script `bash` afin de télécharger les données sur un disque dur externe que j'ai connecté sur un port USB.

```bash
set -e
cd "$OFF_ROOT/raw"
curl -fL --retry 3 -o products.csv.gz.part \
  https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz
gzip -t products.csv.gz.part            # échoue si le fichier est incomplet
mv products.csv.gz.part products.csv.gz
```

Il m'a également généré un programme Python `build_catalog.py` afin de construire une base de données à partir du fichier généré. Je lui ai spécifié certains critères pour filtrer les données : conserver uniquement les produits vendus au Canada et dont les valeurs sont complètes et plausibles.

## Ajouts au backend

### Recherche des aliments

Plusieurs ajouts ont dû être fait pour intégrer _OpenFoodFacts_ au projet. D'abord, le fichier `/backend/core/text_search.py` contient des fonctions visant à faciliter la recherche des aliments. Par exemple, le retrait des accents aide à mieux cibler les éléments recherchés. La recherche est dynamique (les résultats s'affichent au fur et à mesure que l'utilisateur écrit un mot), ce qui rend son fonctionnement plus complexe, mais aussi l'expérience plus agréable.

### Quantité de référence

L'ajout de `serving_g` au modèle `Food` fait suite à un problème auquel je n'avais pas réfléchi quand une suggestion est affichée à l'écran. Elle contient la portion suggérée pour cet aliment. Cette donnée est importante pour le UX, car elle doit correspondre à la portion probable que l'utilisateur ajoutera. Sans elle, nous aurions seulement accès à la quantité de référence `reference_weight_g`. J'ai tout de même questionné Claude sur la pertinence de distinguer ces deux valeurs :

### Conversation avec Claude

#### _Question :_ Pourquoi serving_g a été ajouté au modèle Food plutôt que d'utiliser directement reference_weight_g pour stocker la quantité recommandée par le fabricant?

Parce que les deux champs répondent à des questions différentes :

- `reference_weight_g` : « Pour combien de grammes les calories et les macros sont-elles déclarées ? » C'est le **dénominateur du calcul**.
- `serving_g` : « Quelle quantité proposer par défaut ? » C'est une **suggestion d'interface**, qui n'entre dans aucun calcul de nutriments.

#### Ce n'était pas la seule option

Pour un aliment créé à la main, `reference_weight_g` sert déjà aux deux : tu recopies l'étiquette (« 150 kcal pour 250 g »), et 250 g est la quantité proposée.

Cette approche aurait donc pu fonctionner pour _Open Food Facts_, avec une conversion à l'import et une colonne de moins. Je garderais quand même `serving_g`, surtout pour les 48 % de produits sans portion et parce que le FCÉN exprime lui aussi ses valeurs par 100 g.

### Décision

Afin d'assurer un partage des responsabilités mieux défini, j'ai décidé de garder l'implémentation suggérée par l'IA.

## Afficher l'historique des entrées

Le fait de pouvoir afficher l'historique des entrées effectuées dans le journal est aussi une fonctionnalité à laquelle je n'avais pas pensé, mais qui ajoute définitivement un côté pratique à l'application. Pour le moment, des fonctions permettent d'ordonner les entrés de la base de données afin de récupérer les entrées les plus récentes et les retourner au frontend. J'aimerais peut-être éventuellement que ces entrées soient filtrer **par repas** et que les entrées qui s'affichent dépendent du moment de la journée. Par exemple: À 8:00 AM, je vois les entrées du déjeuner de la veille. Cette façon de faire aiderait à avoir une meilleure expérience pour l'utilisateur.

### Accéder au repo de OpenFoodFacts

Un des questionnement que j'ai eu était: _De quelle manière l'application comprend-elle que ma base de données OpenFoodFacts se trouve sur mon disque dur externe?_ J'ai retracé `off_catalog_path` jusqu'à sa source dans la classe **Settings** pour voir qu'elle n'était pas déclarée explicitement dans l'application. En questionnant Claude à ce sujet, il m'a expliqué que la classe `BaseSettings`, de laquelle hérite _Settings_, lui permet d'accéder aux variables d'environnement du même nom. En déclarant la variable `OFF_CATALOG_PATH`, cela m'évite d'avoir à le spécifier dans mon code. Cependant, si la base de données est hébergée sur le Cloud, peut-être devrai-je le _hardcodé_?

## Quelques ajustements du UI

J'ai aussi remarqué, en voulant personnaliser l'écran d'accueil, que la variable `user.name` n'était pas accessible pour le "saluer" de style : _Bienvenue, Alexandre_. De plus,la largeur des élémens en dessous dépend de la longueur du texte plutôt que d'être fixe, ce qui modifie l'apparence des composantes.

J'ai discuté de cette problématique avec Claude, qui m'a intégré cette modification en ajoutant un `userService` au frontend pour récupérer les informations de **UserProfileRead**. Le paramètre `max-w-md` a été ajouté au _Card_ afin de fixer la largeur de la page d'accueil, comme c'est le cas pour les pages du journal.

### La suite

La prochaine étape consiste à intégrer d'autres fonctionnalités, telle que l'ajout ou la modifications des informations personnelles et l'ajout d'une mesure de poids.

[Retour](https://alexclouts.github.io/betterself/posts/)
