"""Pydantic schemas for request/response validation."""

import re
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.services.settings import settings




# ============= Auth Schemas =============

class EmailRequest(BaseModel):
    """Request schema for OTP request."""
    email: EmailStr


class VerifyOtp(BaseModel):
    """Request schema for OTP verification."""
    email: EmailStr
    otp_code: str

    @field_validator('otp_code')
    def validate_otp_code(cls, otp: str):
        if not otp.isdecimal() or len(otp) != settings.OTP_LENGTH:
            raise ValueError('Invalid OTP')
        return otp


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Category Schemas =============

class CategoryCreateOrUpdate(BaseModel):
    """Request schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    def sanitize_name(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Category can contain alphnumeric characters only')
        return v


class CategoryResponse(BaseModel):
    """Response schema for category."""
    id: int
    name: str
    is_predefined: bool
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Tracking Item Schemas =============

class TrackingItemCreate(BaseModel):
    """Request schema for creating a tracking item."""
    title: str = Field(..., min_length=1, max_length=255)
    category_id: int = Field(..., gt=0)
    reminder_date: date
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('title', 'description')
    def sanitize_string(cls, v):
        if v is None:
            return v
        v = v.strip()
        # Basic XSS prevention
        if '<' in v or '>' in v or 'script' in v.lower():
            raise ValueError('Invalid characters detected')
        return v


class TrackingItemUpdate(BaseModel):
    """Request schema for updating a tracking item."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = Field(None, gt=0)
    reminder_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator('title', 'description')
    def sanitize_string(cls, v):
        if v is None:
            return v
        v = v.strip()
        # Basic XSS prevention
        if '<' in v or '>' in v or 'script' in v.lower():
            raise ValueError('Invalid characters detected')
        return v


class TrackingItemRecreate(BaseModel):
    """Request schema for recreating a tracking item."""
    reminder_date: date


class TrackingItemResponse(BaseModel):
    """Response schema for tracking item."""
    id: int
    user_id: int
    title: str
    category_id: int
    reminder_date: date
    description: Optional[str] = None
    is_done: bool
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""
    items: list
    total: int
    page: int
    pages: int
    page_size: int
