from abc import ABC, abstractmethod
from typing import List
from app.models import TrackingItem


class NotificationService(ABC):
    """Abstract base class for notification services."""

    @abstractmethod
    def send_otp(self, email: str, otp_code: str) -> bool:
        """Send OTP to user's email.

        Args:
            email: Recipient email address
            otp_code: 6-digit OTP code

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def send_reminder(self, email: str, item: TrackingItem) -> bool:
        """Send reminder notification for a single tracking item.

        Args:
            email: Recipient email address
            item: TrackingItem object

        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def send_batch_reminders(self, email: str, items: List[TrackingItem]) -> bool:
        """Send batch reminder notification for multiple tracking items.

        Args:
            email: Recipient email address
            items: List of TrackingItem objects

        Returns:
            True if sent successfully, False otherwise
        """
        pass
