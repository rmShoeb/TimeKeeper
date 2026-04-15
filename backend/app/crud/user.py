"""CRUD operations for User model."""

from typing import Optional
from sqlmodel import Session, select
from app.models import User


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email address.

    Args:
        session: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user


def create_user(session: Session, email: str) -> User:
    """Create a new user.

    Args:
        session: Database session
        email: User's email address

    Returns:
        Created User object
    """
    user = User(email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    """Delete a user.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        True if user was deleted, False if not found
    """
    user = get_user_by_id(session, user_id)
    if not user:
        return False

    session.delete(user)
    session.commit()
    return True
