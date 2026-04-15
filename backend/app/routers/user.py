"""User Account API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.database import get_session
from app.dependencies import get_current_user
from app.schemas import DeleteAccountConfirm
from app.crud import otp as otp_crud, user as user_crud, category as category_crud, tracking_item as tracking_item_crud
from app.models import User

router = APIRouter(prefix="/user", tags=["User Account"])


@router.delete("/delete-account", status_code=status.HTTP_200_OK)
async def request_account_deletion(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Request account deletion by sending OTP.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message
    """
    # Create OTP for account deletion confirmation
    otp = otp_crud.create_otp(session, current_user.email)

    # TODO: Send OTP via notification service
    # For now, print to console
    print(f"[OTP] Account deletion OTP for {current_user.email}: {otp.otp_code} (expires in 2 minutes)")

    return {
        "message": "OTP sent successfully for account deletion confirmation",
        "email": current_user.email
    }


@router.post("/confirm-delete", status_code=status.HTTP_200_OK)
async def confirm_account_deletion(
    confirmation: DeleteAccountConfirm,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Confirm account deletion with OTP and delete user account.

    Deletes all user-related data in the following order:
    1. User's tracking items
    2. User's custom categories
    3. User's OTPs
    4. User account

    Args:
        confirmation: Account deletion confirmation with OTP
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If OTP is invalid or expired
    """
    # Verify OTP
    is_valid = otp_crud.verify_otp(session, current_user.email, confirmation.otp_code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )

    # Delete user-related data
    # 1. Delete user's tracking items
    tracking_item_crud.delete_user_tracking_items(session, current_user.id)

    # 2. Delete user's custom categories
    category_crud.delete_user_categories(session, current_user.id)

    # 3. Delete user's OTPs
    otp_crud.delete_user_otps(session, current_user.email)

    # 4. Delete user account
    user_crud.delete_user(session, current_user.id)

    return {
        "message": "Account deleted successfully"
    }
