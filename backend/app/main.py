from contextlib import asynccontextmanager
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.settings import settings
from app.services.database import isDbHealthy
from app.services.logSetup import setup_logging
from app.services.scheduler import start_scheduler, stop_scheduler, run_startup_jobs
from app.routers import auth, categories, tracking_items, user


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TimeKeeper Backend")
    if not isDbHealthy():
        logger.error("Database is not accessible")
        sys.exit(1)

    logger.info("Starting scheduler")
    start_scheduler()

    logger.info("Running startup jobs")
    await run_startup_jobs()

    logger.info("TimeKeeper Backend is ready")

    yield

    logger.info("Shutting down TimeKeeper Backend")
    stop_scheduler()
    logger.info("TimeKeeper Backend shut down successfully")


app = FastAPI(
    title="TimeKeeper API",
    description="Reminder Tracking System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(tracking_items.router)
app.include_router(user.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TimeKeeper API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    db_health_result = isDbHealthy()
    if not db_health_result:
        logger.error("Database is not accessible")
    return {
        "status": "healthy" if db_health_result else "OH NO!",
        "timezone": settings.SCHEDULER_TIMEZONE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
