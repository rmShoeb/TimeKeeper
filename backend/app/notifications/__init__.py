"""Notification service factory."""

from app.notifications.base import NotificationService
from app.notifications.console import ConsoleNotificationService
from app.notifications.email import EmailService


def get_notification_service(mode: str = "console") -> NotificationService:
    """Factory function to get notification service based on mode.

    Args:
        mode: Notification mode ("console", "email")

    Returns:
        NotificationService instance

    Raises:
        ValueError: If mode is not supported
    """
    if mode == "console":
        return ConsoleNotificationService()
    # Future implementations
    elif mode == "email":
        return EmailService()
    else:
        raise ValueError(f"Unsupported notification mode: {mode}")
