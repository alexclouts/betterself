---
title: "Intégrer le Barcode Reader"
header: ""
date: 2026-11-27T21:12:00.000Z
description: "Les enjeux liés à la mise en place et aux tests du lecteur de code-barres, et gestion des unités de mesures personnalisées aux aliments."
tags:
  - IA
  - Code-barres
  - Mesures
  - Aliments
  -
categories:
  - Fondations
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Intégrer le Barcode Reader

L'article de cette semaine discute de la mise en place du lecteur de code-barres. Je présente les défis liés à la réalisation des tests sur un appareil mobile dans un environnement local. De plus, j'analyserai les limites de l'utilisation d'une base de données publique pour la gestion des données, surtout en ce qui concerne les unités de mesure non normalisés.

Vous pouvez également consulté la [Vidéo 6: Lecteur de code barres et la fin qui approche](https://youtu.be/n5oUSrrmOo4) où je vous fait une courte démonstration du projet en cours.

## Les tests

Le lecteur de code-barres est une fonctionnalité très pratique au quotidien afin de rechercher rapidement des aliments sans avoir à trier les résultats nous-mêmes. Les enjeux que j'ai rencontré portent surtout sur les manières de tester cet outil sur différents appareils (Android et iOS). Ma première idée était de déployer l'application sur mon réseau local, ce qui aurait permis à tous mes appareils de lui accéder facilement depuis le navigateur. Cependant, l'accès à la caméra n'est pas possible sur le protocole `HTTP`. Il faut obligatoirement une connexion sécurisée ou passer par le `localhost`.

## Premier pas sur mobile

Avec Android, c'est plutôt facile de passer par le **localhost** grâce à la possibilité de configurer un _port forward_ sur mon appareil lorsqu'il est branché sur un port USB. Depuis le navigateur Chrome, le endpoint `chrome://inspect/#devices` m'a permis de _forwarder_ le port 8080 sur mon téléphone. Grâce à cela, j'ai pu voir les premières images de l'application et vérifier que le lecteur fonctionnait bien.

### Maintenant, sous iOS

À la maison, un iPad me permettrait de tester cette fonctionnalité sous iOS. J'ai donc questionné Claude pour connaître la procédure.

#### _Question :_ J'ai connecté un iPad via USB-C. Peux-tu me guider sur la façon de faire pour activer le port forwarding?

Avec un iPad branché sur Linux, il n'existe pas d'équivalent au « port forwarding » de Chrome pour Android (`chrome://inspect`, ou `adb reverse`). Ces outils permettent au téléphone de joindre le `localhost` du PC, mais iOS n'offre rien de comparable. `iproxy` (libimobiledevice) fait seulement l'inverse : il donne au PC un accès à un port de l'iPad. Le câble USB-C ne permettra donc pas à Safari d'ouvrir `localhost:5173`.

Je recommande de passer par le Wi-Fi, en HTTPS. Ton PC est à 192.168.2.211 ; l'iPad doit être sur le même réseau.

## Analyse

Suite à ces recommandations, l'environnement de test est accessible à partir de tous les appareils connectés sur mon réseau local. J'ai d'ailleurs pu tester le lecteur de code-barres à quelques occasions durant la journée.

# Problème de lecture

Le navigateur par défaut que j'utilise sur mon téléphone est Google Chrome. En essayant de scanner un article, l'application n'arrivait pas à lire le code-barres.

{{< img
src="troubleshooting1.png"
alt="Troubleshooting 1"
caption=""
width="800">}}

C'est à ce moment que **Claude** m'a fait remarqué que mon test utilisait probablement le lecteur Android intégré au lieu de _ZXing_. Je me suis souvenu que c'était effectivement probable quand j'ai révisé le code du dernier _pull request_ :

```typescript
export function getBarcodeDetector(): Promise<Detector> {
  detectorPromise ??= (async () =>
    (await createNativeDetector()) ?? createPolyfillDetector())().catch(
    (error: unknown) => {
      detectorPromise = null;
      throw error;
    },
  );
  return detectorPromise;
}
```

L'IA m'a donc suggéré de tester la lecture du même produit en utilisant le navigateur **Firefox**, car celui-ci n'a pas de lecteur intégré, ce qui l'oblige à utiliser _ZXing_ de Polyfill. Cette fois-ci, la lecture a fonctionné.

#### _Question :_ Pourquoi ne pourrais-je pas seulement utiliser la bibliothèque du Polyfill au lieu d'utiliser le lecture intégré dans certains cas?

Utiliser seulement ZXing est une option tout à fait défendable, et dans ton cas je pense que c'est le meilleur choix.

### Pourquoi ZXing seul a plus de sens ici

- **La preuve est sous tes yeux**. Sur ton propre produit, le lecteur intégré a échoué et ZXing a lu le code du premier coup. L'avantage théorique de tolérance ne s'est pas vérifié.
- **Un seul comportement partout**. Aujourd'hui, Android utilise un lecteur, et iPhone, iPad et Firefox en utilisent un autre. Avec ZXing partout, tes tests sur Android valent aussi pour iPhone, que tu ne peux pas tester toi-même. C'est sans doute l'argument le plus fort.
- **Plus simple**. La détection du lecteur intégré disparaît (`createNativeDetector`, la vérification des formats), ainsi que l'idée d'une solution de secours entre deux lecteurs. Il reste un seul chemin à comprendre et à déboguer.
- **Le lecteur intégré dépend de Google Play Services**. Son comportement peut changer d'une version à l'autre, et certains Android sans services Google ne l'ont pas du tout.

## Analyse

Cette démonstration est un argument de plus que je vais utiliser afin d'écrire l'ADR pour le choix de la technologie utilisée.

## Amélioration du UI/UX

C'est définitivement ma partie préférée de la conception. J'aime organiser les éléments entre eux pour que l'information soit facile d'accès, mais que l'application conserve son côté esthétique.

Les deux _pull requests_ #33 et #35 sont ceux qui ont modifié l'interface davantage. Étant donné qu'elles visaient surtout à organiser le UI différemment et que ces changements avaient peu d'incidence sur la logique et la sécurité de l'application, je dois admettre que je n'ai pas révisé la plupart de ces commits pour sauver du temps, mais le rendu final est ce qui compte vraiment lorsqu'on s'attarde au UI.

# Les étapes avant la fin

On a désormais franchi la dernière étape d'un produit complet dans son ensemble avec les fonctionnalités promises dans le `README.md`. Elle serait prête à être déployé si le but était seulement de l'utiliser localement sans gestion des utilisateurs ou de solution d'hébergement. Par contre, un dernier problème doit être adressé avant la remise finale, soit celui des **unités de quantité d'un aliment**. C'est un problème qui m'a réellement causé du tord lorsque j'ai utilisé l'application pour les premières fois. Dans la vie de tous les jours, je ne pèse pas tous mes aliments à chaque repas. J'ignore le poids d'une tranche de pain, par exemple. Pour avoir une meilleure expérience, j'aimerais pouvoir entrer la quantité "_2 tranches_" au lieu de 86 grammes.

## Une tranche de pain

J'ai d'abord questionné Claude pour savoir si _OpenFoodFacts_ conservait des unités de mesure propres à l'aliment. Après sa recherche, voici ce qu'il m'a répondu :

### Réponse de Claude

Ce qu'Open Food Facts fournit

- `serving_size` est du texte libre saisi par les contributeurs. Il n'y a ni champ d'unité structuré ni liste fixe d'unités.
- `serving_quantity` est le poids de la portion en grammes (ou en ml), déduit de ce texte. Ton catalogue n'importe que ce chiffre, sous `serving_g`. La table products de off.sqlite n'a aucune colonne pour le texte.

#### Les difficultés

- **Langue** : la plupart des unités sont en anglais (« slices », « cookies »), d'autres en français (« tranches », « morceaux », « tasse »). Il faudrait un petit dictionnaire pour les afficher en français.
- **Nombre et grammes** : dans « 2 slices (50 g) », la portion compte 2 unités. Une tranche pèse donc 25 g, pas 50 g.
- **Unités ambiguës** : « portion », « serving » et « unit » n'apportent rien de plus que les grammes. « cup » et « tbsp » sont des mesures de volume, pas des unités de l'aliment.
- **Bruit** : le texte vient des contributeurs. On voit des formes comme « 250 ml (250 ml) », « 1/2 cup » ou « 14 cm cube ».

### Analyse

Cette simple fonctionnalité est plus complexe qu'elle ne le semble. Claude m'a proposer de reconstruire le catalogue fait à partir des données de _OpenFoodFacts_ pour lire `serving_size`. Le modèle mis à jour permettrait de récupérer un nom d'unité au singulier en français ainsi que le poids d'une unité. Cette refonte nécessite aussi de modifier ma table SQL d'un aliment afin que ces données soient stockées lors de la sauvegarde de l'entrée.

# Construire un dictionnaire

Cette étape est surprenante, mais c'est ici que l'IA fait toute la différence. La première étape proposée par l'IA est de construire un dictionnaire de toutes les unités acceptées par mon application. Pour ce faire, elle fait le comptage de tout l'_export_ et génère les unités retenues avec leur correspondance en français. Elle m'a ensuite présenté les résultats obtenus.

Un des enjeu portait sur les informations offertes dans la description de l'aliment. Certains aliments ont dû être écarté, puisque le poids ou le volume n'est pas indiqué dans l'entrée. Selon moi, c'est important d'avoir cette information pour que l'application puisse interpréter les données de la bonne manière. Dans certains cas, une conversion approximative de `tbsp` = `15 mL` = `15 g` peut être fait pour permettre à l'utilisateur d'entrer la quantité de nourriture réellement consommée sans être limité par une suggestion trop restreinte. Il fallait donc que je détermine où trancher la ligne entre les données que j'accepte et celles qui n'ont pas assez d'informations sur l'aliment.

## Pousser plus loin

Après la mise en place de cette fonctionnalité, je me suis aperçu que la plupart des aliments de _OpenFoodFacts_ n'avait pas les unités attendues. Par exemple, si je tappe `Lait` dans la barre de recherche, je devrais m'attendre à pouvoir choisir une quantité en **tasse** ou en **mililitre**.

{{< img
src="screenshot1.png"
alt="Screenshot 1"
caption=""
width="800">}}

J'ai donc présenté ce problème à Claude et il m'a fait une suggestion intéressante.

### Réponse de Claude

Pour un liquide, les grammes ne sont pas l'unité naturelle. Le catalogue sait déjà reconnaître les liquides, grâce à `categories_tags` (en:milks, en:beverages, en:juices, en:plant-based-milks…). Deux options :

A. **Une tasse par défaut, dans le catalogue (simple)**. Un liquide sans unité reçoit « tasse » (250 ml ≈ 250 g), marquée comme estimée. Le volume seul (« 250 ml ») deviendrait aussi « tasse » s'il s'agit d'un liquide.

- Ça s'intègre au modèle actuel, avec une seule unité par aliment.
- Il suffit de reconstruire le catalogue, sans toucher au frontend.

B. **Les millilitres en plus de l'unité (plus complet)**. Les liquides proposent aussi « `ml` » dans le menu, par exemple « g, ml, tasse », avec 1 ml ≈ 1 g et la mise en garde.

- Il faut un indicateur « liquide » sur l'aliment (nouvelle migration), et le menu doit gérer plusieurs unités.
- C'est plus naturel pour saisir « 200 ml de lait ».

### Analyse

Après lui avoir demandé d'appliquer l'option A, Claude a introduit des règles de conversion entre les unités de mesure pour interpréter les données d'_OpenFoodFacts_. Un message de mise en garde informe à présent l'utilisateur quand certaines données sont calculées selon une grille de correspondance par défaut dans l'application.

Après quelques itérations au sein de la branche `feature/unites-aliments`, la fonctionnalité répond à l'idée que j'avais en tête. À présent, lorsqu'un aliment est considéré comme un liquide, l'application permettra à l'utilisateur de choisir parmi les unités de **tasse**, **cuillère à soupe** et **cuillère à thé**.

## Prochaine étape

En ce qui concerne les services offerts par l'application, je considère que la V1 est officiellement terminée. Il reste uniquement à mettre en place un mécanisme pour confirmer l'adresse courriel associé au compte de l'utilisateur et générer une politique de confidentialité afin de l'informer de la manière dont nous collecterons ses données personnelles. Ensuite, il sera question de gérer l'hébergement de l'application pour la remise finale.

[Retour](https://alexclouts.github.io/betterself/posts/)
