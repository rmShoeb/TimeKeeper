"""Tracking Item API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from app.services.database import get_session
from app.dependencies import get_current_user
from app.schemas import (
    TrackingItemCreate,
    TrackingItemUpdate,
    TrackingItemRecreate,
    TrackingItemResponse,
    PaginatedResponse
)
from app.crud import tracking_item as tracking_item_crud
from app.models import User

router = APIRouter(prefix="/items", tags=["Tracking Items"])


@router.get("/upcoming", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
async def get_upcoming_items(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get upcoming tracking items (is_done=False, reminder_date >= today).

    Items are paginated and ordered by reminder_date ascending (earliest first).
    Page size is validated against [10, 20, 50].

    Args:
        page: Page number (1-indexed)
        limit: Items per page
        current_user: Current authenticated user
        session: Database session

    Returns:
        Paginated response with upcoming items
    """
    result = tracking_item_crud.get_upcoming_items(session, current_user.id, page, limit)

    return PaginatedResponse(
        items=[TrackingItemResponse.from_orm(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
        page_size=result["page_size"]
    )


@router.get("/past", response_model=PaginatedResponse, status_code=status.HTTP_200_OK)
async def get_past_items(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get past tracking items (is_done=True).

    Items are paginated and ordered by created_at descending (latest first).
    Page size is validated against [10, 20, 50].

    Args:
        page: Page number (1-indexed)
        limit: Items per page
        current_user: Current authenticated user
        session: Database session

    Returns:
        Paginated response with past items
    """
    result = tracking_item_crud.get_past_items(session, current_user.id, page, limit)

    return PaginatedResponse(
        items=[TrackingItemResponse.from_orm(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
        page_size=result["page_size"]
    )


@router.post("", response_model=TrackingItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: TrackingItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new tracking item.

    Args:
        item_data: Tracking item creation data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Created tracking item
    """
    item = tracking_item_crud.create_item(session, current_user.id, item_data)
    return TrackingItemResponse.from_orm(item)


@router.put("/{item_id}", response_model=TrackingItemResponse, status_code=status.HTTP_200_OK)
async def update_item(
    item_id: int,
    item_data: TrackingItemUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a tracking item (only if is_done=False).

    Args:
        item_id: Tracking item ID
        item_data: Tracking item update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated tracking item

    Raises:
        HTTPException: If item not found, not owned by user, or already completed
    """
    # Check if item exists
    item = tracking_item_crud.get_item_by_id(session, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this item"
        )

    # Check if item is done
    if item.is_done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify completed items"
        )

    # Update item
    updated_item = tracking_item_crud.update_item(session, item_id, current_user.id, item_data)

    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update item"
        )

    return TrackingItemResponse.from_orm(updated_item)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a tracking item (only if is_done=False).

    Args:
        item_id: Tracking item ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If item not found, not owned by user, or already completed
    """
    # Check if item exists
    item = tracking_item_crud.get_item_by_id(session, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    # Check if item is done
    if item.is_done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete completed items"
        )

    # Delete item
    success = tracking_item_crud.delete_item(session, item_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete item"
        )

    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/recreate", response_model=TrackingItemResponse, status_code=status.HTTP_201_CREATED)
async def recreate_item(
    item_id: int,
    recreate_data: TrackingItemRecreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Recreate a tracking item with a new date.

    Copies all fields from the original item except reminder_date and resets is_done to False.

    Args:
        item_id: Original tracking item ID
        recreate_data: Recreate data containing new reminder date
        current_user: Current authenticated user
        session: Database session

    Returns:
        New tracking item

    Raises:
        HTTPException: If item not found or not owned by user
    """
    # Check if item exists
    item = tracking_item_crud.get_item_by_id(session, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Check ownership
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to recreate this item"
        )

    # Recreate item
    new_item = tracking_item_crud.recreate_item(
        session, item_id, current_user.id, recreate_data.reminder_date
    )

    if not new_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to recreate item"
        )

    return TrackingItemResponse.from_orm(new_item)
