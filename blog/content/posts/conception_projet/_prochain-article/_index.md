# Le endpoint goal_preview

Je n'avais pas réfléchi à cette particularité en construisant mon backend. Je me suis aperçu que des fonctions étaient manquantes dans le service de Onboarding. C'est le cas d'une fonction permettant de récupérer un objectif de poids et une mesure de rhythme (lent, modéré, rapide) pour calculer une date de fin estimée. Cette information doit d'ailleurs être retournée au frontend pour informer l'utilisateur de ces données avant qu'elles ne soient sauvegardés dans la base de données.

En discutant avec l'IA, elle me suggère de créer un nouveau endpoint, soit `goal-preview`, qui vise à obtenir les données à afficher dans le récapitualtif.

## Conversation avec l'IA

#### _Question :_ J'avais comme idée que le frontend récupère les données à GoalStep et les fais parvenir au backend, qui effectue un calcul pour retourner les valeurs désirées pour le récapitulatif. Le backend s'occupe de faire le calcul de combien de temps il parviendra à atteindre son but et le retourne au frontend. Est-ce que tu crois que c'est une bonne pratique?

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

Et retourner :

```python
class GoalPreviewRead(BaseModel):
    goal_type: GoalType
    current_weight_kg: Decimal
    target_weight_kg: Optional[Decimal]
    pace: Optional[GoalPace]
    estimated_weeks: Optional[Decimal]
    estimated_completion_date: Optional[date]
    maintenance_calories_kcal: Decimal
    first_target_calories_kcal: Decimal
    calories_adjustment_kcal: Decimal
    protein_target_g: Decimal
    carbs_target_g: Decimal
    fat_target_g: Decimal
```

## Analyse

L'IA me suggère ensuite les informations que le backend devrait retourner. J'ai décidé de réduire la quantité d'informations, puisque certaines données ne seront pas affichées à l'utilisateur dans le récapitulatif.

# Synchronisation des endpoints API

Un défi que j'ai rencontré en concevant le frontend était la gestion des endpoints des deux côtés de l'application. Les réponses de l'IA song parfois erronées, ce qui fait qu'elle me propose des endpoints inexistants lorsqu'elle construit mes fonctions. J'ai donc chercher une solution afin d'automatiser la synchronisation des endpoints pour éviter d'avoir à les hardcoder dans mon service à chaque fois. Initialement, j'avais pensé à créer un seul fichier contenant tous les chemins API utilisés par mon backend dans un format JSON, par exemple. Celui-ci serait accessible des deux côtés de l'application. Finalement, après avoir évalué mes options, j'ai opté pour une configuration qui utilise OpenAPI et Orval.

## L'ajout de scripts

Pour commencer, j'ai dû ajouter des scripts à mon fichier `packages.json` :

```
"generate:api": "orval --config ./orval.config.ts",
"api:export": "cd ../backend/src/betterself && python scripts/export_openapi.py",
"api:sync": "npm run api:export && npm run generate:api"
```

Ainsi, quand j'exécute le script avec la commande `npm run api:sync`, le frontend se synchronise avec mon backend pour me permettre d'utiliser ses fonctions et ses modèles de données. Ceci est rendu possible grâce à FastAPI. Quand je lance mon backend, OpenAPI génère un fichier qui décrit toutes les données utilisables. Le script exécute ensuite Orval, qui récupère ce fichier pour créer des fonctions utilisables dans mon frontend. Cela me permet d'effectuer mes requêtes API avec Axios. Du côté d'Axios, il vérifie simplement que l'utilisateur possède un `access_token` valide avant d'acheminer la requête. 

# Les limitations de l'IA externe

Plus je progresse dans le développement des nouvelles fonctionnalités, plus je réalise que l'IA doit connaître les aspects techniques de mon projet pour me proposer du code approprié à mon architecture. C'est ainsi que j'ai dû adapter mon approche en renonçant à l'usage d'une IA externe à mon projet. En effet, en l'absence du contexte, les erreurs faites par Perplexity étaient de plus en plus fréquentes, ce qui suscitait des enjeux de performance.

## Intégration de Claude Code

Dans son ensemble, la structure du projet est définie. J'ai donc décidé d'intégrer Claude à mon environnement de travail en lui permettant d'apporter des modifications à mon projet. 

### Avantages

Contrairement à Perplexity, Claude aura accès au contexte du projet pour écrire les fonctions dont j'ai de besoin. Il pourra ainsi consulter les fonctions déjà présentes afin d'en produire de nouvelles basées sur les décisions techniques que j'ai pris jusqu'à présent. Le but est surtout de progresser plus rapidement, tout en gardant le contrôle du code produit par l'IA. 