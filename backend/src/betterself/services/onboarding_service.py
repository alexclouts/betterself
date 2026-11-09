from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.models.measurement_models import Measurement
from betterself.models.goal_models import NutritionGoal
from betterself.models.target_models import GoalTarget
from betterself.models.user_models import User, UserProfile


"""
Ce service gère le suivi de l'état d'intégration d'un utilisateur, en vérifiant s'il a complété les étapes nécessaires telles que 
la création de son profil, l'ajout de mesures corporelles, la définition d'objectifs nutritionnels et la création de cibles d'objectifs.
"""

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db

    # Récupère le statut d'intégration de l'utilisateur, indiquant quelles étapes ont été complétées et lesquelles manquent.
    def get_status(self, user: User) -> dict:
        has_profile = self._has_profile(user)
        has_measurement = self._has_body_measurement(user)
        has_goal = self._has_active_nutrition_goal(user)
        has_target = self._has_active_goal_target(user)

        steps = {
            "profile": has_profile,
            "body_measurement": has_measurement,
            "nutrition_goal": has_goal,
            "goal_target": has_target,
        }
        missing_steps = [
            step
            for step, completed in steps.items()
            if not completed
        ]
        return {
            "is_complete": not missing_steps,
            "missing_steps": missing_steps,
            "steps": steps,
        }

    # Vérifie si l'utilisateur a un profil.
    def _has_profile(self, user: User) -> bool:
        profile = self.db.scalar(
            select(UserProfile).where(
                UserProfile.user_id == user.id,
            )
        )
        return profile is not None


    # Vérifie si l'utilisateur a au moins une mesure corporelle.
    def _has_body_measurement(self, user: User) -> bool:
        measurement = self.db.scalar(
            select(Measurement)
            .where(
                Measurement.user_id == user.id
            )
            .order_by(Measurement.date.desc())
            .limit(1)
        )
        return measurement is not None


    # Vérifie si l'utilisateur a un objectif nutritionnel actif.
    def _has_active_nutrition_goal(self, user: User) -> bool:
        goal = self.db.scalar(
            select(NutritionGoal).where(
                NutritionGoal.user_id == user.id,
                NutritionGoal.status == "active",
            )
        )
        return goal is not None


    # Vérifie si l'utilisateur a une cible d'objectif active.
    def _has_active_goal_target(self, user: User) -> bool:
        target = self.db.scalar(
            select(GoalTarget).where(
                GoalTarget.user_id == user.id,
                GoalTarget.valid_until.is_(None),
            )
        )
        return target is not None