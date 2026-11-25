from typing import Annotated, Optional

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
    Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                max_length=255,
            ),
        ]
    ],
    BeforeValidator(empty_string_to_none),
]


# Les contraintes s'appliquent à la chaîne seulement : appliquées à `str | None`,
# elles échoueraient sur None (TypeError, donc une erreur 500).
OptionalLongText = Annotated[
    Optional[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                max_length=2000,
            ),
        ]
    ],
    BeforeValidator(empty_string_to_none),
]