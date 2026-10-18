from pydantic_settings import BaseSettings

"""
Ce fichier sert à déclarer les paramètres du projet. 
Il contient :
    1. Les chemins de fichiers ou de dossiers (données, résultats, modèles).
    2. Les paramètres de simulation ou d’analyse : nombre d’itérations, taille de population, probabilités, seuils.
    3. Les identifiants, URLs, adresses IP ou noms d’hôtes utilisés par le programme.
    4. Les options d’exécution : mode débogage, niveau de journalisation, environnement de développement ou de production.
    5. Les variables sensibles, idéalement chargées depuis des variables d’environnement plutôt qu’écrites directement dans le fichier.
"""

class Settings(BaseSettings):
    database_url: str = "sqlite:///./betterself.db"
    secret_key: str = "change-me-in-development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()