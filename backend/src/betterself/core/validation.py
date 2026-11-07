from datetime import date

MIN_DATE = date(2020, 1, 1)

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