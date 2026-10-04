---
title: "Mais qui êtes-vous ?"
header: ""
date: 2026-10-03T22:10:00.000Z
description: "Processus d'authentification des utilisateurs, sécurité et gestion des sessions."
tags:
  - Authentification
  - SQL
categories:
  - Cadrage et recherche
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

Même si l’application ne manipule pas de données médicales sensibles, elle contiendra tout de même des informations personnelles : adresse courriel, poids, objectifs, historique alimentaire de l'utilisateur, etc. Il est donc important de mettre en place une méthode d'authentification simple et suffisamment solide.

## Une nécessité

Chaque utilisateur devra pouvoir créer son propre compte afin que personne d'autre ne puisse modifier ses repas, ses objectifs et ses statistiques. L’authentification permettra aussi de relier chaque donnée enregistrée à un utilisateur précis.

Sans authentification, l'application ne pourrait offrir qu’un usage local, ce qui limiterait fortement l’intérêt de l’application. Par exemple, un utilisateur ne pourrait pas récupérer ses données enregistrés sur un autre appareil. Si son appareil est réinitialisé, il perderait aussi toute sa progression. Avec des comptes utilisateurs, il devient possible de conserver un historique, de personnaliser les objectifs caloriques tout en protégeant les données personnelles.

## Courriel et mot de passe

Ma méthode principale sera l’inscription classique par adresse courriel et mot de passe. Lors de la création d’un compte, l’utilisateur fournira une adresse courriel et un mot de passe. Le backend vérifiera que l’adresse n’est pas déjà utilisée, puis créera le compte. Il se pourrait que je décide d'intégrer l'authentification avec un compte Google, qui offre un API permettant d'utiliser la fonctionnalité **Single Sign-On**, favorisant une expérience client plus optimale. Par contre, pour un premier déploiement, l’authentification par courriel et mot de passe reste plus simple à comprendre, à tester et à sécuriser. Elle pourra ensuite être complétée par une connexion externe si le projet évolue.

### Sécurité

Le mot de passe ne sera jamais enregistré en clair dans la base de données. Il sera transformé à l’aide d’une fonction de hachage lente et _salée_, comme **Argon2id** ou **bcrypt**. `OWASP` recommande précisément ce type d’algorithme pour le stockage des mots de passe, car ils sont conçus pour ralentir les attaques _bruteforce_ si la base de données est compromise. À la connexion, le backend comparera le mot de passe fourni au hachage enregistré. Si les deux correspondent, l’utilisateur sera considéré comme authentifié par l'application.

#### Méthode de hachage

Le **hachage** est une transformation à sens unique : à partir du mot de passe, on obtient une chaîne difficile à inverser. Ainsi, même si quelqu’un accède à la base de données, il ne verra pas les mots de passe réels. J’utiliserai un sel unique généré automatiquement pour chaque utilisateur. Le sel empêche deux personnes ayant le même mot de passe d’avoir le même hachage et complique l’utilisation de tables précalculées, comme les _rainbow tables_. En pratique, le backend utilisera une [bibliothèque Python spécialisée](https://pypi.org/project/argon2-cffi/) plutôt que de devoir implémenter le hachage moi-même au sein du projet. Cela simplifiera le fonctionnement du code et facilitera sa mise en oeuvre.

## Jetons JWT

Après une connexion réussie, le backend émettra un jeton d’accès de type **JWT** (_JSON Web Token_). Le frontend enverra ensuite ce jeton dans l’en-tête `Authorization` de chaque requête nécessitant d’être authentifié. D'ailleurs, FastAPI documente ce modèle avec le flux OAuth2 « password »,. Le client envoie un identifiant et un mot de passe afin de recevoir un jeton d’accès, puis utilise ce jeton comme preuve d’authentification pour les requêtes suivantes.

Un JWT contiendra :

- l’identifiant de l’utilisateur;
- la date d’expiration du jeton;
- son rôle ou ses permissions;
- une signature permettant au backend de vérifier que le jeton n’a pas été modifié.

J’utiliserai des jetons d’accès à durée courte. Cela limite les conséquences si un jeton est volé, puisqu’il deviendra rapidement invalide. OWASP recommande aussi de valider la signature, l’émetteur et l’audience d’un jeton, ainsi que de gérer correctement sa durée de vie.

### Stockage du jeton

Pour la première version, je privilégierai un cookie sécurisé de type `HttpOnly` plutôt que le `localStorage`. Un cookie `HttpOnly` n’est pas accessible directement par JavaScript, ce qui réduit le risque de vol du jeton en cas d’attaque XSS. OWASP recommande de ne pas conserver les jetons d’authentification dans des emplacements non sécurisés du navigateur et privilégie les cookies `HttpOnly` ou des mécanismes de stockage sécurisés.

Le cookie sera configuré avec :

- `Secure`, pour qu’il ne soit envoyé qu’en HTTPS;
- `HttpOnly`, pour le protéger de l’accès JavaScript;
- `SameSite`, pour réduire certains risques liés aux requêtes intersites;
- une expiration qui suit la durée de vie du jeton.

### Jetons de rafraîchissement

Pour éviter de demander à l’utilisateur de se reconnecter trop souvent, j’envisage d’ajouter un _refresh token_. Le principe est simple : le jeton d’accès expire rapidement, tandis qu’un jeton de rafraîchissement, plus long, permet d’obtenir un nouveau jeton d’accès sans redemander le mot de passe. Par contre, OWASP souligne l’importance d’une stratégie sécurisée de rotation des jetons de rafraîchissement et d’une validation rigoureuse des jetons. Dans un premier temps, je pourrais commencer avec des sessions relativement courtes, puis ajouter cette fonctionnalité lorsque le reste de l’application sera stable.

## Les erreurs courantes

Voici une liste des choses que je devrai respecter au sujet de l'authentification pendant le développement du projet :

- Ne jamais retourner un message indiquant si c’est le courriel ou le mot de passe qui est incorrect; le message sera simplement « identifiants invalides ».
- Limiter le nombre de tentatives de connexion.
- Utiliser HTTPS en production pour protéger les identifiants et les jetons.
- Ne pas enregistrer les mots de passe, les jetons ou les secrets de signature dans le code source.
- Conserver les variables sensibles dans des variables d’environnement.

OWASP recommande notamment d’éviter les changements périodiques forcés de mot de passe, mais d’encourager des mots de passe robustes et, lorsque c’est pertinent, l’activation de l’authentification multifacteur.

## MFA

La **MFA** _(Multi Factor Authentication)_ ne sera pas présente dans la première version, car elle ajoute de la complexité pour l’utilisateur et pour le développement. Cependant, elle constitue une étape à privilégier une fois que les fonctionnalités principales seront en place. La MFA est particulièrement efficace contre les **attaques liées aux mots de passe**, comme le _credentials stuffing_, les attaques de _bruteforce_ ou le _password spreading_. Pour l'application, une méthode de sécurité pourrait être un code à usage unique envoyé par courriel lors d’une connexion depuis un nouvel appareil. Elle serait également implémenté plus tard durant le développement.

## En résumé

En bref, je vais commencer avec une authentification par courriel et mot de passe, avec des mots de passe hachés à l’aide d’un algorithme adapté, des jetons JWT à courte durée et un stockage sécurisé pour le navigateur. Les jetons de rafraîchissement et la MFA représenteront des améliorations progressives qui s'implémenteront après la première version, si le projet se poursuit.

L’objectif est de garder une solution compréhensible et maintenable, tout en appliquant dès le départ les bases importantes de la sécurité.

[Retour](http://localhost:1313/posts/)
