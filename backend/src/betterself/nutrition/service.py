import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from betterself.users.models import User
from betterself.nutrition.schemas import NutritionGoalCreate
from betterself.nutrition.models import NutritionGoal
from betterself.core.exceptions import RecordNotFound

class NutritionService:
    def __init__(self, db: Session):
        self.db = db

    # Fonction pour créer un objectif nutritionnel
    def create_goal(self, user: User, data: NutritionGoalCreate) -> NutritionGoal:
        goal = NutritionGoal(
            user_id=user.id,
            goal_type=data.goal_type,
            start_weight_kg=data.start_weight_kg,
            target_weight_kg=data.target_weight_kg,
            start_date=data.start_date,
            target_date=data.target_date,
            status="active"
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)

        return goal

    # Fonction pour récupérer un objectif nutritionnel par son ID
    def get_goal_(self, user: User, goal_id: int) -> NutritionGoal:
        return self._get_goal_or_404(user, goal_id)


    # Si l'objectif nutritionnel n'existe pas, lever une exception RecordNotFound
    def _get_goal_or_404(self, user: User, goal_id: int) -> NutritionGoal:
        goal= self.db.scalar(NutritionGoal.for_user(user.id).where(NutritionGoal.id == goal_id))
        if goal is None:
            raise RecordNotFound("Objectif introuvable.")
        return goal

