from collections.abc import Generator

# Doc : docs.sqlalchemy.org/en/21/orm/quickstart.html

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# Importe nos paramètres de configuration depuis le fichier config.py
from betterself.core.config import Settings

settings = Settings()


def create_db_engine(db_url: str):
    connect_args = {}

    # L'argument check_same_thread est nécessaire pour SQLite, mais pas pour d'autres bases de données.
    # Il permet à SQLite de fonctionner correctement dans un environnement multi-thread, comme celui utilisé par FastAPI.
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(db_url, connect_args=connect_args)


engine = create_db_engine(settings.database_url)


# Définition de la base de données déclarative
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Class de base pour tous les modèles SQLAlchemy
class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données.
    Utilisé pour obtenir une session de base de données dans les routes FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()