# Validation qui échappe à Pydantic

Je m'attendais à ce que la vérification retourne une erreur 422, mais ça ne semble pas être le cas. Comment valider tout de même le test unitaire?

L’erreur montre que la valeur invalide (`invalid_goal_type`) a réussi à traverser Pydantic et est arrivée jusqu’à SQLAlchemy. Donc, dans ton `NutritionGoalCreate`, le champ est probablement encore déclaré comme `str` plutôt que comme ton enum `GoalType`.[^33_1]

## 1. Valide dans le schéma

Dans `src/betterself/nutrition/schemas.py`, assure-toi d’avoir :

```python
from betterself.nutrition.models import GoalType


class NutritionGoalCreate(BaseModel):
    goal_type: GoalType
    ...
```

et non :

```python
class NutritionGoalCreate(BaseModel):
    goal_type: str
    ...
```

Avec `goal_type: GoalType`, Pydantic doit rejeter `"invalid_goal_type"` et FastAPI retournera automatiquement :

```text
422 Unprocessable Entity
```
