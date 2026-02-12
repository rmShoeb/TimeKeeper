from app.internalModels import Message

def message_for_send_otp(to_email: str, otp_code: str) -> Message:
    content = f"Your OTP code is: {otp_code}. This code will expire in 2 minutes."
    return Message("OTP NOTIFICATION", to_email, "Your TimeKeeper OTP Code", content)