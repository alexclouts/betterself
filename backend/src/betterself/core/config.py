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
    # Valeur par défaut alignée sur docker-compose.yml (développement local seulement).
    # En production, DATABASE_URL doit être fournie par une variable d'environnement.
    database_url: str = "postgresql+psycopg://betterself:betterself@localhost:5432/betterself"
    secret_key: str = "change-me-in-development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    # Catalogue Open Food Facts (off.sqlite). Facultatif : sans lui, la recherche se
    # limite aux aliments déjà présents dans la base de données.
    off_catalog_path: str | None = None
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Envoi des courriels. Les valeurs par défaut pointent vers Mailpit
    # (docker-compose.yml), qui intercepte les courriels en développement.
    # En production, ces valeurs viennent des variables d'environnement du fournisseur.
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: str | None = None
    # STARTTLS chiffre la connexion; Mailpit ne le demande pas, un vrai fournisseur oui.
    smtp_starttls: bool = False
    mail_from: str = "BetterSelf <no-reply@betterself.local>"
    # Adresse qui reçoit les réponses aux courriels envoyés. Facultative.
    mail_reply_to: str | None = None
    # Adresse du frontend, utilisée pour construire les liens envoyés par courriel.
    frontend_url: str = "http://localhost:5173"
    # Durée de validité d'un lien de vérification du courriel.
    email_verification_expire_hours: int = 24
    # Délai minimal entre deux envois du lien de vérification, contre les abus.
    email_verification_resend_seconds: int = 60

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()