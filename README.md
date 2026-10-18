# Vision du client

### L'utilisateur typique

Je suis quelqu'un qui fait le suivi des aliments que je consomme au quotidien dans le but d'atteindre mon poids idéal. Ainsi, je fais attention à ce que je mange, car je veux perdre de poids ou prendre de la masse musculaire. À chaque jour, je pèse mes aliments pour connaître leur apport calorique et le nombre de macronutriments (protéines, glucides et lipides) qu'ils contiennent. Puisque je veux perdre du poids, mon but est de créer un léger déficit calorique à chaque jour par rapport à mon nombre de calories de maintenance. Je veux aussi connaître le nombre de protéines que j'ai ingéré durant la journée. Je veux pouvoir comparer ce nombre avec mon objectif initial pour faire le suivi de ma progression et atteindre mon objectif.

### Le problème résolu

Faire le suivi de tous ses repas est souvent une tâche fastidieuse, surtout lorsqu'on s'attarde au nombre de calories ingérées. On peut regarder sur l'emballage et faire le calcul à la main, mais cette méthode provoque des erreurs. C'est aussi une tâche complexe, car le poids des aliments entre aussi en ligne de compte. En ce moment, je dois inscrire toutes les valeurs nutritionnelles manuellement. Ça prend un temps considérable dans ma journée et ça me décourage.

### La solution offerte

Je voudrais donc avoir accès à une application Web simple et intuitive qui me permettrait d'enregistrer rapidement mes aliments et mes repas. Quand je consomme un produit alimentaire emballé, j'aimerais pouvoir utiliser son code-barre afin d'obtenir automatiquement ses informations nutritionnelles plutôt que de devoir les saisir manuellement à chaque fois. Si le code-barre n'est pas reconnu, je voudrais l'enregistrer manuellement dans l'application.

L'application me permettrait aussi de créer des repas regroupant plusieurs aliments et de conserver un historique de ma consommation. Je pourrai donc consulter ce que j'ai consommé au cours d'une journée donnée et avoir une vue d'ensemble de mon alimentation. Je souhaiterais également pouvoir consulter les macronutriments associées aux aliments que j'ai enregistrés afin de mieux comprendre mes habitudes alimentaires et comparer ma consommation avec mes objectifs personnels.

Pour que l'utilisation de l'application soit pratique au quotidien, mes données devraient être associées à un compte personnel. Je pourrais ainsi retrouver mon historique alimentaire chaque fois que j'utilise l'application, sans avoir à recommencer la saisie de mes informations. L'application devrait également présenter les informations de manière claire afin que je puisse rapidement comprendre ma consommation sans avoir à parcourir une grande quantité de données.

La solution envisagée est donc une application Web de suivi alimentaire qui permet à l'utilisateur :

- De rechercher des produits alimentaires;
- De les identifier à l'aide de leur code-barre;
- D'enregistrer les aliments consommés;
- De consulter leur valeur nutritionnelle ainsi que leur historique alimentaire.

Une base de données permettrait de conserver les informations propres à chaque utilisateur, tandis qu'un service externe comme Open Food Facts fournirait les informations sur les produits alimentaires. L'objectif principal serait de rendre le suivi de l'alimentation plus rapide, accessible et facile à maintenir au quotidien.

# Déploiement

## Pipeline CI

L’intégration continue (CI) exécute automatiquement les tests du backend à chaque push ou pull request vers la branche `main`. La configuration se trouve dans `.github/workflows/ci.yml`.

### Lancement des tests

Depuis la racine du projet :

```bash
cd backend
uv sync
uv run pytest
```

- `uv sync` installe les dépendances et met à jour l’environnement virtuel local selon `uv.lock`.
- `uv run pytest` exécute les tests avec l’environnement du backend.
