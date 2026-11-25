import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from betterself.models.user_models import User
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.measurement_repo import MeasurementRepository
from betterself.repos.profile_repo import UserProfileRepository
from betterself.repos.target_repo import TargetRepository
from betterself.schemas.target_schemas import GoalTargetRecalculate
from betterself.schemas.target_update_schemas import TargetUpdateRead, TargetUpdateStatus
from betterself.services.goal_service import GoalService, GoalTargetCalculationError

logger = logging.getLogger(__name__)


class TargetService:
    def __init__(self, db: Session):
        self.db = db
        self.goal_repository = GoalRepository(db)
        self.target_repository = TargetRepository(db)
        self.user_profile_repository = UserProfileRepository(db)
        self.measurement_repository = MeasurementRepository(db)


    """
    Recalcule automatiquement la cible nutritionnelle active après un changement
    qui influence le calcul : un nouveau poids ou une modification du profil
    (sexe, année de naissance, taille, niveau d'activité).

    Le poids de référence est la mesure la plus récente ; à défaut, le poids de la
    cible active, puis le poids de départ de l'objectif.

    Ne fait rien si l'utilisateur n'a pas encore de profil ou d'objectif (onboarding
    incomplet). Si le calcul échoue (ex. moins de 1200 kcal), la cible actuelle est
    conservée : la mesure ou le profil restent enregistrés.

    Retourne le résultat (updated ou failed) à transmettre au client,
    ou None si aucun recalcul n'a été tenté.
    """
    def refresh_active_target(self, user: User) -> TargetUpdateRead | None:
        profile = self.user_profile_repository.get_by_user(user)
        goal = self.goal_repository.get_for_user(user)

        if profile is None or goal is None:
            return None

        latest = self.measurement_repository.get_latest_measurement(user)
        active_target = self.target_repository.get_active_for_user(user)

        if latest is not None:
            reference_weight_kg = Decimal(str(latest.weight_kg))
        elif active_target is not None:
            reference_weight_kg = active_target.reference_weight_kg
        else:
            reference_weight_kg = goal.start_weight_kg

        previous_calories = active_target.calories_target_kcal if active_target is not None else None
        service = GoalService(goal_repository=self.goal_repository, target_repository=self.target_repository)

        try:
            new_target = service.recalculate_goal_target(
                user=user,
                data=GoalTargetRecalculate(
                    reference_weight_kg=reference_weight_kg,
                    sex=profile.sex,
                    birth_year=profile.year_of_birth,
                    height_cm=profile.height_cm,
                    activity_level=profile.activity_level,
                ),
            )
        except GoalTargetCalculationError as error:
            logger.warning("Recalcul automatique de la cible impossible ; cible actuelle conservée.", exc_info=True)
            return TargetUpdateRead(
                status=TargetUpdateStatus.FAILED,
                previous_calories_target_kcal=previous_calories,
                calories_target_kcal=previous_calories,
                message=str(error),
            )

        return TargetUpdateRead(
            status=TargetUpdateStatus.UPDATED,
            previous_calories_target_kcal=previous_calories,
            calories_target_kcal=new_target.calories_target_kcal,
        )
