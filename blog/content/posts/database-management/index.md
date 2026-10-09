---
title: "Réflexions sur le schéma des données"
header: ""
date: 2026-10-07T21:56:00.000Z
description: "Réfléchir à comment organiser les données dans l'application de la meilleure manière envisageable, selon les tâches à accomplir."
tags:
  - SQL
  - Architecture
categories:
  - Architecture et données
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Comment schématiser les données ?

Pour m'aider à déterminer la meilleure manière de structurer les données dans le cadre du projet, j'ai décidé de m'attarder à chaque fonctionnalité de l'application en analysant les problèmes à résoudre. J'aborderai chacun de ces thèmes, un à un, afin de définir les schémas les plus appropriés pour la gestion de leurs données.

## Authentification des utilisateurs

L'authentification comprend la connexion de l'utilisateur à l'application. Cette table devrait être la plus épurée possible selon moi. On ne veut pas qu'elle contienne des mesures comme le poids, sexe, âge, niveau d'activité, ect. puisque, même si ces informations portent sur l'utilisateur, cette table sert uniquement à l'authentifier. La séparation des tâches évite de faire appel à cette table si, par exemple, un utilisateur perd 1 lbs. et qu'il apporte des modifications à son profile. On limite les raisons d'interagir avec cette table afin de limiter son exposition et des enjeux de sécurité.

### Sauvegarde du hash

Comme je l'ai expliqué dans une [publication](https://alexclouts.github.io/betterself/posts/authentication/ "Mais qui êtes-vous ?") portant sur l'authentification la semaine dernière, c'est important de **ne pas sauvegarder le mot de passe en _plain text_ dans la base de données**. C'est ici que le hash entre en jeu. On va plutôt utiliser des algorithmes pour encrypter le mot de passe, tels que **Argon2id et bcrypt**.

## Autres informations du profile

Ce qui nous amène aux autres informations que nous obtenons au sujet de l'utilisateur pour calculer son `BMR` (Basal Metabolic Rate) - soit le nombre de calories dépensé au repos. En apprendre davantage [ici](https://my.clevelandclinic.org/health/body/basal-metabolic-rate-bmr/ "BMR (Basal Metabolic Rate)"). Nous chercherons à obtenir ces informations assez rapidement une fois que l'utilisateur aura créé son compte. Le calcul du BMR se fait selon plusieurs paramètres :

- Le poids (qu'on peut sauvegarder en _kg_ **dans une table dédiée** comme expliqué ensuite)
- La taille (en _cm_)
- L'âge. Pour ne pas sauvegarder des données personnelles inutilement, on conserve l'année de naissance uniquement.
- Le niveau d'activité physique. Faible à Élevé. Cette valeur sera choisie sous forme de choix à suggestions.

Ces informations sont associés à un seul utilisateur, qu'on peut identifier avec son ID. On peut également récupérer son nom pour favoriser un meilleur _UX_.

### Changement de poids au fil du temps

On se retrouve face à un problème d'architecture intéressant. Naturellement, le poids de l'utilisateur fluctue au fil du temps. S'il désire connaître l'évolution de son poids, par exemple, sur un graphique, nous devons trouver un moyen de stocker ces données de manière cohérente. Il nous faudrait donc une table qui sauvegarde les enregistrements de son poids à un temps donné, et qu'on associe cette entrée à l'utilisateur qui l'a créé. Parmi les données qu'on voudra enregistrer, on y trouve :

- L'ID de l'utilisateur à qui appartient la saisie
- Le poids mesuré (en kg)
- Un _timestamp_ qui identifie le moment exact de la capture.
- Une photo ?

{{< alert info "La photo de progression" >}}
Dans une version 2.0, je pourrais configurer la fonction de joindre une photo associée au poids enregistré.
{{< /alert >}}

## Les objectifs

Comme mentionné dans la [présentation](https://alexclouts.github.io/betterself/posts/inspirations/ "La première impression") du projet, l'utilisateur commence le processus de On Boarding en se fixant des objectifs en matière de nutrition. Ces objectifs doivent être sauvegardés à quelque part avec un format structuré.

### Type d'objectif

On se demande d'abord, veut-il:

- Perdre du poids
- Prendre de la masse musculaire
- Maintenir son poids corporel
- Faire une recomposition corporelle

{{< alert info "La recomposition corporelle" >}}
La recomposition corporelle passe aussi par l'entraînement physique de l'utilisateur, ce qui implique une forme de suivi des séances. Pour garder le projet initial simple, la version 1.0 ne couvrira pas cet aspect.
{{< /alert >}}

On veut aussi conserver des informations telles que:

- La date de début de l'objectif (_timestamp_)
- La date de fin prévue pour atteindre l'objectif (_timestamp_)
- Le poids qu'il vise à atteindre (en kg)

### Des objectifs plus spécifiques

Ces informations sont déterminées dès le jour 1, et elles ne sont pas supposés changer tant que l'objectif n'est pas accompli. Cependant, on aimerait pouvoir accéder à des objectifs plus concrets au quotidien, tel que de savoir le nombre de calories et de protéines devront être consommés durant la journée (aussi appelée la cible). Quand le poids d'une personne change, un nouveau calcul du BMR devra être fait pour ajuster le déficit en conséquence.

C'est pourquoi il est préférable de contenir ces données dans une seconde table, soit pour les cibles courantes qui sont régulièrement mises à jour. Chaque nouvelle entrée de poids par l'utilisateur entraînera la création d'une nouvelle _cible nutritionnelle_, qui prendra la place de l'ancien.

## Aliments

Du côté des aliments, il est certain que nous devons concevoir un schéma pour représenter les aliments. On veut aussi pouvoir lui attribuer des données nutritionnelles. Une première table serait de représenter un aliment par ses informations nominatives et des indications qui lui permettent de voir d'où il provient (sa source).

#### Indécision au sujet des informations nutritionnelles

Pour cette approche, j'ai des hésitations au sujet de ce qui est préférable. Devrais-je conserver les données nutritionnelles d'un aliment dans une table distincte? Si je conserve les valeurs nutritionnelles de cet aliment dans une table différente, cela me permettrait de séparer clairement deux responsabilités, soit l'identité de l'aliment et sa composition. Cette façon de faire permettrait aussi de gérer plusieurs sources pour le même aliment, selon la marque, par exemple. Par contre, cette division rend l'architecture de la base de données plus complexe. Comme je veux `Keep It Simple Stupid` pour l'instant, j'ai privilégié une structure tout-en-un pour le moment.

{{< alert info "Le partage des aliments" >}}
Dans une version 2.0, je pourrais ajouter la fonctionnalité de créer un aliment accessible par d'autres utilisateurs. Cette fonction nécessiterait la configuration d'une base de données en ligne afin de servir les requêtes en provenance de l'application.
{{< /alert >}}

### La création d'une recette

Je considère que cette fonctionnalité est assez importante pour être inclue dès la première version. Un utilisateur pourra créer une recette (un repas, en d'autres mots), en y ajoutant des aliments. Une fois la _recette_ créée, elle se comporte de la même manière qu'un aliment, c'est-à-dire que la personne peut l'ajouter à son journal sans devoir consigner tous les aliments un-à-un. Selon moi, lorsqu'une recette est créée, on devrait toujours pouvoir consulter les aliments qui la compose. Nous devrions ainsi avoir deux tables distinctes: une qui contient l'_identité_ de la recette, et l'autre qui contient tous les aliments associés à celle-ci.

Pour créer une recette, on devra avoir des informations telles que le poids total, l'ID du propriétaire à l'origine de l'entrée, un nom et une description facultative. Maintenant, pou déterminer ce qui compose une recette, on doit avoir une table qui comprend :

- L'ID de la recette liée à l'entrée
- L'ID de l'aliment ajouté
- La quantité ajouté

#### Questionnements au sujet de la suite logique

Si on se projette dans le fonctionnement des requêtes, l'utilisateur qui ajoute une recette à son journal entraînera les opérations suivantes :

1. Depuis la table `recipe_ingredients`, récupération des ingrédients associés à l'ID de la recette.
2. Depuis la table `foods`, récupération des informations nutritionnelles associées à chaque aliment de la liste obtenue. Les valeurs que nous recherchons sont `reference_weight_g`, `calories_kcal`, et la quantité de macronutriments.
3. En fonction de la quantité indiquée par l'utilisateur, il faut calculer, au prorata, la valeur nutritionnelle de la recette selon les valeurs pour chaque aliment.

Maintenant, je me demande si une méthode plus simple me permettrait d'alléger cette procédure? Si une recette est consignée tel un aliment lorsque l'utilisateur l'ajoute à son journal, ne serait-il pas plus simple de créer une nouvelle entrée dans la table `aliment` qui hériterait des informations de la recette? La valeur nutritionnelle pourrait se calculer seulement lorsque la recette est créée, ce qui éliminerait la nécessité d'effectuer des requêtes successives à chaque fois que l'utilisateur ajoute une recette au journal.

Cette situation me faisait hésiter jusqu'à ce que je me pose la question suivante: _qu'adviendrait-il si on ajoute un aliment à notre recette après sa création, ou qu'on modifie le poids d'un item?_ Les informations associé à la recette ne seraient plus valides. Si on veut que les informations restent cohérentes, on devrait alors mettre à jour **deux tables** à chaque fois qu'un aliment au sein d'une liste subit des modifications, soit:

1. `recipe_ingredients`: Ajout d'un ingrédient ou mise à jour de sa quantité
2. `foods`: Recalcul de la valeur nutritionnelle totale associé à la recette, puisque sa composition a changé.

Je crois aussi que la bonne pratique à adopter dans ce contexte est de conserver une séparation logique entre les entités. Une recette et un aliment ont **des propriétés distinctes** qu'on ne doit pas confondre. Quand j'analyse le processus de cette façon, cette nouvelle alternative est définitivement une façon de faire moins intuitive que l'idée proposée initialement. Je crois qu'il est préférable que l'application mesure la composition d'une recette à chaque fois qu'un utilisateur l'ajoute à son journal. Cela nous garantit qu'on aura toujours les valeurs à jour. La gestion de la mémoire _cache_ permettra aussi d'accélérer ce processus et de minimiser les requêtes faites à la base de données.

## Entrée dans le journal

D'ailleurs, il faut réléchir à la manière dont l'utilisateur pourra consigner un aliment dans son journal, tout en s'assurant que l'application puisse récupérer l'historique alimentaire de la personne. Il faut considérer les caractéristiques suivantes :

1. Une entrée est associé à un utilisateur, donc elle devra conserver son ID.
2. Une entrée peut être un aliment ou une recette. Comme mentionné ci-haut, elles sont dans une table différente, donc il faut conserver leur ID dans un champ propre à chacun afin de retracer la ressource originale.
3. Un seul champ entre `food_id` et `recipe_id` doit être déclaré. L'autre sera forcément `NULL`.
4. Puisqu'on veut conserver l'historique des entrées, les informations doivent être à l'abri des modifications futures apportées aux recettes ou aux aliments. Pour cette raison, le nom et la valeur nutritionnelle de l'aliment seront enregistrés au moment où il est consommé.
5. On doit conserver la date de l'ajout et la recette associée à cette consigne.

# Conception actuelle

Pour résumé la conception de la base de données, voici les tables conçues jusqu'à présent :

1. Pour l'utilisateur:

- `users`: Données liées à l'authentification uniquement.
- `user_profiles`: Données du profile, permettant de mesurer le BMR.
- `body_measurements`: Données liées à la mesure du poids.
- `nutrition_goals`: Données portant sur les objectifs globaux.
- `goal_targets`: Données portant sur les objectifs quotidiens.

2. Pour le journal:

- `foods`: Données nominatives et nutritionnelles d'un aliment.
- `recipes`: Données nominatives d'une recette.
- `recipe_ingredients`: Données d'un aliment consigné dans une recette.
- `food_consumptions`: Données associées à une entrée dans le journal.

# Éléments manquants au MVP

J'ai questionné l'IA à savoir si des tables sont manquantes selon ma conception initiale des besoins de l'application. Elle m'a offert des suggestions intéressantes que je pourrai implémenter une fois que le _MVP_ sera fonctionnel. Elle m'a suggéré les point suivants :

## Les portions

Actuellement, toutes les quantités sont saisies en grammes, mais ce principe ne permet pas d'ajouter des quantités plus intuitives pour l'utilisateur, comme: une banane, deux oeufs, une tasse de riz, etc. Cette option permettrait d'améliorer l'UX au sein de l'application. Pour ce faire, l'IA me propose d'ajouter une table qui s'occupe **des portions**, afin d'associer une quantité (mesurée en grammes) à une mesure abstraite qu'on peut choisir lorsqu'on ajoute un aliment.

## Optimisation des repas de la journée

Les repas de la journée sont directement imbriquées dans l'entrée de la table `food_consumptions`. Cette méthode est simple et fonctionnel pour le MVP, mais elle offre moins de liberté si, par exemple, l'utilisateur veut diviser sa journée en 6 repas, ou s'il veut leur assigner un nom personnalisé. L'IA me suggère donc de créer une table `meals` dédiée à chaque repas. Au lieu de _hardcodé_ le nom du repas dans l'entrée du journal, on pourrait conserver l'ID qui fait référence au repas associé.

## Résumé nutritionnel quotidien

Cette dernière est facultative selon l'IA, mais elle est particulièreme pratique si je désire afficher rapidement des statistiques en lien avec l'historique de consommation de l'utilisateur. Il s'agirait d'une table `daily_nutrition_summaries`, qui regroupe les résumés quotidien de l'apport calorique et nutritionnelle consommé.

[Retour](https://alexclouts.github.io/betterself/posts/)
