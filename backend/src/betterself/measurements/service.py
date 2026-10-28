from sqlalchemy.orm import Session

from sqlalchemy import select
from betterself.measurements.models import Measurement
from betterself.measurements.schemas import MeasurementCreate, MeasurementUpdate
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

        # Vérifie que le poids est positif et réaliste
        if measurement.weight_kg <= 30 or measurement.weight_kg > 500:
            raise ValueError("Poids invalide")

        # Ajoute la mesure à la session de la base de données et la commit
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement


    # Récupère les mesures pour un utilisateur donné, avec des filtres optionnels sur les dates
    def get_measurements_for_user(self, user: User, start_date=None, end_date=None):
        # On peut seulement récupérer les mesures appartenant à cet utilisateur
        query =  select(Measurement).where(Measurement.user_id == user.id)

        # Filtre les mesures à partir de la date de début et de fin si elles sont fournies
        if start_date is not None:
            query = query.where(Measurement.date >= start_date)

        if end_date is not None:
            query = query.where(Measurement.date <= end_date)

        # Trie les mesures par date décroissante
        query = query.order_by(Measurement.date.asc())


        return list(self.db.scalars(query))


    # Récupère une mesure spécifique par ID pour un utilisateur donné
    def get_measurement_by_id(self, user: User, measurement_id: int) -> Measurement:
        query = select(Measurement).where(
            Measurement.user_id == user.id,
            Measurement.id == measurement_id
        )
        # Exécute la requête pour récupérer la mesure correspondant à l'ID et à l'utilisateur donné
        measurement = self.db.scalar(query)

        if measurement is None:
            return None

        return measurement


    # Supprime une mesure spécifique par ID pour un utilisateur donné
    def delete_measurement_by_id(self, user: User, measurement_id: int) -> bool:
        query = select(Measurement).where(
            Measurement.user_id == user.id,
            Measurement.id == measurement_id
        )
        measurement = self.db.scalar(query)

        if measurement is None:
            return False

        self.db.delete(measurement)
        self.db.commit()

        # Une réponse 204 ne doit pas renvoyer de contenu, donc on retourne simplement True pour indiquer le succès
        return True

    def update_measurement_by_id(self, user: User, measurement_id: int, data: MeasurementUpdate) -> Measurement | None:
        query = select(Measurement).where(
            Measurement.user_id == user.id,
            Measurement.id == measurement_id
        )
        measurement = self.db.scalar(query)

        if measurement is None:
            return None

        if data.date is not None:
            measurement.date = data.date

        if data.weight_kg is not None:
            measurement.weight_kg = data.weight_kg

        self.db.commit()
        self.db.refresh(measurement)
        return measurement