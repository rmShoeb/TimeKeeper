"""Database models for TimeKeeper application."""

from datetime import datetime, date
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    __tablename__ = "User" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tracking_items: list["TrackingItem"] = Relationship(back_populates="user")
    categories: list["Category"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    """Category model for tracking items."""
    __tablename__ = "Category" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    is_predefined: bool = Field(default=False, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="categories")
    tracking_items: list["TrackingItem"] = Relationship(back_populates="category")


class TrackingItem(SQLModel, table=True):
    """Tracking item model for warranties, licenses, subscriptions, etc."""
    __tablename__ = "TrackingItem" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    category_id: int = Field(foreign_key="category.id", index=True)
    reminder_date: date = Field(index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_done: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    user: User = Relationship(back_populates="tracking_items")
    category: Category = Relationship(back_populates="tracking_items")


class OTP(SQLModel, table=True):
    __tablename__ = "OTP" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, max_length=255)
    otp_code: str = Field(max_length=6)
    expires_at: datetime = Field(index=True)
    is_used: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SchedulerRun(SQLModel, table=True):
    __tablename__ = "SchedulerRun" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    job_name: str = Field(unique=True, index=True, max_length=100)
    last_run_at: datetime = Field(index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
