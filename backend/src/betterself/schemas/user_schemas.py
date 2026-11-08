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