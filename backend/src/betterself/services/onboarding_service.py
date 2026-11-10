from datetime import date, timedelta

from betterself.services.goal_service import GoalService
from sqlalchemy import select
from sqlalchemy.orm import Session
from betterself.repos.profile_repo import UserProfileRepository
from betterself.repos.measurement_repo import MeasurementRepository
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.target_repo import TargetRepository

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
        self.profile_repository = UserProfileRepository(db)
        self.measurement_repository = MeasurementRepository(db)
        self.goal_repository = GoalRepository(db)
        self.target_repository = TargetRepository(db)
        self.goal_service = GoalService(self.goal_repository, self.target_repository)

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

    # Enregistre les informations d'onboarding pour l'utilisateur.
    def save_onboarding(self, user, onboarding_data: dict) -> None:
        self._save_profile(user, onboarding_data)
        self._save_measurement(user, onboarding_data)
        self._save_nutrition_goal(user, onboarding_data)
        self._save_goal_target(user, onboarding_data)

    
    # Sauvegarde les informations du profil utilisateur.
    def _save_profile(self, user, data: dict) -> None:
        profile = self.profile_repository.get_profile_or_404(user.id)

        if profile is None:
            profile = UserProfile(user_id=user.id)
            self.profile_repository.add(profile)

        profile.first_name = data["name"]
        profile.year_of_birth = date(int(data["birthYear"]), 1, 1)
        profile.sex = data["sex"]


    # Sauvegarde les mesures corporelles de l'utilisateur.
    def _save_measurement(self, user, data: dict) -> None:
        measurement = self.measurement_repository.get_measurements_for_user(user)
        
        if measurement is None:
            measurement = Measurement(
                user_id=user.id,
                date=date.today(),
            )
            self.measurement_repository.add(measurement)

        measurement.weight_kg = data["weightKg"]


    # Sauvegarde l'objectif nutritionnel de l'utilisateur.
    def _save_nutrition_goal(self, user, data: dict) -> None:
        goal = self.goal_repository.get_for_user(user.id)

        if goal is None:
            goal = NutritionGoal(
                user_id=user.id,
                status="active",
            )
            self.goal_repository.add(goal)

        goal.goal_type = data["goal"]


    # Sauvegarde la cible d'objectif de l'utilisateur.
    def _save_goal_target(
        self,
        user,
        onboarding_data: dict,
    ) -> None:
        nutrition_goal = self.goal_repository.get_for_user(user.id)

        if nutrition_goal is None:
            raise ValueError(
                "Un objectif nutritionnel actif doit exister avant la création d’une cible."
            )

        # Vérifie si une cible active existe pour l'utilisateur. Pas supposée exister au moment de l'onboarding.
        goal_target = self.target_repository.get_active_for_user(user.id)

        if goal_target is None:
            # Crée une nouvelle cible si aucune n'existe.
            goal_target = GoalTarget(
                user_id=user.id,
                goal_id=nutrition_goal.id,
                valid_from=date.today(),
                valid_until=None,
            )
            self.target_repository.add(goal_target)

        # Récupère les calculs de la cible d'objectif en fonction des données d'onboarding.
        calculation = self.goal_service.calculate_goal_target(
            goal=nutrition_goal,
            reference_weight_kg=onboarding_data["weightKg"],
            sex=onboarding_data["sex"],
            birth_year=onboarding_data["birthYear"],
            height_cm=onboarding_data["heightCm"],
            activity_level=onboarding_data["activityLevel"],
        )

        # Met à jour les attributs de la cible d'objectif avec les calculs obtenus.
        goal_target.reference_weight_kg = onboarding_data["weightKg"]
        goal_target.maintenance_calories_kcal = calculation["maintenance_calories_kcal"]
        goal_target.calories_target_kcal = calculation["calories_target_kcal"]
        goal_target.calories_adjustment_kcal = calculation["calories_adjustment_kcal"]
        goal_target.protein_target_g = calculation["protein_target_g"]
        goal_target.carbs_target_g = calculation["carbs_target_g"]
        goal_target.fat_target_g = calculation["fat_target_g"]
        goal_target.calculation_method = calculation["calculation_method"]