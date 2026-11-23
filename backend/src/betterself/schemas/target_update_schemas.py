from enum import Enum

from pydantic import BaseModel


class TargetUpdateStatus(str, Enum):
    UPDATED = "updated"
    FAILED = "failed"


"""
Résultat du recalcul automatique de la cible nutritionnelle, joint à la réponse
d'une action qui l'a déclenché (nouvelle mesure, modification du profil).

- updated : une nouvelle cible est active ; les calories avant/après sont fournies.
- failed  : le calcul a échoué, l'ancienne cible est conservée ; `message` explique pourquoi.

Absent (null) lorsque aucun recalcul n'a été tenté.
"""
class TargetUpdateRead(BaseModel):
    status: TargetUpdateStatus
    previous_calories_target_kcal: int | None = None
    calories_target_kcal: int | None = None
    message: str | None = None
