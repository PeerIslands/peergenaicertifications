"""User repository for database operations."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime

from ...config.database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    """User database model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_all(self) -> List[User]:
        """
        Get all users from database.
        
        Returns:
            List of all User objects
        """
        return self.db.query(User).all()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists with given email.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def exists_by_id(self, user_id: int) -> bool:
        """
        Check if user exists with given ID.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user exists, False otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first() is not None
    
    def create(self, user_data: dict) -> User:
        """
        Create a new user.
        
        Args:
            user_data: Dictionary with user data (name, email, description)
            
        Returns:
            Created User object
        """
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id: User ID to update
            user_data: Dictionary with updated user data
            
        Returns:
            Updated User object if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def count(self) -> int:
        """
        Get total count of users.
        
        Returns:
            Total number of users
        """
        return self.db.query(User).count()
    
    def delete_all(self) -> int:
        """
        Delete all users (used for testing/data initialization).
        
        Returns:
            Number of users deleted
        """
        count = self.count()
        self.db.query(User).delete()
        self.db.commit()
        return count

