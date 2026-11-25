---
title: "Amélioration du workflow"
header: ""
date: 2026-11-25T13:20:44.000Z
description: "J'augmente l'efficacité du workflow, tout en ajoutant les fonctions de mesures de poids."
tags:
  - IA
  - Frontend
  - Workflow
  - Efficacité
  - Barcode
categories:
  - Développement
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Amélioration du workflow

Dans cet article, j'aborde l'évolution du projet sous l'angle du recours à l'IA et des changements que cela entraîne sur ma façon de travailler. En ajoutant de nouvelles fonctionnalités, j'ai cherché de nouvelles manières de rendre le développement plus efficace pour garantir que le travail effectué par Claude soit relu et compris avant chaque commit à la branche principale.

## La mesure de poids

Pour intégrer la mesure de poids, j'ai voulu tester les limites de l'IA en lui demandant de me représenter visuellement les fluctuations du poids de l'utilisateur sur un graphique. Claude m'a donc généré un fichier `WeightChart.tsx` pour y construire le rendu les comosantes. J'ai été agréablement surpris du résultat et de constater qu'elle n'a pas eu recours à une librairie externe pour accomplir cette tâche. De plus, quand on survole un point correspondant à une entrée, une bulle informative affiche les détails (date, poids précis et fluctuation par rapport à la dernière mesure). Je n'aurais pas pu imaginer mieux pour le déploiement du MVP.

Le recours rapide à l'IA me place dans une situation délicate. Son utilisation est nécessaire pour progresser à un rythme qui me permettra de terminer le projet à temps pour la remise, mais le défi est à présent celui de réviser le code introduit par l'IA. Or, mon rôle n'est plus d'écrire du code efficace, mais plutôt de _"suivre la game"_ en essayant de comprendre les chemins empruntés pour que tout fonctionne correctement.

### Exemple simple

Après avoir demandé à Claude de construire la page servant à enregistrer une mesure de poids, j'ai testé cette fonctionnalité et je me suis apperçu que l'ajout d'une nouvelle mesure affichait simplement un message de réussite à l'écran. La plupart du temps, cette opération est unique et ne nécessite pas de rester sur cette page par la suite. J'ai donc demandé que l'utilisateur soit redirigé vers l'écran d'accueil lorsque l'entrée est ajoutée sans erreur.

## L'ajout de _Toasts_

Lorsqu'une valeur associée au BMR change (poids, niveau d'activité physique, etc.), cela entraîne un recalcul de la cible nutritionnelle quotidienne. Je voulais donc une manière de notifier l'utilisateur quand quelque chose de nouveau se produit. Par contre, l'ajout des pop-ups (aussi appelés _Toasts_) ont entraîné de nombreuses modifications au sein du projet. J'ai donc demandé à Claude de créer un **pull request** avec celles-ci. Pour améliorer mon _workflow_ pendant que je révisais le code, j'ai aussi demandé à Copilot d'analyser le commit de son côté. J'ai été étonné de voir que des changements était suggérés par Copilot.

{{< img
src="screenshot1.png"
alt="Screenshot1"
caption=""
width="500">}}

Le résumé des changements apportés par ce _PR_ est également une belle découverte que j'ai fait. Pour des ajouts mineurs au projet, cette façon de faire pourra m'aider à sauver du temps plutôt que de revoir le commit en entier à chaque fois.

Maintenant, mon **workflow** ressemble plutôt à :

1. Demander à Claude le développement d'une nouvelle fonctionnalité.
2. Tester le déploiement en fonction du comportement voulu.
3. Expliquer à l'IA les correctifs à apporter, s'il y a lieu.
4. Créer un _pull request_ des changements à approuver.
5. Réviser le code produit, assisté de Copilot si nécessaire.
6. Merger le pull request à la branche principale si tout est conforme à mes attentes.
7. Passer à la prochaine itération.

## Commandes pratiques

Les commandes que j'ai écrite sur mon tableau blanc m'aident également à avoir un workflow plus efficace. Quand une modification importante est effectuée, je dois redémarrer mon _frontend_ et c'est pratique d'avoir la commande à porter de main.

{{< img
src="tableau_blanc.jpg"
alt="Tableau blanc"
caption=""
width="500">}}

## Une autre décision importante

Pour conclure la semaine, une autre décision importante que j'ai dû prendre portait sur le choix de technologie de lecture pour le **bacode detector**, qui sera la prochaine étape après la gestion des mesures de poids. En lui demandant de m'aider à concevoir cette fonctionnalité, voilà ce qu'il m'a expliqué :

### Conversation avec Claude

#### _Question :_ Quelles sont les étapes pour la lecture du code barre maintenant?

#### Les étapes proposées

1. Choisir la technologie de lecture. L'API native `BarcodeDetector` existe dans Chrome sur Android, mais pas dans Safari sur iPhone ni dans Firefox. Je recommande le `polyfill barcode-detector` (basé sur ZXing) : il expose la même API partout, donc un seul code à maintenir. Formats à activer : `EAN-13`, `EAN-8`, `UPC-A` et `UPC-E`.

2. Créer le composant de lecture (**BarcodeScanner**) :
   - ouvrir la caméra arrière avec `getUserMedia` ;
   - lire l'image en continu jusqu'à reconnaître un code, puis faire vibrer le téléphone et éteindre la caméra ;
   - gérer les cas d'échec avec des messages clairs : permission refusée, pas de caméra, navigateur non compatible ;
   - toujours proposer de taper les chiffres à la main, pour un ordinateur ou une étiquette abîmée.

3. Brancher le parcours. Un bouton 📷 sur la page de recherche ouvre la lecture. Après un scan, deux cas :
   - **produit trouvé** : on va directement à la page d'ajout de l'aliment (après import s'il vient du catalogue), sans passer par la liste de résultats ;
   - **produit inconnu** : on ouvre la création d'aliment avec le code déjà rempli. Il est enregistré dans `external_reference_id`, et le prochain scan du même produit le retrouve. C'est exactement ce que demande la vision du client dans le `README`.

4. Ajuster le backend (petit). Je suggère une route dédiée, `GET /foods/barcode/{code}`, qui renvoie un seul résultat ou une 404. C'est plus clair qu'une recherche pour le parcours « trouvé / inconnu ». Il faut aussi vérifier deux points, avec des tests :
   - un aliment créé à la main est-il retrouvé par son code, et seulement par son auteur ?
   - que se passe-t-il si deux aliments ont le même code ?

## Analyse

Compte tenu de sa simplicité d'utilisation, je vais préférer `polyfill barcode-detector` aux alternatives, puisque je préfère qu'elle soit utilisable autant pour Android que pour iOS.

### Prochain article

Dans le prochain article, je poursuivrai le développement du lecteur de codebarre et nous aurons un premier aperçu de l'application sur mobile grâce au _port forwarding_ via USB.

[Retour](https://alexclouts.github.io/betterself/posts/)
