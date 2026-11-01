from datetime import date

MIN_DATE = date(2020, 1, 1)
MIN_WEIGHT_KG = 30
MAX_WEIGHT_KG = 500


def validate_weight_kg(value: float) -> float:
    if value <= MIN_WEIGHT_KG or value > MAX_WEIGHT_KG:
        raise ValueError(
            "Le poids est invalide."
        )

    return value


def validate_date_not_future(value: date) -> date:
    if value > date.today() or value < MIN_DATE:
        raise ValueError(
            "La date doit être dans le passé ou aujourd'hui."
        )

    return value


def validate_date_within_allowed_range(value: date) -> date:
    if value < MIN_DATE:
        raise ValueError("Date invalide.")

    return value