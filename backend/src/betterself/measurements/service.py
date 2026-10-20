from sqlalchemy.orm import Session

from sqlalchemy import select
from betterself.measurements.models import Measurement
from betterself.measurements.schemas import MeasurementCreate
from betterself.users.models import User

class MeasurementService:
    def __init__(self, db: Session):
        self.db = db

    def create_measurement(self, user: User, data: MeasurementCreate) -> Measurement:
        measurement = Measurement(
            user_id = user.id,
            date = data.date,
            weight_kg = data.weight_kg,
        )

        # Ajoute la mesure à la session de la base de données et la commit
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement


    # Récupère les mesures pour un utilisateur donné, avec des filtres optionnels sur les dates
    def get_measurements_for_user(self, user: User, start_date=None, end_date=None):
        query =  select(Measurement).where(Measurement.user_id == user.id)

        if start_date is not None:
            query = query.where(Measurement.date >= start_date)

        if end_date is not None:
            query = query.where(Measurement.date <= end_date)

        # Trie les mesures par date décroissante
        query = query.order_by(Measurement.date.desc())


        return list(self.db.scalars(query))
    
