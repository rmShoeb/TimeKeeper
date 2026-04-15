from datetime import date
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from app.models import TrackingItem, Category
from app.schemas import TrackingItemCreate, TrackingItemUpdate

# Page size validation constants
ALLOWED_PAGE_SIZES = [10, 20, 50]
DEFAULT_PAGE_SIZE = 10


def validate_page_size(limit: int) -> int:
    """Validate and sanitize page size to prevent malicious queries.

    Args:
        limit: Requested page size

    Returns:
        Validated page size (defaults to DEFAULT_PAGE_SIZE if invalid)
    """
    if limit not in ALLOWED_PAGE_SIZES:
        return DEFAULT_PAGE_SIZE
    return limit


def get_upcoming_items(session: Session, user_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """Get upcoming tracking items (is_done=False, reminder_date >= today).

    Items are ordered by reminder_date ascending (earliest first).
    Page size is validated against ALLOWED_PAGE_SIZES.

    Args:
        session: Database session
        user_id: User's ID
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Dictionary with items, total, page, pages, and page_size
    """
    # Validate limit to prevent malicious large queries
    limit = validate_page_size(limit)

    skip = (page - 1) * limit

    # Query for upcoming items
    statement = select(TrackingItem).where(
        TrackingItem.user_id == user_id,
        TrackingItem.is_done == False,
        TrackingItem.reminder_date >= date.today()
    ).order_by(TrackingItem.reminder_date.asc()) # type: ignore

    # Get total count
    #! instead of running the complete query, have to find a way to execute count by SQL
    total_statement = select(TrackingItem).where(
        TrackingItem.user_id == user_id,
        TrackingItem.is_done == False,
        TrackingItem.reminder_date >= date.today()
    )
    total = len(session.exec(total_statement).all())

    # Get paginated items
    items = session.exec(statement.offset(skip).limit(limit)).all()

    # Load category relationship for each item
    for item in items:
        if item.category_id:
            category_statement = select(Category).where(Category.id == item.category_id)
            item.category = session.exec(category_statement).first()

    return {
        "items": list(items),
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total > 0 else 1,
        "page_size": limit
    }


def get_past_items(session: Session, user_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """Get past tracking items (is_done=True).

    Items are ordered by created_at descending (latest first).
    Page size is validated against ALLOWED_PAGE_SIZES.

    Args:
        session: Database session
        user_id: User's ID
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Dictionary with items, total, page, pages, and page_size
    """
    # Validate limit to prevent malicious large queries
    limit = validate_page_size(limit)

    skip = (page - 1) * limit

    # Query for past items
    statement = select(TrackingItem).where(
        TrackingItem.user_id == user_id,
        TrackingItem.is_done == True
    ).order_by(TrackingItem.created_at.desc()) # type: ignore

    # Get total count
    total_statement = select(TrackingItem).where(
        TrackingItem.user_id == user_id,
        TrackingItem.is_done == True
    )
    total = len(session.exec(total_statement).all())

    # Get paginated items
    items = session.exec(statement.offset(skip).limit(limit)).all()

    # Load category relationship for each item
    for item in items:
        if item.category_id:
            category_statement = select(Category).where(Category.id == item.category_id)
            item.category = session.exec(category_statement).first()

    return {
        "items": list(items),
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total > 0 else 1,
        "page_size": limit
    }


def get_item_by_id(session: Session, item_id: int) -> Optional[TrackingItem]:
    """Get tracking item by ID.

    Args:
        session: Database session
        item_id: Tracking item ID

    Returns:
        TrackingItem object if found, None otherwise
    """
    statement = select(TrackingItem).where(TrackingItem.id == item_id)
    item = session.exec(statement).first()

    # Load category relationship
    if item and item.category_id:
        category_statement = select(Category).where(Category.id == item.category_id)
        item.category = session.exec(category_statement).first()

    return item


def create_item(session: Session, user_id: int, item_data: TrackingItemCreate) -> TrackingItem:
    """Create a new tracking item.

    Args:
        session: Database session
        user_id: User's ID
        item_data: Tracking item data

    Returns:
        Created TrackingItem object
    """
    item = TrackingItem(
        user_id=user_id,
        title=item_data.title,
        category_id=item_data.category_id,
        reminder_date=item_data.reminder_date,
        description=item_data.description,
        is_done=False
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    # Load category relationship
    if item.category_id:
        category_statement = select(Category).where(Category.id == item.category_id)
        item.category = session.exec(category_statement).first()

    return item


def update_item(session: Session, item_id: int, user_id: int, item_data: TrackingItemUpdate) -> Optional[TrackingItem]:
    """Update a tracking item (only if is_done=False).

    Args:
        session: Database session
        item_id: Tracking item ID
        user_id: User's ID
        item_data: Updated tracking item data

    Returns:
        Updated TrackingItem object if successful, None otherwise
    """
    item = get_item_by_id(session, item_id)

    if not item:
        return None

    # Check ownership and ensure item is not done
    if item.user_id != user_id or item.is_done:
        return None

    # Update fields
    if item_data.title is not None:
        item.title = item_data.title
    if item_data.category_id is not None:
        item.category_id = item_data.category_id
    if item_data.reminder_date is not None:
        item.reminder_date = item_data.reminder_date
    if item_data.description is not None:
        item.description = item_data.description

    session.add(item)
    session.commit()
    session.refresh(item)

    # Load category relationship
    if item.category_id:
        category_statement = select(Category).where(Category.id == item.category_id)
        item.category = session.exec(category_statement).first()

    return item


def delete_item(session: Session, item_id: int, user_id: int) -> bool:
    """Delete a tracking item (only if is_done=False).

    Args:
        session: Database session
        item_id: Tracking item ID
        user_id: User's ID

    Returns:
        True if item was deleted, False otherwise
    """
    item = get_item_by_id(session, item_id)

    if not item:
        return False

    # Check ownership and ensure item is not done
    if item.user_id != user_id or item.is_done:
        return False

    session.delete(item)
    session.commit()
    return True


def recreate_item(session: Session, item_id: int, user_id: int, new_date: date) -> Optional[TrackingItem]:
    """Recreate a tracking item with a new date.

    Copies all fields except reminder_date and resets is_done to False.

    Args:
        session: Database session
        item_id: Original tracking item ID
        user_id: User's ID
        new_date: New reminder date

    Returns:
        New TrackingItem object if successful, None otherwise
    """
    original_item = get_item_by_id(session, item_id)

    if not original_item or original_item.user_id != user_id:
        return None

    # Create new item with copied fields
    new_item = TrackingItem(
        user_id=user_id,
        title=original_item.title,
        category_id=original_item.category_id,
        reminder_date=new_date,
        description=original_item.description,
        is_done=False
    )
    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    # Load category relationship
    if new_item.category_id:
        category_statement = select(Category).where(Category.id == new_item.category_id)
        new_item.category = session.exec(category_statement).first()

    return new_item


def get_items_due_today(session: Session) -> List[TrackingItem]:
    """Get all tracking items due today (for scheduler).

    Args:
        session: Database session

    Returns:
        List of TrackingItem objects due today
    """
    statement = select(TrackingItem).where(
        TrackingItem.reminder_date == date.today(),
        TrackingItem.is_done == False
    )
    items = session.exec(statement).all()

    # Load user and category relationships
    for item in items:
        if item.category_id:
            category_statement = select(Category).where(Category.id == item.category_id)
            item.category = session.exec(category_statement).first()

    return list(items)


def mark_item_done(session: Session, item_id: int) -> bool:
    """Mark a tracking item as done.

    Args:
        session: Database session
        item_id: Tracking item ID

    Returns:
        True if item was marked as done, False if not found
    """
    item = get_item_by_id(session, item_id)

    if not item:
        return False

    item.is_done = True
    session.add(item)
    session.commit()
    return True


def delete_old_records(session: Session, cutoff_date: date) -> int:
    """Delete tracking items older than cutoff_date.

    Args:
        session: Database session
        cutoff_date: Items with created_at before this date will be deleted

    Returns:
        Number of items deleted
    """
    statement = select(TrackingItem).where(
        TrackingItem.created_at < cutoff_date
    )
    old_items = session.exec(statement).all()

    count = len(old_items)
    for item in old_items:
        session.delete(item)

    session.commit()
    return count


def delete_user_tracking_items(session: Session, user_id: int) -> int:
    """Delete all tracking items for a user.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        Number of items deleted
    """
    statement = select(TrackingItem).where(TrackingItem.user_id == user_id)
    items = session.exec(statement).all()

    count = len(items)
    for item in items:
        session.delete(item)

    session.commit()
    return count
