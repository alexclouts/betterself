from datetime import date

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.schemas.measurement_schemas import MeasurementUpdate, MeasurementCreate, MeasurementCreatedRead, MeasurementRead
from betterself.repos.measurement_repo import MeasurementRepository
from betterself.models.user_models import User
from betterself.core.dependencies import get_current_user
from betterself.core.exceptions import RecordNotFound
from betterself.prefix import MEASUREMENTS_URL
from betterself.services.target_refresh import refresh_active_target

"""
Pour l'instant, nous optons pour une structure try/except pour gérer les erreurs de type MeasurementNotFound étant
donné qu'il y a seulement quelques fonctions
"""

router = APIRouter(prefix=MEASUREMENTS_URL, tags=["Mesures"])

def get_measurement_service(db: Session = Depends(get_db)) -> MeasurementRepository:
    return MeasurementRepository(db)

# Endpoint pour créer une nouvelle mesure
@router.post("", response_model=MeasurementCreatedRead, status_code=status.HTTP_201_CREATED)
def create_measurement(
    data: MeasurementCreate,
    current_user: User = Depends(get_current_user),
    service: MeasurementRepository = Depends(get_measurement_service),
    db: Session = Depends(get_db),
):
    measurement = service.create_measurement(user=current_user, data=data)

    # Un nouveau poids actuel change la cible nutritionnelle. Une mesure
    # rétroactive (antérieure à la plus récente) ne la change pas.
    latest = service.get_latest_measurement(current_user)
    target_update = None
    
    if latest is not None and latest.id == measurement.id:
        target_update = refresh_active_target(db, current_user)

    return MeasurementCreatedRead.model_validate(measurement).model_copy(
        update={"target_update": target_update}
    )


# Endpoint pour récupérer les mesures de l'utilisateur courant
@router.get("", response_model=list[MeasurementRead])
def get_measurements(
    service: MeasurementRepository = Depends(get_measurement_service),
    current_user: User = Depends(get_current_user),
    start_date: date | None = None,
    end_date: date | None = None,
):
    return service.get_measurements_for_user(user=current_user, start_date=start_date, end_date=end_date)



# Endpoint pour récupérer une mesure spécifique par ID pour l'utilisateur courant
@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(
    measurement_id: int,
    service: MeasurementRepository = Depends(get_measurement_service),
    current_user: User = Depends(get_current_user)
):
    try: 
        return service.get_measurement_by_id(user=current_user, measurement_id=measurement_id)
    # On catch l'exception générée par le service lorsqu'un objectif n'est pas trouvé
    except RecordNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")


# Endpoint pour supprimer une mesure spécifique par ID pour l'utilisateur courant
@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(
    measurement_id: int,
    service: MeasurementRepository = Depends(get_measurement_service),
    current_user: User = Depends(get_current_user)
):
    try:
        service.delete_measurement_by_id(user = current_user, measurement_id=measurement_id)
    except RecordNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")


# Endpoint pour mettre à jour une mesure spécifique par ID pour l'utilisateur courant
@router.patch("/{measurement_id}", response_model=MeasurementRead)
def update_measurement(
    measurement_id: int,
    data: MeasurementUpdate,
    service: MeasurementRepository = Depends(get_measurement_service),
    current_user: User = Depends(get_current_user)
):
    try:
        measurement = service.update_measurement_by_id(user=current_user, measurement_id=measurement_id, data=data)
    except RecordNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    return measurement