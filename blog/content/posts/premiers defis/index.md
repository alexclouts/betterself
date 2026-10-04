---
title: "Mes premiers défis!"
header: ""
date: 2026-09-26T08:45:00.000Z
description: "Configurer le projet GitHub et m'approprier l'IA."
tags:
  - IA
  - Défi
categories:
  - Cadrage et recherche
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

## Premiers défis rencontrés

### Configuration de l'environnement `uv`

En configurant `uv` avec la commande `uv init`, j'ai rencontré plusieurs erreurs en voulant reproduire les exemples donnés durant les explications. Plutôt que de créer un fichier `main.py` dans le répertoire de mon projet, ma commande configurait plutôt le fichier `__init__.py` dans un nouveau répertoire `/src/betterself/`.

#### Erreur de validation : Mauvais fichier

Finalement, l'IA me recommandait aussi de créer un répertoire distincts nommé `tests` uniquement pour les tests unitaires de mes fonctions, ce que j'ai fait. Par contre, le pipeline CI ne validait pas mon workflow. J'ai à nouveau tenté de reproduire l'exemple donné pour créer un test, mais la commande `from main import calories_per_gram...` a échoué puisque j'ai fait une erreur en spécifiant le chemin vers les fonctions testées. Puisqu'elles se trouvaient dans le fichier `__init__.py`, il fallait que je spécifie le nom du projet pour y avoir accès : `from betterself import...`.

### Apprentissage de Git

Une autre défi que j'ai rencontré est l'apprentissage de **Git**. D'abord, il y a des étapes à respecter pour envoyer un commit, lire le status des modifications effectuées, les commandes `push` et `pull`, etc. Bien que je reconnais l'importance de la sécurité, j'ai aussi été étonné d'avoir besoin de configurer un token avec des accès particuliers pour envoyer un commit. Puisque mon répertoire est public, l'IA m'a recommandé de fournir un adresse courriel `noreply` , que j'ai pu activé dans les réglages de mon compte.

### L'usage de l'IA en programmation

Cet aspect est un défi, mais surtout une méthode de travail à adopter pour le reste du projet. Il s'agit de l'habitude d'avoir recours à l'IA pour écrire le code tout en conservant le rôle de chef d'orchestre. Par exemple, dans `VSCode` j'ai eu recours à l'IA pour générer des fonctions simples qui se retrouveront plus tard dans l'application. Ça me semblait _contre-intuitif_ d'offrir des permissions à l'IA pour générer du code à ma place. J'ai double vérifier certaines commandes qu'elle désirait exécuter avec mon autorisation afin de comprendre son but et si je pouvais lui faire « confiance ».

Si je rencontre des problèmes plus techniques durant le projet, je ferai des vidéos explicatives afin d'expliquer les défis et les solutions que j'aurai identifié.

[Retour](http://localhost:1313/posts/)
