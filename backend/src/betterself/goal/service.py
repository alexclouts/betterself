import uuid

from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.goal.models import NutritionGoal
from betterself.goal.schemas import NutritionGoalCreate
from betterself.users.models import User


class NutritionGoalAlreadyExistsError(Exception):
    """
    Levée lorsqu'un utilisateur tente de créer un objectif nutritionnel
    alors qu'il en possède déjà un.

    L'objectif est créé durant le onboarding. L'utilisateur peut ensuite le
    modifier, mais il ne peut pas en créer un second.
    """


class GoalService:
    def __init__(self, db: Session):
        self.db = db

    # Fonction pour récupérer l'objectif nutritionnel de l'utilisateur
    def get_goal(self, user: User) -> NutritionGoal | None:
        """
        Retourne l'objectif nutritionnel de l'utilisateur, ou None s'il n'a
        pas encore complété l'étape de onboarding.
        """
        return self.db.get(NutritionGoal, user.id)

    # Fonction pour récupérer l'objectif nutritionnel ou lever une exception
    def get_goal_or_404(self, user: User) -> NutritionGoal:
        """
        Retourne l'objectif nutritionnel de l'utilisateur.

        Cette méthode est utilisée notamment par le service des cibles
        nutritionnelles, qui a besoin de connaître l'objectif afin de
        calculer les calories et macronutriments.
        """
        goal = self.get_goal(user)

        if goal is None:
            raise RecordNotFound(
                "Aucun objectif nutritionnel n'a été trouvé."
            )

        return goal

    # Fonction pour créer l'objectif nutritionnel durant le onboarding
    def create_goal(
        self,
        user: User,
        data: NutritionGoalCreate,
    ) -> NutritionGoal:
        """
        Crée l'objectif nutritionnel initial de l'utilisateur.

        Puisqu'un utilisateur ne peut posséder qu'un seul objectif, la création
        est refusée si un objectif existe déjà. L'utilisateur doit alors
        modifier son objectif existant.
        """
        if self.get_goal(user) is not None:
            raise NutritionGoalAlreadyExistsError(
                "L'utilisateur possède déjà un objectif nutritionnel."
            )

        goal = NutritionGoal(
            user_id=user.id,
            goal_type=data.goal_type,
            start_weight_kg=data.start_weight_kg,
            target_weight_kg=data.target_weight_kg,
            start_date=data.start_date,
            target_date=data.target_date,
            status="active",
        )

        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)

        return goal

    # Fonction pour mettre à jour l'objectif nutritionnel existant
    def update_goal(
        self,
        user: User,
        data: NutritionGoalCreate,
    ) -> NutritionGoal:
        """
        Met à jour l'objectif nutritionnel existant de l'utilisateur.

        L'utilisateur ne crée pas un nouvel objectif : il modifie celui créé
        durant le onboarding. La relation `1 utilisateur = 1 objectif` est
        donc préservée.
        """
        goal = self.get_goal_or_404(user)

        goal.goal_type = data.goal_type
        goal.start_weight_kg = data.start_weight_kg
        goal.target_weight_kg = data.target_weight_kg
        goal.start_date = data.start_date
        goal.target_date = data.target_date

        self.db.commit()
        self.db.refresh(goal)

        return goal