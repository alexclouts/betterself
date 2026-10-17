# ADR: Choix du language Python

## Contexte

Nous devons décider si le language Python est adapté à la conception de notre application. Le projet inclut l'analyse et l'enregistrement de données, des requêtes à une API externe (Open Food Facts), l'authentification des utilisateurs et le développement Web.

## Décision

J'ai décidé d'utiliser Python comme principal language de programmation pour ce projet.

## Avantages

- **Usages similaires au projet.** Python est couramment utilisé dans des domaines tels que l’analyse de données, l’apprentissage machine et le développement Web. Sa syntaxe est facile à lire et à comprendre, ce qui facilite la maintenance du code.

- **Support de la communauté.** Python bénéficie d’une grande communauté de développeurs. De nombreuses ressources sont disponibles en ligne pour résoudre les problèmes fréquents et trouver des exemples d’intégration avec FastAPI, SQLAlchemy ou Pydantic.

- **Langage évolutif.** Python peut être utilisé aussi bien pour des applications simples que pour des systèmes plus complexes. Cette flexibilité facilite le développement itératif de l'application.

- **Écosystème adapté aux API.** FastAPI, Pydantic, SQLAlchemy et pytest forment un ensemble cohérent pour développer, valider, persister et tester les données de l’application.

- **Facile d’intégration avec des API externes.** Python offre des bibliothèques simples pour effectuer des requêtes HTTP, notamment `httpx` ou `requests`. Cela est pertinent pour interroger Open Food Facts.

- **Grande compatibilité.** Python peut interagir avec plusieurs technologies et langages, notamment Java et C++. Cette compatibilité pourrait être utile si le projet évolue vers des fonctionnalités plus spécialisées, comme l’analyse de données ou l’apprentissage machine.

## Inconvénients

- **Performance réduite.** Python est généralement moins performant que Java, C# ou C++ pour des charges de calcul plus importantes. Toutefois, cette limite n'aura pas des impacts significatifs pour l'application.

- **Compatibilité des versions Python.** Selon la version utilisée, la syntaxe et les capacités du language peuvent varier, ce qui représente un défi pour la mise à jour et l'entretien du projet. Par conséquent, il faut porter une attention au choix de la version à préconiser.

## Conclusion

Après avoir considéré les avantages et les inconvénients reliés au choix du language, il est convenu que Python représente la meilleure option grâce à sa grande flexibilité, ses cas d'utilisation typiques et un écosystème adapté aux requêtes API.
