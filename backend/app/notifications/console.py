"""Console notification service for development."""

import logging
from typing import List
from app.notifications.base import NotificationService
from app.models import TrackingItem
from app.notifications.messages import *


logger = logging.getLogger(__name__)

class ConsoleNotificationService(NotificationService):
    """Console notification service that prints to stdout.

    Used for development and testing purposes.
    """

    def send_otp(self, email: str, otp_code: str) -> bool:
        logger.debug(message_for_send_otp(email, otp_code))
        return True

    def send_reminder(self, email: str, item: TrackingItem) -> bool:
        logger.debug(message_for_single_reminder(email, item))
        return True

    def send_batch_reminders(self, email: str, items: List[TrackingItem]) -> bool:
        logger.debug(message_for_batch_reminder(email, items))
        return True
