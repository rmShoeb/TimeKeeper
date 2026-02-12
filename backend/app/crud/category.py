from typing import List, Optional
from sqlmodel import Session, select, or_
from app.models import Category, TrackingItem


def get_categories_for_user(session: Session, user_id: int) -> List[Category]:
    """Get all categories available to a user (predefined + user's custom).

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        List of Category objects
    """
    statement = select(Category).where(
        or_(
            Category.is_predefined == True,
            Category.user_id == user_id
        )
    ).order_by(Category.is_predefined.desc(), Category.name) # type: ignore

    categories = session.exec(statement).all()
    return list(categories)


def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    """Get category by ID.

    Args:
        session: Database session
        category_id: Category ID

    Returns:
        Category object if found, None otherwise
    """
    statement = select(Category).where(Category.id == category_id)
    category = session.exec(statement).first()
    return category


def create_user_category(session: Session, user_id: int, name: str) -> Category:
    """Create a user-specific category.

    Args:
        session: Database session
        user_id: User's ID
        name: Category name

    Returns:
        Created Category object
    """
    category = Category(
        name=name,
        is_predefined=False,
        user_id=user_id
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_user_category(session: Session, category_id: int, user_id: int, name: str) -> Optional[Category]:
    """Update a user's custom category.

    Args:
        session: Database session
        category_id: Category ID
        user_id: User's ID
        name: New category name

    Returns:
        Updated Category object if successful, None if category not found or not owned by user
    """
    category = get_category_by_id(session, category_id)

    if not category:
        return None

    # Check ownership and prevent modification of predefined categories
    if category.is_predefined or category.user_id != user_id:
        return None

    category.name = name
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def is_category_in_use(session: Session, category_id: int) -> bool:
    """Check if a category is being used by any tracking items.

    Args:
        session: Database session
        category_id: Category ID

    Returns:
        True if category is in use, False otherwise
    """
    statement = select(TrackingItem).where(TrackingItem.category_id == category_id).limit(1)
    item = session.exec(statement).first()
    return item is not None


def delete_user_category(session: Session, category_id: int, user_id: int) -> tuple[bool, str | None]:
    """Delete a user's custom category.

    Args:
        session: Database session
        category_id: Category ID
        user_id: User's ID

    Returns:
        Tuple of (success: bool, error_message: str | None)
        - (True, None) if category was deleted
        - (False, error_message) if deletion failed
    """
    category = get_category_by_id(session, category_id)

    if not category:
        return False, "Category not found"

    # Check ownership and prevent deletion of predefined categories
    if category.is_predefined:
        return False, "Cannot delete predefined categories"

    if category.user_id != user_id:
        return False, "You don't have permission to delete this category"

    # Check if category is in use
    if is_category_in_use(session, category_id):
        return False, "Cannot delete category that is being used by tracking items. Please reassign or delete those items first."

    session.delete(category)
    session.commit()
    return True, None


def delete_user_categories(session: Session, user_id: int) -> int:
    """Delete all of a user's custom categories.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        Number of categories deleted
    """
    statement = select(Category).where(
        Category.user_id == user_id,
        Category.is_predefined == False
    )
    categories = session.exec(statement).all()

    count = len(categories)
    for category in categories:
        session.delete(category)

    session.commit()
    return count
