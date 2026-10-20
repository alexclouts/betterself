from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from jose import jwt

from betterself.core.config import settings


"""
Fonctions pour le hachage et la vérification des mots de passe en utilisant l'algorithme Argon2.

"""

# Initialisation du hacheur de mots de passe Argon2
pwd_hasher = PasswordHasher()

# Fonction pour hacher un mot de passe
def hash_password(password: str) -> str:
    return pwd_hasher.hash(password)

# Fonction pour vérifier un mot de passe par rapport à son hachage
def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        pwd_hasher.verify(password_hash, plain_password)
        return True
    except VerifyMismatchError:
        return False


"""
Crée un jeton d'accès JWT pour l'utilisateur spécifié.

"""
def create_access_token(subject:str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # Le jeton contient la date d'expiration et l'identifiant de l'utilisateur (subject).
    to_encode = {"exp": expire, "sub": str(subject)}

    # Encode le jeton en utilisant la clé secrète et l'algorithme spécifiés dans les paramètres de configuration.
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt