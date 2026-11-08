from datetime import date
from decimal import Decimal

from betterself.core.exceptions import RecordNotFound
from betterself.models.goal_models import NutritionGoal
from betterself.models.target_models import GoalTarget
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.target_repo import TargetRepository
from betterself.schemas.goal_schemas import NutritionGoalCreate
from betterself.schemas.target_schemas import GoalTargetRecalculate
from betterself.models.user_models import User


class NutritionGoalAlreadyExistsError(Exception):
    """L'utilisateur possède déjà un objectif nutritionnel."""


class GoalTargetCalculationError(Exception):
    """La cible nutritionnelle ne peut pas être calculée."""

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

        return self.goal_repository.save(goal)


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


    # Calcule la cible nutritionnelle pour un objectif donné en fonction du poids de référence et des paramètres personnels.
    def calculate_goal_target(
        self,
        goal: NutritionGoal,
        reference_weight_kg: Decimal,
        *,
        sex: str,
        birth_year: int,
        height_cm: Decimal,
        activity_level: str,
    ) -> dict:
        weight = float(reference_weight_kg)
        height = float(height_cm)
        age = date.today().year - birth_year

        # Calcul du métabolisme de base (BMR) en utilisant la formule de Mifflin-St Jeor.
        if sex == "M":
            bmr = (10 * weight + 6.25 * height - 5 * age + 5)
        elif sex == "F":
            bmr = (10 * weight + 6.25 * height - 5 * age - 161)
        else:
            bmr = (10 * weight + 6.25 * height - 5 * age)

        activity_multipliers = {
            "low": 1.2,
            "moderate": 1.55,
            "high": 1.725,
        }
        # Vérifie que le niveau d'activité physique est valide.
        if activity_level not in activity_multipliers:
            raise GoalTargetCalculationError(
                "Le niveau d'activité physique est invalide."
            )
        # Calcul des calories de maintien en fonction du BMR et du niveau d'activité.
        maintenance_calories = round(bmr * activity_multipliers[activity_level])

        calorie_adjustments = {
            "lose_weight": -500,
            "maintain_weight": 0,
            "gain_muscle": 300,
            "body_recomposition": 0,
        }
        # Ajuste les calories en fonction de l'objectif nutritionnel.
        calorie_adjustment = calorie_adjustments[goal.goal_type.value]
        calories_target = (maintenance_calories + calorie_adjustment)

        if calories_target <= 0:
            raise GoalTargetCalculationError(
                "La cible calorique calculée est invalide."
            )

        # Calcul des macronutriments cibles en fonction des calories cibles.
        protein_target = round(weight * 1.8)
        fat_target = round((calories_target * 0.25) / 9)
        carbs_target = max(round((calories_target - protein_target * 4 - fat_target * 9) / 4), 0,)

        return {
            "maintenance_calories_kcal": maintenance_calories,
            "calories_target_kcal": calories_target,
            "calories_adjustment_kcal": calorie_adjustment,
            "protein_target_g": protein_target,
            "carbs_target_g": carbs_target,
            "fat_target_g": fat_target,
            "calculation_method": "mifflin_st_jeor_v1",
        }


    # Recalcule la cible nutritionnelle pour un objectif donné en fonction des nouvelles données de l'utilisateur.
    def recalculate_goal_target(
        self,
        user: User,
        data: GoalTargetRecalculate,
    ) -> GoalTarget:
        goal = self.get_goal_or_404(user)
        today = date.today()
        # Récupère la cible active actuelle de l'utilisateur, le cas échéant.
        active_target = self.target_repository.get_active_for_user(user)

        if active_target is not None:
            # Ferme la cible active actuelle avant de créer une nouvelle cible.
            self.target_repository.close(
                target=active_target,
                closed_at=today,
            )
        # Calcule les nouvelles valeurs cibles en fonction des données fournies.
        calculated_values = self.calculate_goal_target(
            goal=goal,
            reference_weight_kg=data.reference_weight_kg,
            sex=data.sex,
            birth_year=data.birth_year,
            height_cm=data.height_cm,
            activity_level=data.activity_level,
        )

        new_target = GoalTarget(
            user_id=user.id,
            valid_from=today,
            valid_until=None,
            reference_weight_kg=data.reference_weight_kg,
            **calculated_values,
        )
        return self.target_repository.add(new_target)