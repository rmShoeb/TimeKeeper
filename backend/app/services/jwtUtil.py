from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.services.settings import settings


def create_access_token(data: dict) -> str:
    """Create JWT access token.

    Args:
        data: Dictionary containing user data (e.g., {"user_id": 1})

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # type: ignore
    to_encode.update({
        "exp": expire,
        "iat": datetime.now()
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM) # type: ignore
    return encoded_jwt


def verify_token(token: str) -> int:
    """Verify JWT token and extract user_id.

    Args:
        token: JWT token string

    Returns:
        User ID from token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]) # type: ignore
        user_id: Optional[int] = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user information not found"
            )
        return user_id
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
