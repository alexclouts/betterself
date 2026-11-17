---
title: "Les ramifications du frontend"
header: ""
date: 2026-11-16T21:06:00.000Z
description: "Nous aborderons mon passage de Perplexity à Claude Code et découvrirons différentes librairies qui augmente l'efficacité du code."
tags:
  - Frontend
  - Orval
  - OpenAPI
  - TanStack Query
  - Cache
  - IA
categories:
  - Conception du projet
---

{{< img
src="preview.png"
alt="Preview"
caption=""
width="500">}}

# Récapitulatif de l'objectif

Pendant le développement, je me suis aperçu que des fonctions étaient manquantes dans le service de Onboarding. C'est le cas d'une fonction permettant de récupérer un objectif de poids et une mesure de rhythme (lent, modéré, rapide) pour calculer une date de fin estimée. Je veux que cette information soit retournée au frontend pour offrir un récapitulatif à l'utilisateur avant que ces données ne soient sauvegardés.

En discutant avec l'IA, elle me suggère de créer un nouveau endpoint, soit `goal-preview`, qui vise à obtenir les données à afficher dans le récapitualtif.

## Conversation avec l'IA

#### _Question :_ J'avais comme idée que le frontend récupère les données à GoalStep et les fais parvenir au backend, qui effectue un calcul pour retourner les valeurs désirées pour le récapitulatif. Le backend s'occuperait de calculer combien de temps sera nécessaire pour atteindre son but et retourne la réponse au frontend. Est-ce que tu crois que c'est une bonne pratique?

Oui, ton idée initiale est la bonne pratique : le frontend envoie les **entrées brutes** de `GoalStep`, et le backend effectue le calcul puis retourne les valeurs du récapitulatif. Le frontend peut aussi calculer une estimation locale pour une expérience instantanée, mais il ne doit jamais être la source de vérité ni envoyer une valeur calculée que le backend considère comme fiable.

Le backend peut offrir un endpoint de prévisualisation, sans persister les données :

```python
@router.post("/goal-preview", response_model=GoalPreviewRead)
def preview_goal(
    payload: GoalStepData,
    current_user: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> GoalPreviewRead:
    return service.preview_goal(
        user=current_user,
        goal_data=payload,
    )
```

## Analyse

Je me suis inspiré du modèle `GoalPreviewRead` proposé par l'IA, mais j'ai décidé de réduire la quantité d'informations. Certaines données ne seront pas affichées à l'utilisateur dans le récapitulatif.

# Synchronisation des endpoints API

Un défi que j'ai rencontré en concevant le frontend était la gestion des endpoints des deux côtés de l'infrastructure. Comme abordé précédemment, les réponses de l'IA sont parfois erronées, ce qui fait qu'elle me propose des endpoints inexistants lorsqu'elle construit mes fonctions. J'ai donc chercher une solution afin d'automatiser la synchronisation des endpoints pour éviter d'avoir à les _hardcoder_ dans mon service à chaque fois. Initialement, j'avais pensé à créer un seul fichier qui hébergerait tous les chemins API utilisés par mon backend dans un format JSON. Celui-ci serait accessible par les deux côtés de l'application pour éviter de les répéter. Finalement, après avoir évalué mes options, j'ai opté pour une configuration qui utilise `OpenAPI` et `Orval`.

## L'ajout de scripts

Pour commencer, j'ai dû ajouter des scripts à mon fichier `packages.json` :

```
"generate:api": "orval --config ./orval.config.ts",
"api:export": "cd ../backend/src/betterself && python scripts/export_openapi.py",
"api:sync": "npm run api:export && npm run generate:api"
```

Quand j'exécute le script avec la commande `npm run api:sync`, le frontend se synchronise avec mon backend et me permet d'accéder à ses fonctions et à ses modèles de données. Ceci est rendu possible grâce à FastAPI. Quand je lance mon backend, OpenAPI génère un fichier qui décrit la structure du backend. Le script exécute ensuite Orval, qui récupère ce fichier pour créer des fonctions utilisables du côté frontend. Cela me permet d'effectuer mes requêtes API grâce à Axios. Axios vérifie simplement que l'utilisateur possède un `access_token` valide avant d'acheminer la requête et cette vérification se fait également lorsque la requête est reçue de l'autre côté.

# Les limitations de l'IA externe

Plus je progresse dans le développement des nouvelles fonctionnalités, plus je réalise que l'IA doit connaître les aspects techniques de mon projet pour me proposer du code approprié à mon architecture. C'est ainsi que j'ai dû adapter mon approche et finalement renoncer à l'usage d'une IA **externe** à mon projet. En effet, en l'absence du contexte, les erreurs faites par Perplexity étaient de plus en plus fréquentes, ce qui m'obligeait à apporter des correctifs de plus en plus fréquemment.

## Intégration de Claude Code

Dans son ensemble, la structure du projet est définie. J'ai donc décidé d'intégrer Claude à mon environnement de travail en lui permettant d'apporter des modifications à mon projet.

### Avantages

Contrairement à Perplexity, Claude aura accès au contexte du projet pour écrire les fonctions dont j'ai de besoin. Il pourra ainsi consulter les fonctions déjà présentes afin d'en produire de nouvelles basées sur les décisions techniques que j'ai pris jusqu'à présent. Le but est surtout de progresser plus rapidement, tout en gardant le contrôle du code produit par l'IA.

# TanStack Query

Une suggestion que m'a proposé Claude est de mettre en place _TanStack Query_ au sein du projet. Je ne connaissais pas cette bibliothèque, donc je lui ai demandé de m'expliquer son utilité.

Selon Claude, TanStack Query est une bibliothèque qui gère les données venant du serveur dans un application React. Elle s'occupe du chargement, de la mise en cache, le rafraîchissement et la synchronisation après une modification.

## Réponse de Claude

Actuellement, chaque chargement est traité par :

```python
const [data, setData] = useState(...);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  let cancelled = false;
  service.get().then(...).catch(...).finally(...);
  return () => { cancelled = true; };
}, [dayKey]);
```

Ça fonctionne, mais ça laisse des manques :

- **Pas de cache** : En passant de l'accueil au journal, la même journée est rechargée de zéro.
- **Pas d'invalidation** : Après un ajout, rien ne prévient les autres écrans que leurs données sont périmées.
- **Code répété** : Chaque page réécrit loading, erreur et annulation.

### Le même chargement avec TanStack Query

```python
const { data: entries = [], isLoading, error } = useQuery({
  queryKey: ["journal", dayKey],          // identifiant unique dans le cache
  queryFn: () => journalService.getEntriesForDay(dayKey),
});
```

### Les mutations (modifications)

```python
const queryClient = useQueryClient();

const deleteMutation = useMutation({
  mutationFn: (id: string) => journalService.deleteEntry(id),
  onSuccess: () => {
    // Toutes les données du journal seront rechargées là où elles sont affichées.
    queryClient.invalidateQueries({ queryKey: ["journal"] });
  },
});
```

Le `setEntries(current => current.filter(...))` du journal deviendrait inutile. L'accueil, le journal et toute autre page qui affiche la journée se mettraient à jour d'eux-mêmes.

### Ce que ça changerait pour le projet

1. **Installation et configuration**. `npm install @tanstack/react-query`, puis un <QueryClientProvider> autour de l'application dans `main.tsx`.

2. **useJournalDay**. Il deviendrait deux `useQuery` (entrées et cible) plus le useMemo des totaux, et ferait environ 15 lignes au lieu de 60.

3. **orval**. Il sait générer directement des hooks TanStack Query (`client: "react-query" dans orval.config`), par exemple un `useListFoodConsumptionsFoodConsumptionsGet(...)` prêt à l'emploi. Tu pourrais toutefois garder tes services, qui ajoutent les messages d'erreur en français et la conversion des dates. C'est l'option la plus simple.

## Analyse

Je comprends que cet outil est une évolution naturelle de mon projet. Sa mise en place me permettrait d'augmenter l'efficacité, réduire le nombre de lignes de code utilisées et d'ajouter des fonctions essentielles telles que la mise en cache et l'invalidation des données. Je n'avais pas encore trouvé de solution pour la gestion du cache, donc j'ai été agréablement surpris de m'apercevoir que Claude avait identifié ce besoin avant même que je lui en parle. Avec le nombre grandissant de pages et de services au sein de l'application, je crois que c'est une évolution naturelle de l'architecture. J'ai donc autorisé Claude à aller de l'avant avec _TanStack Query_.

# Le bug des résultats mélangés

La prochaine suggestion me proposait d'implémenter TanStack Query pour la recherche des aliments. Avant d'accepter sa recommandation, j'ai d'abord voulu comprendre ce que ça impliquait.

#### _Question :_ Quelle est l'avantage de migrer la recherche d'aliment vers TanStack Query?

## Réponse de Claude

Le `clearTimeout` annule bien la recherche tant qu'on tape. Mais une fois une requête partie, rien n'empêche sa réponse d'arriver après une recherche plus récente :

1. Tu tapes « **pom** » et tu fais une pause : la requête « pom » part.
2. Tu continues avec « **pomme** » : la requête « pomme » part.
3. Si « **pom** » répond en dernier (réseau lent, recherche plus large), setFoods affiche les résultats de « pom » alors que le champ contient « pomme ».

Avec TanStack Query, chaque terme a sa propre entrée de cache (`["foods", "search", "pomme"]`). La page affiche toujours les résultats du terme en cours, quel que soit l'ordre d'arrivée des réponses. TanStack Query fournit aussi un signal qui peut annuler la requête devenue inutile.

## Analyse

Cet exemple est également une réponse inattendue de la part de l'IA. Il m'aurait certainement fallu consacrer plusieurs heures à tester cette fonctionnalité afin d'identifier ce bug de style _race condition_, de comprendre sa cause et d'envisager une solution possible. Claude m'a aussi souligné plusieurs avantages, y compris la gestion du cache visant à optimiser les requêtes et à offrir une meilleure expérience UX en général :

- **Effacer des lettres**. Revenir de « pommes » à « pomme » affiche les résultats déjà connus, sans appel réseau.
- **Pas de clignotement**. Avec `placeholderData: keepPreviousData`, les anciens résultats restent visibles pendant le chargement des nouveaux, au lieu d'une liste vide.
- **Le retour depuis la page d'un aliment**. Aujourd'hui, query est un `useState`, donc quand tu choisis un aliment puis fais « ← Retour », le champ revient vide et la recherche est perdue. Le cache seul ne règle pas ça. Il faut aussi conserver le terme, par exemple dans l'URL (`/journal/add?q=pomme`). Combinés, on retrouve le terme et les résultats instantanément.

### Délai avant d'envoyer la requête

En configurant TanStack Query, Claude fera aussi l'ajout d'un petit hook ` useDebouncedValue` afin de conserver le délai de **300 ms** à respecter avant d'envoyer une nouvelle requête pour la recherche. Cette fonctionnalité sert surtout à éviter que des requêtes successives soient faites lorsque l'utilisateur est en train d'écrire dans la barre de recherche.
