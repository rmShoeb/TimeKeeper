import secrets

def generate_otp() -> str:
    """Generate cryptographically secure 6-digit OTP.

    Returns:
        6-digit OTP string
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)]) # type: ignore