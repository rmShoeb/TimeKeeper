import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from app.services.settings import settings


def setup_logging():
    """Configure environment-aware logging for TimeKeeper."""
    log_format = "[{asctime}] [{levelname}] [{name}] {message}"
    formatter = logging.Formatter(log_format, style="{", datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any default/existing handlers to prevent duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Standard stream handler for live terminal / container logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if settings.ENVIRONMENT == "prod":
        # Prod Environment:
        # Initialize and attach the Better Stack logging transport.
        # Do not attach local file handlers.
        if settings.LOGGER_TOKEN:
            try:
                from logtail import LogtailHandler
                if settings.LOGGER_HOST:
                    logtail_handler = LogtailHandler(
                        source_token=settings.LOGGER_TOKEN,
                        host=settings.LOGGER_HOST
                    )
                else:
                    logtail_handler = LogtailHandler(source_token=settings.LOGGER_TOKEN)
                root_logger.addHandler(logtail_handler)
            except Exception as e:
                root_logger.error(f"Failed to initialize Better Stack logger: {e}")
        else:
            root_logger.warning("LOGGER_TOKEN missing in production. Cloud logging disabled.")
    else:
        # Dev Environment (default):
        # Ensure the target logs directory exists
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        # Attach a TimedRotatingFileHandler:
        # Target file: logs/timekeeper.log
        # Rotation: when="midnight", interval=1
        # Suffix: %Y-%m-%d
        # Backup retention: backupCount=30
        # Do not initialize or attach the Better Stack handler/transport.
        log_file_path = os.path.join(settings.LOG_DIR, "timekeeper.log")
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)