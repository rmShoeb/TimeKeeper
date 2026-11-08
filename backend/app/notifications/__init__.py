"""Notification service factory."""

from app.notifications.base import NotificationService
from app.notifications.console import ConsoleNotificationService
from app.notifications.email import EmailService
from app.services.settings import settings


def get_notification_service() -> NotificationService:
    """Factory function to get notification service based on mode.

    Args:
        mode: Notification mode ("console", "email")

    Returns:
        NotificationService instance

    Raises:
        ValueError: If mode is not supported
    """
    if settings.NOTIFICATION_MODE == "console":
        return ConsoleNotificationService()
    # Future implementations
    elif settings.NOTIFICATION_MODE == "email":
        return EmailService()
    else:
        raise ValueError(f"Unsupported notification mode: {settings.NOTIFICATION_MODE}")
