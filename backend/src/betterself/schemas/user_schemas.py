from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# Valide le les données d'entrée pour la création d'un utilisateur
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

# Valide les données d'entrée pour la lecture des informations d'un utilisateur
class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

# Jeton d'accès pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Réponse contenant seulement un message pour l'utilisateur
class MessageResponse(BaseModel):
    message: str

# Jeton reçu par courriel pour confirmer l'adresse
class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1, max_length=128)
    # Mot de passe du compte : prouve que la personne qui confirme est celle qui s'est inscrite.
    password: str = Field(min_length=1, max_length=128)

# Demande d'un nouveau lien de vérification
class ResendVerificationRequest(BaseModel):
    email: EmailStr
