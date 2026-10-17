# ADR: Choix d’une méthode d’authentification

## Contexte

L'application doit permettre aux utilisateurs de créer un compte, de se connecter avec leur courriel et leur mot de passe, puis d’accéder uniquement à leurs propres données. L’application conservera des informations personnelles et de santé, notamment le poids, la grandeur, la date de naissance, les objectifs nutritionnels et les consommations alimentaires.

Le backend FastAPI doit donc pouvoir :

- créer un compte utilisateur
- valider un courriel et un mot de passe lors de la connexion
- hacher les mots de passe avant de les enregistrer
- identifier l’utilisateur associé à chaque requête protégée
- empêcher un utilisateur d’accéder aux données d’un autre utilisateur
- permettre la déconnexion
- protéger les endpoints sensibles de l’API

Le frontend React devra envoyer les informations d’authentification au backend, conserver le jeton reçu et l’inclure dans les requêtes suivantes.

## Options considérées

- Authentification par session avec cookies
- Authentification par jeton JWT
- Authentification déléguée à un fournisseur externe (Google, GitHub, etc.)
- Authentification de base HTTP (Basic Auth)

## Décision

L’authentification sera réalisée avec des **jetons JWT (JSON Web Tokens)**.

Lors de la connexion, le backend FastAPI validera le courriel et le mot de passe. Si les informations sont correctes, il générera un jeton JWT signé et le retournera au frontend React. Le frontend conservera ce jeton et l’inclura dans l’en-tête `Authorization` des requêtes protégées.

## Avantages

- **Architecture adaptée à une application API.** Les jetons JWT conviennent bien à une application composée d’un frontend React et d’un backend FastAPI séparés. Le frontend peut envoyer le jeton à chaque requête sans dépendre d’une session côté serveur.

- **Backend sans état.** Le backend n’a pas besoin de conserver une session en mémoire pour chaque utilisateur connecté. L’identité de l’utilisateur peut être vérifiée à partir du jeton signé reçu dans la requête.

- **Simplicité d’intégration avec React.** Le frontend peut conserver le jeton reçu après la connexion, puis l’ajouter automatiquement aux requêtes HTTP vers les endpoints protégés.

- **Contrôle des permissions.** Le backend pourra vérifier l’identité de l’utilisateur à partir du jeton et appliquer des règles d’autorisation. Par exemple, un utilisateur ne pourra consulter ou modifier que ses propres mesures corporelles et objectifs nutritionnels.

- **Expiration configurable.** La durée de vie du jeton pourra être limitée. Cela réduit le risque associé au vol d’un jeton, puisqu’un jeton expiré ne sera plus accepté par le backend.

- **Extensibilité.** Le système pourra évoluer vers l’ajout de rôles, de permissions ou de rafraîchissement de jetons si l'application devient plus complexe.

## Inconvénients

- **Risque associé au stockage du jeton.** Si le jeton est conservé dans le `localStorage`, il peut être accessible à du code JavaScript malveillant en cas de faille de sécurité dans le frontend. Une approche plus sécurisée consiste à utiliser un cookie `HttpOnly`, `Secure` et `SameSite`, ou à limiter la durée de vie des jetons.

- **Difficulté de révocation immédiate.** Un JWT reste valide jusqu’à son expiration, sauf si le backend met en place une liste de révocation ou un mécanisme de jetons de rafraîchissement. La déconnexion ne supprime donc pas automatiquement la validité d’un jeton déjà émis.

- **Complexité supplémentaire.** La gestion des jetons nécessite de choisir une clé secrète ou une paire de clés, de définir une durée d’expiration et de gérer les erreurs liées aux jetons invalides ou expirés.

- **Protection des secrets nécessaire.** La clé utilisée pour signer les jetons doit être conservée hors du code source, par exemple dans une variable d’environnement. Si cette clé est compromise, un attaquant pourrait générer des jetons valides.

## Alternatives rejetées

### Authentification par session avec cookies

L’authentification par session est simple et sécurisée lorsque les cookies sont correctement configurés. Toutefois, elle nécessite que le backend conserve l’état des sessions ou utilise un mécanisme de stockage de sessions. Cette approche est viable, mais les jetons JWT offrent une intégration plus directe avec une architecture React + FastAPI séparée.

### Authentification déléguée à un fournisseur externe

L’utilisation de Google, GitHub ou un autre fournisseur d’identité réduirait la charge liée à la gestion des mots de passe. Toutefois, cette solution dépend d’un service externe, complique la configuration initiale et n’est pas nécessaire pour la première version de BetterSelf. Elle pourrait être ajoutée plus tard comme méthode de connexion supplémentaire.

### Authentification de base HTTP

L’authentification de base HTTP envoie le courriel et le mot de passe encodés à chaque requête. Elle est simple à mettre en œuvre, mais moins adaptée à une application Web moderne, car elle n’offre pas de mécanisme pratique d’expiration, de déconnexion ou de renouvellement de session.

## Conclusion

L’authentification de BetterSelf sera réalisée avec des jetons JWT. Cette approche est adaptée à l’architecture séparée entre React et FastAPI, permet de protéger les endpoints de l’API et facilite l’identification de l’utilisateur à chaque requête.

Les risques associés aux JWT, notamment le stockage du jeton et sa révocation, seront atténués par une durée d’expiration limitée, une configuration sécurisée des cookies si nécessaire et une validation rigoureuse des jetons côté backend. Les mots de passe seront toujours hachés et ne seront jamais stockés en clair.
