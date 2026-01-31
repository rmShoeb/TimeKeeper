"""CRUD operations for OTP model."""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models import OTP
from app.auth import generate_otp
from app.config import settings


def create_otp(session: Session, email: str) -> OTP:
    """Create a new OTP for the given email.

    Deletes any existing OTPs for this email before creating a new one.

    Args:
        session: Database session
        email: User's email address

    Returns:
        Created OTP object
    """
    # Delete any existing OTPs for this email
    statement = select(OTP).where(OTP.email == email)
    existing_otps = session.exec(statement).all()
    for otp in existing_otps:
        session.delete(otp)

    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_VALIDITY_MINUTES)

    otp = OTP(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )
    session.add(otp)
    session.commit()
    session.refresh(otp)

    return otp


def verify_otp(session: Session, email: str, otp_code: str) -> bool:
    """Verify OTP for the given email.

    Security: Deletes OTP immediately after successful verification for better
    security, privacy compliance, and data minimization (GDPR).

    Args:
        session: Database session
        email: User's email address
        otp_code: OTP code to verify

    Returns:
        True if OTP is valid, False otherwise
    """
    statement = select(OTP).where(
        OTP.email == email,
        OTP.otp_code == otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.utcnow()
    )
    otp = session.exec(statement).first()

    if not otp:
        return False

    # Delete immediately after successful verification
    # Benefits: Better security, privacy compliance, data minimization
    session.delete(otp)
    session.commit()

    return True


def cleanup_expired_otps(session: Session) -> int:
    """Delete expired OTPs.

    Args:
        session: Database session

    Returns:
        Number of OTPs deleted
    """
    statement = select(OTP).where(OTP.expires_at < datetime.utcnow())
    expired_otps = session.exec(statement).all()

    count = len(expired_otps)
    for otp in expired_otps:
        session.delete(otp)

    session.commit()
    return count


def delete_user_otps(session: Session, email: str) -> int:
    """Delete all OTPs for a user.

    Args:
        session: Database session
        email: User's email address

    Returns:
        Number of OTPs deleted
    """
    statement = select(OTP).where(OTP.email == email)
    otps = session.exec(statement).all()

    count = len(otps)
    for otp in otps:
        session.delete(otp)

    session.commit()
    return count
