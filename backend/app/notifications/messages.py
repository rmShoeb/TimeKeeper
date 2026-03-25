from typing import List

from app.internalModels import Message
from app.models import TrackingItem

def message_for_send_otp(to_email: str, otp_code: str) -> Message:
    content = f"Your OTP code is: {otp_code}. This code will expire in 2 minutes."
    return Message("OTP NOTIFICATION", to_email, "Your TimeKeeper OTP Code", content)

def message_for_single_reminder(to_email: str, item: TrackingItem) -> Message:
    content = f"You have a reminder today for item: {item.title}, Category: {item.category.name if item.category else 'N/A'}"
    if item.description:
        content += f"Description: {item.description}"
    return Message("REMINDER NOTIFICATION", to_email, f"TimeKeeper Alert for item {item.title}", content)

def message_for_batch_reminder(to_email: str, items: List[TrackingItem]) -> Message:
    content = f"You have {len(items)} reminder(s) today.\n"
    for idx, item in enumerate(items, 1):
        content += f"\n\t{idx}. {item.title}"
        content += f"\n\tCategory: {item.category.name if item.category else 'N/A'}"
        if item.description:
            content += f"\n\tDescription: {item.description}"
        content += "\n"
    return Message("REMINDER NOTIFICATION", to_email, f"TimeKeeper Alert for {len(items)} item(s)", content)
