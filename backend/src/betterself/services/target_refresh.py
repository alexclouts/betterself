import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from betterself.models.target_models import GoalTarget
from betterself.models.user_models import User
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.measurement_repo import MeasurementRepository
from betterself.repos.profile_repo import UserProfileRepository
from betterself.repos.target_repo import TargetRepository
from betterself.schemas.target_schemas import GoalTargetRecalculate
from betterself.services.goal_service import GoalService, GoalTargetCalculationError

logger = logging.getLogger(__name__)


"""
Recalcule automatiquement la cible nutritionnelle active après un changement
qui influence le calcul : un nouveau poids ou une modification du profil
(sexe, année de naissance, taille, niveau d'activité).

Le poids de référence est la mesure la plus récente ; à défaut, le poids de la
cible active, puis le poids de départ de l'objectif.

Ne fait rien si l'utilisateur n'a pas encore de profil ou d'objectif (onboarding
incomplet). Si le calcul échoue (ex. moins de 1200 kcal), la cible actuelle est
conservée : la mesure ou le profil restent enregistrés.

Retourne la nouvelle cible, ou None si aucun recalcul n'a eu lieu.
"""
def refresh_active_target(db: Session, user: User) -> GoalTarget | None:
    profile = UserProfileRepository(db).get_by_user(user)
    goal_repository = GoalRepository(db)
    target_repository = TargetRepository(db)
    goal = goal_repository.get_for_user(user)
    
    if profile is None or goal is None:
        return None

    latest = MeasurementRepository(db).get_latest_measurement(user)
    active_target = target_repository.get_active_for_user(user)

    if latest is not None:
        reference_weight_kg = Decimal(str(latest.weight_kg))
    elif active_target is not None:
        reference_weight_kg = active_target.reference_weight_kg
    else:
        reference_weight_kg = goal.start_weight_kg

    service = GoalService(goal_repository=goal_repository, target_repository=target_repository)
    try:
        return service.recalculate_goal_target(
            user=user,
            data=GoalTargetRecalculate(
                reference_weight_kg=reference_weight_kg,
                sex=profile.sex,
                birth_year=profile.year_of_birth,
                height_cm=profile.height_cm,
                activity_level=profile.activity_level,
            ),
        )
    except GoalTargetCalculationError:
        logger.warning("Recalcul automatique de la cible impossible ; cible actuelle conservée.", exc_info=True)
        return None
