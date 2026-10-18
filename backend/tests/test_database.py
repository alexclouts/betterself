from sqlalchemy.engine import Engine
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column, Session

from betterself.core.database import create_db_engine, get_db, Base

# Teste la création d'un moteur de base de données
def test_create_db_engine():
    # Teste la création d'un moteur de base de données avec une URL SQLite
    engine = create_db_engine("sqlite:///./test.db")
    assert isinstance(engine, Engine)


# Teste le générateur de session de base de données
def test_get_db():
    db_generator = get_db()
    db_session = next(db_generator)

    assert isinstance(db_session, Session)
    
    db_generator.close()  # Ferme le générateur pour libérer les ressources


# Teste la création d'une table dans la base de données
def test_db_create_table():
    engine = create_db_engine("sqlite:///./test.db")

    class TestTable(Base):
        __tablename__ = "test_table"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]

    # Crée la table dans la base de données
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    # Vérifie que la table a été créée
    assert "test_table" in inspector.get_table_names()

    # Nettoie en supprimant la table après le test
    Base.metadata.drop_all(bind=engine)
