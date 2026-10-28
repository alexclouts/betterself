from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.measurements.schemas import MeasurementUpdate, MeasurementCreate, MeasurementRead
from betterself.measurements.service import MeasurementService
from betterself.users.models import User
from betterself.users.router import read_current_user

router = APIRouter(prefix="/measurements", tags=["Mesures"])

# Endpoint pour créer une nouvelle mesure
@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(
    data: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user)
):
    service = MeasurementService(db)
    return service.create_measurement(user=current_user, data=data)


# Endpoint pour récupérer les mesures de l'utilisateur courant
@router.get("", response_model=list[MeasurementRead])
def get_measurements(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user),
    start_date: str = None,
    end_date: str = None
):
    service = MeasurementService(db)
    return service.get_measurements_for_user(user=current_user, start_date=start_date, end_date=end_date)



# Endpoint pour récupérer une mesure spécifique par ID pour l'utilisateur courant
@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user)
):
    service = MeasurementService(db)
    measurement = service.get_measurement_by_id(user=current_user, measurement_id=measurement_id)

    if measurement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    return measurement


# Endpoint pour supprimer une mesure spécifique par ID pour l'utilisateur courant
@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user)
):
    service = MeasurementService(db)
    success = service.delete_measurement_by_id(user=current_user, measurement_id=measurement_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    return None

# Endpoint pour mettre à jour une mesure spécifique par ID pour l'utilisateur courant
@router.patch("/{measurement_id}", response_model=MeasurementRead)
def update_measurement(
    measurement_id: int,
    data: MeasurementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_current_user)
):
    service = MeasurementService(db)
    measurement = service.update_measurement_by_id(user=current_user, measurement_id=measurement_id, data=data)

    if measurement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    return measurement