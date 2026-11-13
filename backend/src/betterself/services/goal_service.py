from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from betterself.core.exceptions import RecordNotFound
from betterself.models.goal_models import GoalPace, GoalType, NutritionGoal
from betterself.models.profile_models import UserProfile
from betterself.models.target_models import GoalTarget
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.target_repo import TargetRepository
from betterself.schemas.goal_schemas import NutritionGoalCreate
from betterself.schemas.onboarding_schemas import OnboardingCreate
from betterself.schemas.profile_schemas import ActivityLevel, Sex
from betterself.schemas.target_schemas import GoalTargetCalculationInput
from betterself.models.user_models import User


class NutritionGoalAlreadyExistsError(Exception):
    """L'utilisateur possède déjà un objectif nutritionnel."""


class GoalTargetCalculationError(Exception):
    """La cible nutritionnelle ne peut pas être calculée."""

CALORIES_PER_KG = Decimal("7700")

WEEKLY_WEIGHT_CHANGE_KG = {
    GoalPace.SLOW: Decimal("0.226796"),       # 0.5 lb / semaine
    GoalPace.MODERATE: Decimal("0.453592"),   # 1 lb / semaine
    GoalPace.AGGRESSIVE: Decimal("0.680389"), # 1.5 lb / semaine
}


"""
Service pour la gestion des objectifs nutritionnels et des cibles associées.
Fournit des méthodes pour récupérer, créer, mettre à jour et recalculer les objectifs et cibles nutritionnels.
"""
class GoalService:
    def __init__(
        self,
        goal_repository: GoalRepository,
        target_repository: TargetRepository,
    ):
        self.goal_repository = goal_repository
        self.target_repository = target_repository

    # Récupère l'objectif nutritionnel pour un utilisateur donné.
    # Si aucun objectif n'existe, renvoie None.
    def get_goal(
        self,
        user: User,
    ) -> NutritionGoal | None:
        return self.goal_repository.get_for_user(user)


    # Récupère l'objectif nutritionnel pour un utilisateur donné ou lève une erreur si inexistant.
    def get_goal_or_404(
        self,
        user: User,
    ) -> NutritionGoal:
        goal = self.get_goal(user)

        if goal is None:
            raise RecordNotFound(
                "Aucun objectif nutritionnel n'a été trouvé."
            )
        return goal


    # Crée un nouvel objectif nutritionnel pour un utilisateur donné.
    def create_goal(
        self,
        user: User,
        data: NutritionGoalCreate,
    ) -> NutritionGoal:
        existing_goal = self.get_goal(user)

        if existing_goal is not None:
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
        return self.goal_repository.add(goal)


    # Met à jour l'objectif nutritionnel existant pour un utilisateur donné.
    def update_goal(
        self,
        user: User,
        data: NutritionGoalCreate,
    ) -> NutritionGoal:
        goal = self.get_goal_or_404(user)

        goal.goal_type = data.goal_type
        goal.start_weight_kg = data.start_weight_kg
        goal.target_weight_kg = data.target_weight_kg
        goal.start_date = data.start_date
        goal.target_date = data.target_date

        return goal


    # Récupère la cible nutritionnelle active pour un utilisateur donné.
    # Si aucune cible active n'existe, lève une erreur.
    def get_active_goal_target(
        self,
        user: User,
    ) -> GoalTarget:
        target = self.target_repository.get_active_for_user(user)

        if target is None:
            raise RecordNotFound(
                "Aucune cible nutritionnelle active n'a été trouvée."
            )
        return target


    # Calcule l'ajustement calorique quotidien en fonction du type d'objectif et du rythme.
    # Lève une erreur si le calcul de l'ajustement calorique échoue.
    def calculate_calorie_adjustment(
        self,
        *,
        goal_type: GoalType,
        pace: Optional[GoalPace],
    ) -> int:
        if goal_type == GoalType.MAINTAIN_WEIGHT:
            # Pour un objectif de maintien du poids, l'ajustement calorique est nul.
            if pace is not None:
                raise GoalTargetCalculationError(
                    "Le rythme ne doit pas être fourni pour un objectif de maintien."
                )

            return 0

        if pace is None:
            raise GoalTargetCalculationError(
                "Le rythme est requis pour une perte de poids ou un gain musculaire."
            )
        # Calcule le changement de poids quotidien en fonction du rythme hebdomadaire.
        weekly_weight_change_kg = WEEKLY_WEIGHT_CHANGE_KG[pace]

        daily_weight_change_kg = (
            weekly_weight_change_kg / Decimal("7")
        )
        # Calcule l'ajustement calorique quotidien en fonction du changement de poids quotidien.
        daily_calorie_adjustment = (
            daily_weight_change_kg * CALORIES_PER_KG
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )

        # Retourne l'ajustement calorique en fonction du type d'objectif.
        if goal_type == GoalType.LOSE_WEIGHT:
            return -int(daily_calorie_adjustment)

        if goal_type == GoalType.GAIN_MUSCLE:
            return int(daily_calorie_adjustment)

        raise GoalTargetCalculationError(
            "Le type d’objectif n’est pas pris en charge pour le calcul "
            "de l’ajustement calorique."
        )


    # Calcule la cible nutritionnelle pour un objectif donné en fonction du poids de référence et des paramètres personnels.
    # Lève une erreur si le calcul de la cible nutritionnelle échoue.
    def calculate_goal_target(
        self,
        data: GoalTargetCalculationInput,
    ) -> dict:
        weight = float(data.reference_weight_kg)
        height = float(data.height_cm)
        age = date.today().year - data.birth_year
        # Calcule l'âge de l'utilisateur à partir de l'année de naissance.
        if data.sex == Sex.male:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif data.sex == Sex.female:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age

        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTREMELY_ACTIVE: 1.9,
        }

        if data.activity_level not in activity_multipliers:
            raise GoalTargetCalculationError(
                "Le niveau d’activité physique est invalide."
            )

        maintenance_calories = round(bmr * activity_multipliers[data.activity_level])
        # Obtient l'ajustement calorique en fonction du type d'objectif et du rythme.
        calories_adjustment_kcal = self.calculate_calorie_adjustment(
            goal_type=data.goal_type,
            pace=data.pace,
        )

        calories_target_kcal = (
            maintenance_calories + calories_adjustment_kcal
        )

        if calories_target_kcal <= 0:
            raise GoalTargetCalculationError(
                "La cible calorique calculée est invalide."
            )
        # Calcule les cibles en macronutriments en fonction des calories cibles et du poids de référence.
        protein_target = round(weight * 1.8)
        fat_target = round((calories_target_kcal * 0.25) / 9)
        carbs_target = max(round((calories_target_kcal - protein_target * 4 - fat_target * 9) / 4), 0)
        return {
            "maintenance_calories_kcal": maintenance_calories,
            "calories_target_kcal": calories_target_kcal,
            "calories_adjustment_kcal": calories_adjustment_kcal,
            "protein_target_g": protein_target,
            "carbs_target_g": carbs_target,
            "fat_target_g": fat_target,
            "calculation_method": "mifflin_st_jeor_v1",
        }


    # Recalcule la cible nutritionnelle pour un objectif donné en fonction des nouvelles données de l'utilisateur.
    def recalculate_goal_target(
        self,
        user: User,
        data: GoalTargetCalculationInput,
    ) -> GoalTarget:
        today = date.today()
        # Récupère la cible active actuelle de l'utilisateur, le cas échéant.
        active_target = self.target_repository.get_active_for_user(user.id)

        if active_target is not None:
            # Ferme la cible active actuelle avant de créer une nouvelle cible.
            self.target_repository.close(
                target=active_target,
                closed_at=today,
            )
        # Calcule les nouvelles valeurs cibles en fonction des données fournies.
        calculated_values = self.calculate_goal_target(
            data
        )

        new_target = GoalTarget(
            user_id=user.id,
            valid_from=today,
            valid_until=None,
            reference_weight_kg=data.reference_weight_kg,
            **calculated_values
        )
        return self.target_repository.add(new_target)


