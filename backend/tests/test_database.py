from sqlalchemy.engine import Engine
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column, Session

from betterself.core.database import create_db_engine, get_db, Base
from tests.conftest import TEST_DATABASE_URL

# Teste la création d'un moteur de base de données
def test_create_db_engine():
    # Teste la création d'un moteur de base de données avec une URL PostgreSQL
    engine = create_db_engine(TEST_DATABASE_URL)
    assert isinstance(engine, Engine)
    assert engine.dialect.name == "postgresql"


# Teste le générateur de session de base de données
def test_get_db():
    db_generator = get_db()
    db_session = next(db_generator)

    assert isinstance(db_session, Session)

    db_generator.close()  # Ferme le générateur pour libérer les ressources


# Teste la création d'une table dans la base de données
def test_db_create_table(test_engine):

    class TestTable(Base):
        __tablename__ = "test_table"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]

    try:
        # Crée seulement cette table, sans toucher aux tables de l'application
        TestTable.__table__.create(bind=test_engine)

        inspector = inspect(test_engine)
        # Vérifie que la table a été créée
        assert "test_table" in inspector.get_table_names()
    finally:
        # Nettoie : supprime la table et la retire des métadonnées partagées
        TestTable.__table__.drop(bind=test_engine, checkfirst=True)
        Base.metadata.remove(TestTable.__table__)
