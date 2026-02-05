from sqlmodel import create_engine, Session
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)


def get_session():
    with Session(engine) as session:
        yield session
