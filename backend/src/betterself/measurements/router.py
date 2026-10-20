from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.measurements.schemas import MeasurementCreate, MeasurementRead
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
