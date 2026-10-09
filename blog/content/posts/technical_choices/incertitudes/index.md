---
title: "Encore incertain..."
header: ""
date: 2026-09-25T08:50:00.000Z
description: "Les principales incertitudes techniques qui devront être résolues pendant le développement."
tags:
  - Incertitude
  - Questionnement
categories:
  - Fondations
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="600">}}

## Détails à explorer

À ce stade, même si l'architecture générale du projet commence à prendre forme, plusieurs décisions importantes n'ont pas encore été prises.

### La plateforme d'hébergement

Le **choix d'hébergement** est encore un choix qui n'est pas définitif. Plusieurs considérations sont encore inconnues pour le moment et dépendent de l'avancé du projet. Elles comprennent, par exemple, la simplicité de configuration du service utilisé, la facilité à intégrer une base de données SQL et les coûts associés à l'hébergement des services.

### L'authentification

Plusieurs options sont possibles. Lors de mes recherches, j'ai vu que `FastAPI` supportait la méthode **OAuth 2.0** d'emblée, ce qui est une avenue intéressante. Autrement, un service d'authentification traditionnel (combinaison email/mot de passe) peut également être offerte. Cette décision sera prise selon les besoins en matière de sécurité et le temps de développement requis pour sa mise en place.

### Frontend React

Comme `React` ne m'est pas encore familié, j'ignore pour le moment la structure à employer au sein du projet. Le choix des librairies et des fonctionnalités à utiliser est encore à déterminer. Par exemple, voici une liste des aspects que j'ignore pour le moment :

- comment organiser les composants;
- comment gérer l'état de l'application;
- comment effectuer la navigation;
- comment gérer les formulaires;
- comment communiquer avec l'API;
- quelles bibliothèques supplémentaires sont réellement nécessaires.

### Intégration de l’API Open Food Facts

Plusieurs questions ne sont pas encore répondues concernant la gestion des requêtes à l'API externe `Open Food Facts`. Par exemple, comment gérer les cas où un code-barres n’est pas reconnu ? Faut-il prévoir un mécanisme de cache local pour limiter les appels externes et améliorer les temps de réponse ?

Ces incertitudes seront répondues au fur et à mesure que les premières fonctionnalités seront développées (authentification, recherche d’aliments, enregistrement de consommations, tableau de bord).

## Évolution du projet

Certaines décisions sont difficiles à prendre avant d'avoir développé les premières fonctionnalités. Les premiers prototypes devraient permettre de valider plusieurs hypothèses décrites ci-haut. Je prévois de revoir progressivement ces choix au fur et à mesure que j'aurai implémenté l'authentification, la recherche d'aliments, l'enregistrement des consommations et le tableau de bord au sein du système.

[Retour](https://alexclouts.github.io/betterself/posts/)
