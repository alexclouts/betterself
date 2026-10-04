---
title: "La première impression"
header: ""
date: 2026-09-26T08:45:00.000Z
description: "Logo, processus de On Boarding et recherche d'inspiration."
tags:
  - Idée
  - Inspiration
categories:
  - Cadrage et recherche
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

## Inspiration et recherche d'idées

En attendant que le projet soit validé et que je puisse aller de l'avant, j'ai commencé à m'attarder au `UI`. Je me suis fixé 3 tâches pour m'aider à visualiser de quoi l'application aura l'air :

- Créer un logo et choisir la couleur primaire et secondaire.
- Déterminer les informations à obtenir lors du processus de `On Boarding`.
- Rechercher des designs qui serviront d'inspiration pour le projet.

### Création du logo

L'IA m'a aidé à générer un logo basé sur les couleurs que je vais utiliser dans mon projet, soit **bleu** comme couleur primaire et **orange** comme couleur secondaire.

{{< img
src="logo.png"
alt="Logo de BetterSelf"
caption=""
width="300">}}

### Le processus On Boarding

La création d'un compte sur l'application nécessite un processus de **On boarding** sous forme de questions à répondre. Les réponses fournies par l'utilisateur serviront à mettre de l'avant les fonctionnalités de l'application pour qu'elles reflètent bien ses objectifs. Certains sujets devraient être abordés, tel que démontré sur le tableau blanc.

{{< img
src="tableau.jpg"
alt="Croquis du processus sur tableau blanc"
width="600"
caption="">}}

Ces points m'aident à prévoir les informations que je devrai stocker au sujet de l'utilisateur dès le lancement de l'application. Ils seront utiles lors du développement de la base de données SQL.

## Bibliothèque de designs

### Design #1

Source: https://dribbble.com/shots/27762376-Dashboard-UI-for-Real-Estate-Arden

{{< img
src="design1.jpg"
alt="Image du design 1"
caption="">}}

#### Points clés:

- Le contraste des couleurs qu'on retrouve dans les `layouts`, soit le gris plus foncé pour les éléments non sélectionnés, la couleur de fond blanc/gris et la couleur primaire quand l'utilisateur sélectionne un choix.
- La manière dont les composantes sont disposés sur l'écran, de sorte qu'on peut voir plusieurs informations sur une seule page.
- Je crois que ce modèle s'adapterait bien à une application mobile.
- Les barres de progression dans la section `Property Views` serait une excellente manière de présenter l'évolution des aliments consignés durant la journée.

### Design #2

Source: https://dribbble.com/shots/27761977-Money-Management-Dashboard

{{< img
src="design2.png"
alt="Image du design 2"
caption="">}}

#### Points clés:

- Je trouve que le menu à gauche facilite le passage d'une section à l'autre dans l'application. Sur l'interface mobile, le menu pourrait défilé en cliquant sur un bouton burger au coin gauche de l'écran.
- La section `Overview` donne immédiatement un aperçu des données importantes pour l'utilisateur, que je pourrais reproduire en affichant sa progression pour la période en cours.
- La section des `Recent Transactions` pourrait aussi être remplacé par les aliments qui ont récemment été consigné, avec la possibilité de faire un ajout rapide.
- Le style des chartes en demi-lune et linéaire qui permet rapidement de voir nos résultats.

### Design #3

Source: https://dribbble.com/shots/27760886-Dieting-Mobile-App

{{< img
src="design3.png"
alt="Image du design 3"
caption="">}}

#### Points clés:

- Ce design ressemble davantage à mon idée d'application.
- La manière dont les repas de la journée sont divisés en sous-catégorie (`breakfast`, `lunch`, `snacks` et `dinner`) et chacune d'elle affiche le nombre de calories consommés.
- Ça donne une façon de mieux organiser son alimentation.
- Par contre, l'usage de l'IA pour scanner la nourriture n'est pas une fonctionnalité que je veux implémenter en raison du coût et de la complexité qu'elle impose.
- À mon avis, le calendrier n'est pas nécessaire puisqu'il entraîne une surcharge de travail inutile et qu'il ne s'agit pas d'une fonctionnalité essentielle.

[Retour](http://localhost:1313/posts/)
