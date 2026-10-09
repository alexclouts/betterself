---
title: "Présentation du blog"
header: ""
date: 2026-10-04T14:30:00.000Z
description: "Présentation du blog et des problématiques rencontrées lors du déploiement et correction de bogue."
tags:
  - Vidéo
  - Défi
categories:
  - Fondations
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

La publication que je vous partage aujourd'hui présente les derniers préparatifs avant d'entâmer le développement de l'application `BetterSelf`. Dans le cadre d'une vidéo explicative, je vous explique les fonctionnalités du blog et les choix que j'ai fait afin de construire le site.

Trouvez le lien vers la vidéo YouTube [ici](https://www.youtube.com/watch?v=CSiVBhjG1qg "Vidéo 1: Présentation du Blog").

## Erreur de navigation

Durant la vidéo, je décris un problème que j'ai rencontré pendant que je testais les fonctionnalité du site. En naviguant à la section `Étapes du projet`, la redirection de page échoue lorsque je clique sur une étape. J'ai vérifié la logique de l'application et j'en ai conclu que le problème était probablement lié au chemin d'accès. En effet, j'ai renommé l'onglet original `Categories`, ainsi que son chemin URL pour qu'il devienne `phases`, comme le démontre l'image suivante:

{{< img
src="screenshot1.png"
alt="Capture d'écran 1"
caption="">}}

### Identification du problème

Quand je vérifie le lien du renvoi, j'ai remarqué que l'URL n'a pas été modifié. Elle est toujours `https://alexclouts.github.io/categories/cadrage-et-recherche/`.

{{< img
src="screenshot2.png"
alt="Capture d'écran 2"
caption="">}}

Après avoir découvert cette problématique, j'ai demandé à l'IA intégrée à Visual Studio Code d'apporter les modifications nécessaires pour rectifier la situation. Après avoir confirmé que la correction avait bien été faite, j'ai `push` la nouvelle version dans la branche principale du projet.
