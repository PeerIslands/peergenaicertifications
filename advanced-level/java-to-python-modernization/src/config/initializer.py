"""Data initialization for seeding sample users."""
from sqlalchemy.orm import Session

from .database import SessionLocal, init_db
from ..api.repositories.user_repository import UserRepository, User


def initialize_data() -> None:
    """
    Initialize database with sample data.
    Clears existing data and creates 5 sample users.
    """
    # Initialize database tables
    init_db()
    
    # Create database session
    db: Session = SessionLocal()
    try:
        repository = UserRepository(db)
        
        # Clear existing data
        repository.delete_all()
        print("Cleared existing data")
        
        # Create sample users (matching legacy Java implementation)
        sample_users = [
            {"name": "John Doe", "email": "john.doe@example.com", "description": "Software Developer"},
            {"name": "Jane Smith", "email": "jane.smith@example.com", "description": "Product Manager"},
            {"name": "Bob Johnson", "email": "bob.johnson@example.com", "description": "Data Analyst"},
            {"name": "Alice Brown", "email": "alice.brown@example.com", "description": "UX Designer"},
            {"name": "Charlie Wilson", "email": "charlie.wilson@example.com", "description": "DevOps Engineer"},
        ]
        
        for user_data in sample_users:
            repository.create(user_data)
        
        total_users = repository.count()
        print(f"Sample data initialized successfully!")
        print(f"Total users created: {total_users}")
        
    finally:
        db.close()

