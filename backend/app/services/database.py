import logging
import time
from sqlmodel import create_engine, Session, text
from app.services.settings import settings


logger = logging.getLogger(__name__)
engine = create_engine(
    settings.DATABASE_URL, # type: ignore
    echo=False,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {} # type: ignore
)


def get_session():
    with Session(engine) as session:
        yield session


def isDbHealthy(retries: int = 3, delay: int = 3) -> bool:
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"DB health check attempt {i+1} failed for error {e}")
            time.sleep(delay)
    logger.error("Could not connect to database. Check logs for details.")
    return False