"""User API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ..services.user_service import UserService
from ..models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    ErrorResponse
)
from ..repositories.user_repository import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="Get all users",
    description="Retrieve a list of all users in the system"
)
def get_all_users(db: Session = Depends(get_db)):
    """
    Get all users.
    
    Returns:
        UserListResponse with list of users and total count
    """
    service = UserService(db)
    users = service.get_all_users()
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=len(users)
    )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the User API is running",
    response_model=dict
)
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status message
    """
    return {"status": "healthy", "message": "User API is running!"}


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    summary="Get user by email",
    description="Retrieve a specific user by their email address",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Get user by email address.
    
    Args:
        email: Email address to search for
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException: 404 if user not found
    """
    service = UserService(db)
    user = service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with email: {email}"
        )
    
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    
    Args:
        user_id: User ID to retrieve
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException: 404 if user not found
    """
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with id: {user_id}"
        )
    
    return UserResponse.model_validate(user)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided information",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or email already exists"}
    }
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Args:
        user_data: UserCreate model with user information
        
    Returns:
        UserResponse with created user data
        
    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    service = UserService(db)
    user = service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update an existing user",
    description="Update user information by ID",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or email conflict"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing user.
    
    Args:
        user_id: User ID to update
        user_data: UserUpdate model with updated information
        
    Returns:
        UserResponse with updated user data
        
    Raises:
        HTTPException: 404 if user not found, 400 if email conflict
    """
    service = UserService(db)
    user = service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Delete a user by ID",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    
    Args:
        user_id: User ID to delete
        
    Raises:
        HTTPException: 404 if user not found
    """
    service = UserService(db)
    service.delete_user(user_id)

