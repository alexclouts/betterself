# ADR: Choix d'un frontend React

## Contexte

Nous devons choisir une bibliothèque Javascript qui agira comme frontend de l'application pour offrir une interface qui devra être interactive, réactive et accessible depuis différents appareils. Elle devra également communiquer avec un backend FastAPI afin d’envoyer et de recevoir des données au format JSON.

React sera responsable de l’affichage des pages et des composants, de la gestion des formulaires et de l’état local de l’interface, ainsi que de l’envoi des requêtes HTTP vers l’API. Il ne contiendra pas la logique métier principale, comme le calcul du métabolisme ou l’enregistrement des mesures dans la base de données.

## Options considérées

- React
- Vue.js
- Application native (Kotlin)

## Décision

React sera la bibliothèque Javascript choisie pour le frontend.

## Avantages

1. **Interface partagée sur plusieurs appareils.** React nous permet de construire une seule application qui cible différentes plateformes: ordinateur, appareil mobile, tablette.

2. **Architecture basée sur les composantes.** Cette bibliothèque facilite la réutilisation du code en divisant sa structure en composantes, ce qui le rend modulable et facile à déployer ou à mettre à jour.

3. **Support de la communauté.** React est une solution très populaire au sein des développeurs. On y trouve donc une grande variété d'exemples, de cas d'utilisation et de bibliothèques prêtes à être intégrées.

4. **Grande flexibilité.** React peut être combinée à une grande variété de bibliothèques et de _frameworks_ différents, ce qui nous permet de tirer le meilleur parti de plusieurs technologies.

5. **Compatibilité avec une architecture API.** React est particulièrement adapté à une application dont le backend est une API REST. Le frontend React enverra des requêtes HTTP à FastAPI et affichera les réponses JSON. Cette séparation facilitera le développement, les tests et l’évolution des deux parties de l’application.

6. **Évolution possible vers une application mobile.** React offre une voie d’évolution vers une solution mobile, notamment avec React Native. Cette option ne sera pas nécessaire pour la première version, mais elle rend le choix plus durable à long terme.

## Inconvénients

1. **Courbe d'apprentissage**. L'apprentissage de React (syntaxe, ressources disponibles) peut prendre un certain temps, ce qui augmente le temps de développement nécessaire pour implémenter les premières fonctionnalités.

2. **Outils de développement externes**. React nécessite le recours à des outils additionnels. Bien que cela entraîne une plus grande liberté, cela complexifie le processus de développement.

3. **Absence de data binding.** Contrairement à certains frameworks comme Vue.js, React n’offre pas de data binding intégré. La synchronisation entre les champs d’un formulaire et l’état de l’application devra donc être gérée explicitement à l’aide de `useState` et de gestionnaires d’événements.

## Alternatives rejetées

### Vue.js

Vue.js est une alternative intéressante à React. Il offre une syntaxe simple, une bonne documentation et une liaison de données bidirectionnelle pratique pour la gestion des formulaires.

React a été retenu en raison de son écosystème plus large, de la quantité plus importante de ressources disponibles et de sa popularité auprès des développeurs. React est également mieux aligné avec l’approche API envisagée, où le frontend communique avec un backend FastAPI par des requêtes HTTP et des données JSON.

### Application native avec Kotlin

Une application native développée avec Kotlin offrirait de bonnes performances et un accès direct aux fonctionnalités du système, particulièrement sur Android. Kotlin est également un langage moderne, sûr et agréable à utiliser.

Toutefois, une application native Android ne serait pas directement disponible sur iOS. Il faudrait donc développer une seconde application ou utiliser une solution multiplateforme supplémentaire. Elle ne répond pas non plus aux exigences du projet, soit une application Web en premier lieu.

## Conclusion

React sera utilisé pour concevoir le frontend de mon application. Bien qu'elle présente une courbe d'apprentissage, elle comprend plusieurs bénéfices adaptés à mes besoins pour sa performance, son fonctionnement et sa flexibilité.
