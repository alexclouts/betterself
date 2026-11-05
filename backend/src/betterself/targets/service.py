from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.goal.models import NutritionGoal
from betterself.goal.service import GoalService
from betterself.targets.models import GoalTarget
from betterself.targets.schemas import GoalTargetRecalculate
from betterself.users.models import User


"""
Levée lorsque la cible nutritionnelle ne peut pas être calculée à partir
des paramètres biométriques disponibles.
"""
class GoalTargetCalculationError(Exception):
    pass


class TargetService:
    def __init__(self, db: Session):
        self.db = db
        self.goal_service = GoalService(db)

    """
    Retourne la cible nutritionnelle active de l'utilisateur.
    La cible active est la seule ligne dont `valid_until` est `None`.
    Elle contient les calories et macronutriments que l'utilisateur doit suivre actuellement.
    """    
    def get_active_goal_target(self, user: User) -> GoalTarget:
        query = (
            select(GoalTarget)
            .where(
                GoalTarget.user_id == user.id,
                GoalTarget.valid_until.is_(None),
            )
            .order_by(GoalTarget.valid_from.desc())
            .limit(1)
        )

        target = self.db.scalar(query)

        if target is None:
            raise RecordNotFound(
                "Aucune cible nutritionnelle active n'a été trouvée."
            )

        return target


    """
    Calcule les calories et macronutriments cibles à partir du poids de référence et des paramètres biométriques de l'utilisateur.
    Cette version utilise Mifflin-St Jeor. Les règles nutritionnelles pourront être isolées dans un module de calcul plus tard.
    """
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

        if sex == "M":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif sex == "F":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age

        activity_multipliers = {
            "low": 1.2,
            "moderate": 1.55,
            "high": 1.725,
        }

        if activity_level not in activity_multipliers:
            raise GoalTargetCalculationError(
                "Le niveau d'activité physique est invalide."
            )

        maintenance_calories = round(
            bmr * activity_multipliers[activity_level]
        )

        # Ajustements initiaux selon l'objectif nutritionnel de l'utilisateur.
        calorie_adjustments = {
            "lose_weight": -500,
            "maintain_weight": 0,
            "gain_muscle": 300,
            "body_recomposition": 0,
        }

        calorie_adjustment = calorie_adjustments[goal.goal_type.value]
        calories_target = maintenance_calories + calorie_adjustment

        if calories_target <= 0:
            raise GoalTargetCalculationError(
                "La cible calorique calculée est invalide."
            )

        protein_target = round(weight * 1.8)
        fat_target = round((calories_target * 0.25) / 9)
        carbs_target = max(
            round(
                (calories_target - protein_target * 4 - fat_target * 9) / 4
            ),
            0,
        )

        return {
            "maintenance_calories_kcal": maintenance_calories,
            "calories_target_kcal": calories_target,
            "calories_adjustment_kcal": calorie_adjustment,
            "protein_target_g": protein_target,
            "carbs_target_g": carbs_target,
            "fat_target_g": fat_target,
            "calculation_method": "mifflin_st_jeor_v1",
        }

    """
    Crée une nouvelle cible nutritionnelle à partir d'un nouveau poids.
    La cible active précédente est fermée en renseignant `valid_until`.
    La nouvelle cible devient la seule cible active, tandis que l'ancienne reste disponible dans l'historique.
    """
    def recalculate_goal_target(
        self,
        user: User,
        data: GoalTargetRecalculate,
    ) -> GoalTarget:
        # L'utilisateur doit posséder un objectif nutritionnel.
        goal = self.goal_service.get_goal_or_404(user)

        today = date.today()

        # Ferme la cible active, s'il y en a une.
        active_target = self.db.scalar(
            select(GoalTarget).where(
                GoalTarget.user_id == user.id,
                GoalTarget.valid_until.is_(None),
            )
        )

        # Si une cible active existe, on la ferme en renseignant `valid_until`.
        if active_target is not None:
            active_target.valid_until = today

        calculated_values = self.calculate_goal_target(
            goal=goal,
            reference_weight_kg=data.reference_weight_kg,
            sex=data.sex,
            birth_year=data.birth_year,
            height_cm=data.height_cm,
            activity_level=data.activity_level,
        )

        # Crée la nouvelle cible nutritionnelle avec les valeurs calculées.
        new_target = GoalTarget(
            user_id=user.id,
            valid_from=today,
            valid_until=None,
            reference_weight_kg=data.reference_weight_kg,
            **calculated_values,
        )

        self.db.add(new_target)
        self.db.commit()
        self.db.refresh(new_target)

        return new_target