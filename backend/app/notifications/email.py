import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.internalModels import Message
from app.models import TrackingItem
from app.notifications.base import NotificationService
from app.notifications.messages import *
from app.services.settings import settings
import logging

logger = logging.getLogger(__name__)


class EmailService(NotificationService):
    """SMTP email notification service.
    """

    def __init__(self):
        """Initialize SMTP email service.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            smtp_from: From email address
            smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, smtp_from: str
        """
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
    
    def _send_email(self, messageObject: Message):
        if not self.smtp_host or not self.smtp_port or not self.smtp_user or not self.smtp_password:
            logger.error("SMTP credentials not set. Cannot send email.")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_from # type: ignore
            msg["To"] = messageObject.to_email
            msg["Subject"] = messageObject.subject
            msg.attach(MIMEText(messageObject.content, "plain"))

            # Connect to server
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Secure the connection
            server.login(self.smtp_user, self.smtp_password)
            
            # Send
            server.sendmail(self.smtp_from, messageObject.to_email, msg.as_string()) # type: ignore
            server.quit()
            
            logger.info(f"Email sent successfully to {messageObject.to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {messageObject.to_email}: {str(e)}")
            return False

    def send_otp(self, email: str, otp_code: str) -> bool:
        return self._send_email(message_for_send_otp(email, otp_code))

    def send_reminder(self, email: str, item: TrackingItem) -> bool:
        return self._send_email(message_for_single_reminder(email, item))

    def send_batch_reminders(self, email: str, items: List[TrackingItem]) -> bool:
        return self._send_email(message_for_batch_reminder(email, items))
