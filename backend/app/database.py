from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# pool_pre_ping + pool_recycle: the websocket handler holds one DB session
# open for the entire lifetime of a camera connection (potentially hours).
# Without these, a MySQL idle-connection timeout shows up as
# "MySQL server has gone away" the first time recognition tries to write
# after the connection has been sitting idle.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=280,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
