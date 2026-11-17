from collections.abc import Generator

# Doc : docs.sqlalchemy.org/en/21/orm/quickstart.html

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# Importe nos paramètres de configuration depuis le fichier config.py
from betterself.core.config import Settings

settings = Settings()


def create_db_engine(db_url: str):
    # pool_pre_ping vérifie qu'une connexion du pool est toujours vivante avant de l'utiliser.
    # Utile avec PostgreSQL, puisque le serveur peut fermer des connexions inactives
    # (redémarrage, délai d'inactivité de l'hébergeur, etc.).
    return create_engine(db_url, pool_pre_ping=True)


engine = create_db_engine(settings.database_url)


# Définition de la base de données déclarative
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=True,
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
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()