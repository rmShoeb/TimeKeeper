import logging
import sys
from logtail import LogtailHandler
from app.services.settings import settings


def setup_logging():
    log_format = "[{asctime}] [{levelname}] [{name}] {message}"
    formatter = logging.Formatter(log_format, style="{", datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any default handlers to prevent duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if settings.LOGGER_TOKEN:
        logtail_handler = LogtailHandler(source_token=settings.LOGGER_TOKEN)
        root_logger.addHandler(logtail_handler)
    else:
        root_logger.warning("BetterStack token missing. Cloud logging disabled.")

    # Silence noisy libraries (Optional)
    # Prevents third-party logs from drowning out your app logic
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)