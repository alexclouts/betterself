from datetime import date

"""
Fichier utilitaire pour la validation des entrées de poids et de dates.
Vérifie que les poids sont dans la plage autorisée et que les dates sont valides.
"""

# Date la plus ancienne autorisée pour les entrées
MIN_DATE = date(2020, 1, 1)
# Poids minimal et maximal autorisés pour les entrées
MIN_WEIGHT_KG = 30
MAX_WEIGHT_KG = 500

class RangeValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


# Validation du poids en kilogrammes
def validate_weight_kg(value: float) -> float:
    if value <= MIN_WEIGHT_KG or value > MAX_WEIGHT_KG:
        raise RangeValidationError(
            "Le poids est invalide."
        )
    return value


# Validation d'une date pour s'assurer qu'elle est dans les limites autorisées
def validate_date_not_future(value: date) -> date:
    if value > date.today() or value < MIN_DATE:
        raise RangeValidationError("La date doit être dans le passé ou au aujourd'hui.")

    return value


# Validation d'une date pour s'assurer qu'elle est dans le futur
def validate_date_in_future(value: date) -> date:
    if value < date.today():
        raise RangeValidationError("La date doit être future à aujourd'hui")

    return value