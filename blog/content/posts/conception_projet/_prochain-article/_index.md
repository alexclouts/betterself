# Le endpoint goal_preview

Je n'avais pas réfléchi à cette particularité en construisant mon backend, peut-être parce que c'est difficile de réfléchir aux besoins du frontend avant de l'avoir commencé. Bref, je me suis apperçu que des fonctions étaient manquantes dans le service de Onboarding. C'est le cas de la fonction qui permet de récupérer un objectif de poids et une mesure de rhythme (lent, modéré, rapide) pour retourner une date de fin estimée. Cette information doit d'ailleurs être retournée au frontend pour informer l'utilisateur de ces données avant qu'elles ne soient sauvegardés dans la base de données.

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

Une problématique que j'ai rencontré en concevant le frontend était la gestion des endpoints des deux côtés de l'application. Souvent, l'IA génère du code en me proposant des endpoints inexistants. J'ai donc chercher une solution afin d'automatiser la synchronisation des endpoints et j'ai opté pour OpenAPI et Orval.

## L'ajout de scripts

Pour que cela fonctionne, j'ai dû ajouter des scripts à mon fichier `packages.json` :

```
"generate:api": "orval --config ./orval.config.ts",
"api:export": "cd ../backend/src/betterself && python scripts/export_openapi.py",
"api:sync": "npm run api:export && npm run generate:api"
```

Ainsi, quand j'exécute le script `npm run api:sync`, _Orval_ récupère le fichier généré par OpenAPI pour créer des fonctions utilisables dans mon frontend. D'ailleurs, il interagit avec mon API Axios pour effectuer les requêtes avec mon `access_token`.
