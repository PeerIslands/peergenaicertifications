"""User data models for API requests and responses."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    description: Optional[str] = Field(None, max_length=200, description="Optional user description")


class UserCreate(UserBase):
    """Model for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Model for updating an existing user (all fields optional)."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    description: Optional[str] = Field(None, max_length=200)


class UserResponse(UserBase):
    """Model for user response."""
    id: int = Field(..., description="User ID")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Model for list of users response."""
    users: list[UserResponse]
    total: int


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str
    detail: Optional[str] = None

