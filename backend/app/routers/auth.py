"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.database import get_session
from app.dependencies import get_current_user
from app.schemas import EmailRequest, OTPVerifyRequest, TokenResponse, UserResponse
from app.crud import otp as otp_crud, user as user_crud
from app.services.jwtUtil import create_access_token
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(
    request: EmailRequest,
    session: Session = Depends(get_session)
):
    """Request OTP for email-based authentication.

    Generates a 6-digit OTP and sends it via the configured notification service.

    Args:
        request: Email request containing user's email
        session: Database session

    Returns:
        Success message
    """
    # Create OTP (this also deletes any existing OTPs for this email)
    otp = otp_crud.create_otp(session, request.email)

    # TODO: Send OTP via notification service
    # For now, print to console
    print(f"[OTP] OTP for {request.email}: {otp.otp_code} (expires in 2 minutes)")

    return {
        "message": "OTP sent successfully",
        "email": request.email
    }


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    request: OTPVerifyRequest,
    session: Session = Depends(get_session)
):
    """Verify OTP and return JWT token.

    If the user doesn't exist, creates a new user.

    Args:
        request: OTP verification request containing email and OTP code
        session: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If OTP is invalid or expired
    """
    # Verify OTP
    is_valid = otp_crud.verify_otp(session, request.email, request.otp_code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Get or create user
    user = user_crud.get_user_by_email(session, request.email)
    if not user:
        user = user_crud.create_user(session, request.email)

    # Create JWT token
    access_token = create_access_token({"user_id": user.id})

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user
