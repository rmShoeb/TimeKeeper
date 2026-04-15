"""Category API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.database import get_session
from app.dependencies import get_current_user
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as category_crud
from app.models import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all categories available to the user (predefined + user's custom).

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        List of categories
    """
    categories = category_crud.get_categories_for_user(session, current_user.id)
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new user-specific category.

    Args:
        category_data: Category creation data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Created category
    """
    category = category_crud.create_user_category(session, current_user.id, category_data.name)
    return category


@router.put("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a user's custom category.

    Cannot update predefined categories.

    Args:
        category_id: Category ID
        category_data: Category update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated category

    Raises:
        HTTPException: If category not found or cannot be modified
    """
    # Check if category exists and get it
    category = category_crud.get_category_by_id(session, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if it's a predefined category
    if category.is_predefined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify predefined categories"
        )

    # Check ownership
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this category"
        )

    # Update category
    updated_category = category_crud.update_user_category(
        session, category_id, current_user.id, category_data.name
    )

    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update category"
        )

    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a user's custom category.

    Cannot delete predefined categories.

    Args:
        category_id: Category ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If category not found or cannot be deleted
    """
    # Check if category exists and get it
    category = category_crud.get_category_by_id(session, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if it's a predefined category
    if category.is_predefined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete predefined categories"
        )

    # Check ownership
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this category"
        )

    # Delete category
    success, error_message = category_crud.delete_user_category(session, category_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Failed to delete category"
        )

    return {"message": "Category deleted successfully"}
