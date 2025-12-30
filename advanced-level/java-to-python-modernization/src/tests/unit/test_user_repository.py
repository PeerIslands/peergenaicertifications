"""Unit tests for UserRepository."""
import pytest
from src.api.repositories.user_repository import UserRepository, User


class TestUserRepository:
    """Test cases for UserRepository."""
    
    def test_create_user(self, db_session, sample_user_data):
        """Test creating a new user."""
        repository = UserRepository(db_session)
        user = repository.create(sample_user_data)
        
        assert user.id is not None
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.description == sample_user_data["description"]
    
    def test_get_by_id(self, db_session, sample_user_data):
        """Test getting user by ID."""
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        found_user = repository.get_by_id(created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]
    
    def test_get_by_id_not_found(self, db_session):
        """Test getting user by ID when not found."""
        repository = UserRepository(db_session)
        user = repository.get_by_id(999)
        
        assert user is None
    
    def test_get_by_email(self, db_session, sample_user_data):
        """Test getting user by email."""
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        found_user = repository.get_by_email(sample_user_data["email"])
        
        assert found_user is not None
        assert found_user.email == sample_user_data["email"]
    
    def test_get_by_email_not_found(self, db_session):
        """Test getting user by email when not found."""
        repository = UserRepository(db_session)
        user = repository.get_by_email("nonexistent@example.com")
        
        assert user is None
    
    def test_exists_by_email(self, db_session, sample_user_data):
        """Test checking if user exists by email."""
        repository = UserRepository(db_session)
        
        # Should not exist before creation
        assert repository.exists_by_email(sample_user_data["email"]) is False
        
        # Create user
        repository.create(sample_user_data)
        
        # Should exist after creation
        assert repository.exists_by_email(sample_user_data["email"]) is True
    
    def test_exists_by_id(self, db_session, sample_user_data):
        """Test checking if user exists by ID."""
        repository = UserRepository(db_session)
        
        # Should not exist before creation
        assert repository.exists_by_id(1) is False
        
        # Create user
        created_user = repository.create(sample_user_data)
        
        # Should exist after creation
        assert repository.exists_by_id(created_user.id) is True
    
    def test_update_user(self, db_session, sample_user_data):
        """Test updating a user."""
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        update_data = {"name": "Updated Name", "description": "Updated Description"}
        updated_user = repository.update(created_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        assert updated_user.description == "Updated Description"
        assert updated_user.email == sample_user_data["email"]  # Unchanged
    
    def test_update_user_not_found(self, db_session):
        """Test updating a user that doesn't exist."""
        repository = UserRepository(db_session)
        update_data = {"name": "Updated Name"}
        
        updated_user = repository.update(999, update_data)
        
        assert updated_user is None
    
    def test_delete_user(self, db_session, sample_user_data):
        """Test deleting a user."""
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        result = repository.delete(created_user.id)
        
        assert result is True
        assert repository.get_by_id(created_user.id) is None
    
    def test_delete_user_not_found(self, db_session):
        """Test deleting a user that doesn't exist."""
        repository = UserRepository(db_session)
        result = repository.delete(999)
        
        assert result is False
    
    def test_get_all_users(self, db_session, sample_users_data):
        """Test getting all users."""
        repository = UserRepository(db_session)
        
        # Create multiple users
        for user_data in sample_users_data:
            repository.create(user_data)
        
        all_users = repository.get_all()
        
        assert len(all_users) == len(sample_users_data)
    
    def test_get_all_users_empty(self, db_session):
        """Test getting all users when database is empty."""
        repository = UserRepository(db_session)
        all_users = repository.get_all()
        
        assert len(all_users) == 0
    
    def test_count(self, db_session, sample_users_data):
        """Test counting users."""
        repository = UserRepository(db_session)
        
        assert repository.count() == 0
        
        for user_data in sample_users_data:
            repository.create(user_data)
        
        assert repository.count() == len(sample_users_data)
    
    def test_delete_all(self, db_session, sample_users_data):
        """Test deleting all users."""
        repository = UserRepository(db_session)
        
        # Create users
        for user_data in sample_users_data:
            repository.create(user_data)
        
        assert repository.count() == len(sample_users_data)
        
        # Delete all
        deleted_count = repository.delete_all()
        
        assert deleted_count == len(sample_users_data)
        assert repository.count() == 0
    
    def test_email_uniqueness(self, db_session, sample_user_data):
        """Test that email uniqueness is enforced at database level."""
        from sqlalchemy.exc import IntegrityError
        
        repository = UserRepository(db_session)
        repository.create(sample_user_data)
        
        # Try to create another user with same email
        # This should raise an IntegrityError when commit is called
        user = User(**sample_user_data)
        db_session.add(user)
        try:
            with pytest.raises(IntegrityError):
                db_session.commit()
        finally:
            # Rollback to clear the failed transaction
            db_session.rollback()

