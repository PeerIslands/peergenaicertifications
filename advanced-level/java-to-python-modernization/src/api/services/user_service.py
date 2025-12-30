"""User service for business logic."""
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException

from ..repositories.user_repository import UserRepository, User
from ..models.user import UserCreate, UserUpdate


class UserService:
    """Service for user business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.repository = UserRepository(db)
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List of all User objects
        """
        return self.repository.get_all()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.repository.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.repository.get_by_email(email)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: UserCreate model with user data
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If email already exists (400)
        """
        if self.repository.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail=f"User with email {user_data.email} already exists"
            )
        
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "description": user_data.description
        }
        
        return self.repository.create(user_dict)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update an existing user.
        
        Args:
            user_id: User ID to update
            user_data: UserUpdate model with updated data
            
        Returns:
            Updated User object
            
        Raises:
            HTTPException: If user not found (404) or email conflict (400)
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id: {user_id}"
            )
        
        # Check email uniqueness if email is being updated
        if user_data.email is not None and user_data.email != user.email:
            if self.repository.exists_by_email(user_data.email):
                raise HTTPException(
                    status_code=400,
                    detail=f"User with email {user_data.email} already exists"
                )
        
        # Build update dictionary (only include non-None values)
        update_dict = {}
        if user_data.name is not None:
            update_dict["name"] = user_data.name
        if user_data.email is not None:
            update_dict["email"] = user_data.email
        if user_data.description is not None:
            update_dict["description"] = user_data.description
        
        updated_user = self.repository.update(user_id, update_dict)
        if not updated_user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id: {user_id}"
            )
        
        return updated_user
    
    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID.
        
        Args:
            user_id: User ID to delete
            
        Raises:
            HTTPException: If user not found (404)
        """
        if not self.repository.exists_by_id(user_id):
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id: {user_id}"
            )
        
        self.repository.delete(user_id)

