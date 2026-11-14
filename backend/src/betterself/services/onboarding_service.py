from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from betterself.schemas.onboarding_schemas import GoalPreviewRead, GoalTimeline
from betterself.schemas.onboarding_schemas import OnboardingCreate
from betterself.schemas.profile_schemas import UserProfileUpdate
from betterself.schemas.target_schemas import GoalTargetCalculationInput
from betterself.services.goal_service import WEEKLY_WEIGHT_CHANGE_KG, GoalService
from opentelemetry.trace import Status
from sqlalchemy import select
from sqlalchemy.orm import Session
from betterself.repos.profile_repo import UserProfileRepository
from betterself.repos.measurement_repo import MeasurementRepository
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.target_repo import TargetRepository

from betterself.models.measurement_models import Measurement
from betterself.models.goal_models import GoalPace, GoalType, NutritionGoal
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
    def save_onboarding(self, user: User, data: OnboardingCreate) -> None:
        self._save_profile(user, data)
        self._save_measurement(user, data)
        goal = self._save_nutrition_goal(user, data)
        self._save_goal_target(user, data)

    
    # Sauvegarde les informations du profil utilisateur.
    def _save_profile(
        self,
        user: User,
        data: OnboardingCreate,
    ) -> UserProfile:
        return self.profile_repository.create_or_update_profile(
            user=user,
            data=UserProfileUpdate(
                first_name=data.first_name,
                year_of_birth=data.birth_year,
                sex=data.sex,
                height_cm=data.height_cm,
                activity_level=data.activity_level,
            ),
        )


    # Sauvegarde les mesures corporelles de l'utilisateur.
    def _save_measurement(
        self,
        user: User,
        data: OnboardingCreate,
    ) -> Measurement:
        measurement = Measurement(
            user_id=user.id,
            date=date.today(),
            weight_kg=data.current_weight_kg,
        )
        return self.measurement_repository.add(measurement)


    # Sauvegarde l'objectif nutritionnel de l'utilisateur.
    def _save_nutrition_goal(
        self,
        user: User,
        data: OnboardingCreate,
    ) -> NutritionGoal:
        nutrition_goal = self.goal_repository.get_for_user(user)

        timeline = self.calculate_goal_timeline(
            onboarding=data,
        )

        if nutrition_goal is None:
            nutrition_goal = NutritionGoal(
                user_id=user.id,
                goal_type=data.goal_type,
                goal_pace=data.pace,
                start_weight_kg=data.current_weight_kg,
                target_weight_kg=data.target_weight_kg,
                start_date=date.today(),
                target_date=timeline.target_date,
                status="active",
            )
            return self.goal_repository.add(nutrition_goal)

        nutrition_goal.goal_type = data.goal_type
        nutrition_goal.goal_pace = data.pace
        nutrition_goal.start_weight_kg = data.current_weight_kg
        nutrition_goal.target_weight_kg = data.target_weight_kg
        nutrition_goal.start_date = date.today()
        nutrition_goal.target_date = timeline.target_date
        nutrition_goal.status = "active"

        return nutrition_goal


    # Sauvegarde la cible d'objectif de l'utilisateur.
    def _save_goal_target(
        self,
        user: User,
        data: OnboardingCreate,
    ) -> GoalTarget:
        self.target_repository.close(user, date.today())

        calculation = self.goal_service.calculate_goal_target(
            GoalTargetCalculationInput(
                goal_type=data.goal_type,
                pace=data.pace,
                reference_weight_kg=data.current_weight_kg,
                target_weight_kg=data.target_weight_kg,
                sex=data.sex,
                birth_year=data.birth_year,
                height_cm=data.height_cm,
                activity_level=data.activity_level,
            )
        )
        goal_target = GoalTarget(
            user_id=user.id,
            valid_from=date.today(),
            valid_until=None,
            reference_weight_kg=data.current_weight_kg,
            maintenance_calories_kcal=calculation["maintenance_calories_kcal"],
            calories_target_kcal=calculation["calories_target_kcal"],
            calories_adjustment_kcal=calculation["calories_adjustment_kcal"],
            protein_target_g=calculation["protein_target_g"],
            carbs_target_g=calculation["carbs_target_g"],
            fat_target_g=calculation["fat_target_g"],
            calculation_method=calculation["calculation_method"],
        )
        return self.target_repository.add(goal_target)
        

    """
    Prévisualise l'objectif nutritionnel de l'utilisateur en fonction des données fournies.
    """
    def preview_goal(
        self,
        *,
        goal_data: OnboardingCreate,
    ) -> GoalPreviewRead:
        # Calcule la timeline estimée pour l'objectif en fonction des données d'onboarding.
        timeline = self.calculate_goal_timeline(onboarding=goal_data)

        # Calcule la cible d'objectif nutritionnel
        goal_target = self.goal_service.calculate_goal_target(
            GoalTargetCalculationInput(
                goal_type=goal_data.goal_type,
                pace=goal_data.pace,
                reference_weight_kg=goal_data.current_weight_kg,
                target_weight_kg=goal_data.target_weight_kg,
                sex=goal_data.sex,
                birth_year=goal_data.birth_year,
                height_cm=goal_data.height_cm,
                activity_level=goal_data.activity_level
            )
        )
        return GoalPreviewRead(
            goal_type=goal_data.goal_type,
            current_weight_kg=goal_data.current_weight_kg,
            target_weight_kg=goal_data.target_weight_kg,
            pace=goal_data.pace,
            estimated_weeks=timeline.estimated_weeks,
            estimated_completion_date=timeline.target_date,
            first_target_calories_kcal=goal_target["calories_target_kcal"],
        )


    """
    Calcule la chronologie de l'objectif nutritionnel de l'utilisateur en fonction des données fournies.
    """
    def calculate_goal_timeline(
        self,
        onboarding: OnboardingCreate,
        start_date: date | None = None,
    ) -> GoalTimeline:
        # Si l'objectif est de maintenir le poids, il n'y a pas de chronologie à calculer.
        if onboarding.goal_type == GoalType.MAINTAIN_WEIGHT:
            return GoalTimeline(
                estimated_weeks=None,
                target_date=None,
            )

        # Normalement vérifié par le validateur du schéma OnboardingCreate, mais on le re-vérifie ici pour la sécurité.
        if onboarding.pace is None:
            raise ValueError(
                "Un rythme est requis pour les objectifs de perte de poids ou de gain musculaire."
            )

        start = start_date or date.today()

        # Convertir les poids en Decimal pour des calculs précis.
        starting_weight = Decimal(str(onboarding.current_weight_kg))
        target_weight = Decimal(str(onboarding.target_weight_kg))

        weight_difference = abs(target_weight - starting_weight)
        weekly_change = WEEKLY_WEIGHT_CHANGE_KG[onboarding.pace]

        # Calculer le nombre de semaines estimé pour atteindre l'objectif.
        estimated_weeks = (weight_difference / weekly_change).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP,
        )
        days = int((estimated_weeks * Decimal("7")).to_integral_value(rounding=ROUND_HALF_UP))
        target_date = start + timedelta(days=days)

        return GoalTimeline(
            estimated_weeks=estimated_weeks,
            target_date=target_date,
        )
