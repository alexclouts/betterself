from sqlalchemy.orm import Session

from betterself.models.measurement_models import Measurement
from betterself.schemas.measurement_schemas import MeasurementCreate, MeasurementUpdate
from betterself.models.user_models import User
from betterself.core.exceptions import RecordNotFound

class MeasurementRepository:
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
        # On peut seulement récupérer les mesures appartenant à cet utilisateur
        query =  Measurement.for_user(user.id)

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
        return self._get_measurement_or_404(user, measurement_id)


    # Supprime une mesure spécifique par ID pour un utilisateur donné
    def delete_measurement_by_id(self, user: User, measurement_id: int) -> bool:
        measurement = self._get_measurement_or_404(user, measurement_id)

        self.db.delete(measurement)
        self.db.commit()

        # Une réponse 204 ne doit pas renvoyer de contenu, donc on retourne simplement True pour indiquer le succès
        return True

    # Met à jour une mesure spécifique par ID pour un utilisateur donné
    def update_measurement_by_id(self, user: User, measurement_id: int, data: MeasurementUpdate) -> Measurement | None:
        measurement = self._get_measurement_or_404(user, measurement_id)

        if data.date is not None:
            measurement.date = data.date

        if data.weight_kg is not None:
            measurement.weight_kg = data.weight_kg

        self.db.commit()
        self.db.refresh(measurement)
        return measurement


    # Dans tous les cas où une mesure est recherchée, on génère une exception si elle n'existe pas
    def _get_measurement_or_404(self, user: User, measurement_id: int) -> Measurement:
        measurement = self.db.scalar(
            Measurement.for_user(user.id).where(Measurement.id == measurement_id)
        )
        if measurement is None:
            raise RecordNotFound("Mesure introuvable.")
        
        return measurement