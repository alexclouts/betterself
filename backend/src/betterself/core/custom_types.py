from typing import Annotated

from pydantic import BeforeValidator, StringConstraints


"""
Convertit une chaîne vide ou composée d'espaces en `None`.
"""
def empty_string_to_none(value: object) -> object:
    if isinstance(value, str) and not value.strip():
        return None

    return value


NonEmptyText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]


OptionalText = Annotated[
    str | None,
    BeforeValidator(empty_string_to_none),
    StringConstraints(
        strip_whitespace=True,
        max_length=255,
    ),
]


OptionalLongText = Annotated[
    str | None,
    BeforeValidator(empty_string_to_none),
    StringConstraints(
        strip_whitespace=True,
        max_length=2000,
    ),
]