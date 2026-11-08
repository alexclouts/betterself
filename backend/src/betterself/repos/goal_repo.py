from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.models.goal_models import NutritionGoal
from betterself.models.user_models import User


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db


    # Récupère l'objectif nutritionnel pour un utilisateur donné.
    def get_for_user(
        self,
        user: User,
    ) -> NutritionGoal | None:
        query = select(NutritionGoal).where(
            NutritionGoal.user_id == user.id,
        )
        return self.db.scalar(query)


    # Ajoute un nouvel objectif nutritionnel pour un utilisateur donné.
    def add(
        self,
        goal: NutritionGoal,
    ) -> NutritionGoal:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal


    # Sauvegarde les modifications apportées à un objectif nutritionnel existant.
    def save(
        self,
        goal: NutritionGoal,
    ) -> NutritionGoal:
        self.db.commit()
        self.db.refresh(goal)
        return goal