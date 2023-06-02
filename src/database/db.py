from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError

from src.conf.config import settings

print("+++++++++++++++++++++++++++", settings.sqlalchemy_database_url)
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except DatabaseError: # noqa
        db.rollback()
    finally:
        db.close()
