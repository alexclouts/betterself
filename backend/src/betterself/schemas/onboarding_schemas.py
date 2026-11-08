from pydantic import BaseModel

# Schéma de lecture du statut d'intégration d'un utilisateur, indiquant quelles étapes ont été complétées et lesquelles manquent.
class OnboardingStatusRead(BaseModel):
    is_complete: bool
    missing_steps: list[str]
    steps: dict[str, bool]