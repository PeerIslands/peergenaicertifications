"""Unit tests for UserService."""
import pytest
from fastapi import HTTPException
from src.api.services.user_service import UserService
from src.api.models.user import UserCreate, UserUpdate


class TestUserService:
    """Test cases for UserService."""
    
    def test_get_all_users(self, db_session, sample_users_data):
        """Test getting all users."""
        # Create users directly in repository
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        for user_data in sample_users_data:
            repository.create(user_data)
        
        service = UserService(db_session)
        users = service.get_all_users()
        
        assert len(users) == len(sample_users_data)
    
    def test_get_user_by_id(self, db_session, sample_user_data):
        """Test getting user by ID."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        service = UserService(db_session)
        user = service.get_user_by_id(created_user.id)
        
        assert user is not None
        assert user.email == sample_user_data["email"]
    
    def test_get_user_by_id_not_found(self, db_session):
        """Test getting user by ID when not found."""
        service = UserService(db_session)
        user = service.get_user_by_id(999)
        
        assert user is None
    
    def test_get_user_by_email(self, db_session, sample_user_data):
        """Test getting user by email."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        repository.create(sample_user_data)
        
        service = UserService(db_session)
        user = service.get_user_by_email(sample_user_data["email"])
        
        assert user is not None
        assert user.email == sample_user_data["email"]
    
    def test_create_user_success(self, db_session):
        """Test creating a user successfully."""
        service = UserService(db_session)
        user_data = UserCreate(
            name="New User",
            email="newuser@example.com",
            description="New Description"
        )
        
        user = service.create_user(user_data)
        
        assert user.id is not None
        assert user.name == "New User"
        assert user.email == "newuser@example.com"
    
    def test_create_user_duplicate_email(self, db_session, sample_user_data):
        """Test creating user with duplicate email raises exception."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        repository.create(sample_user_data)
        
        service = UserService(db_session)
        user_data = UserCreate(
            name="Another User",
            email=sample_user_data["email"],  # Duplicate email
            description="Another Description"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_user(user_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()
    
    def test_update_user_success(self, db_session, sample_user_data):
        """Test updating a user successfully."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        service = UserService(db_session)
        update_data = UserUpdate(
            name="Updated Name",
            description="Updated Description"
        )
        
        updated_user = service.update_user(created_user.id, update_data)
        
        assert updated_user.name == "Updated Name"
        assert updated_user.description == "Updated Description"
        assert updated_user.email == sample_user_data["email"]  # Unchanged
    
    def test_update_user_not_found(self, db_session):
        """Test updating a user that doesn't exist."""
        service = UserService(db_session)
        update_data = UserUpdate(name="Updated Name")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_user(999, update_data)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_update_user_duplicate_email(self, db_session, sample_users_data):
        """Test updating user with duplicate email raises exception."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        user1 = repository.create(sample_users_data[0])
        user2 = repository.create(sample_users_data[1])
        
        service = UserService(db_session)
        update_data = UserUpdate(email=user2.email)  # Try to use user2's email
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_user(user1.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail.lower()
    
    def test_update_user_same_email_allowed(self, db_session, sample_user_data):
        """Test updating user with same email is allowed."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        service = UserService(db_session)
        update_data = UserUpdate(
            name="Updated Name",
            email=created_user.email  # Same email
        )
        
        updated_user = service.update_user(created_user.id, update_data)
        
        assert updated_user.email == created_user.email
        assert updated_user.name == "Updated Name"
    
    def test_delete_user_success(self, db_session, sample_user_data):
        """Test deleting a user successfully."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        service = UserService(db_session)
        service.delete_user(created_user.id)
        
        # Verify user is deleted
        assert repository.get_by_id(created_user.id) is None
    
    def test_delete_user_not_found(self, db_session):
        """Test deleting a user that doesn't exist."""
        service = UserService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_user(999)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_update_user_partial_update(self, db_session, sample_user_data):
        """Test partial update of user (only some fields)."""
        from src.api.repositories.user_repository import UserRepository
        repository = UserRepository(db_session)
        created_user = repository.create(sample_user_data)
        
        service = UserService(db_session)
        update_data = UserUpdate(name="Only Name Updated")
        
        updated_user = service.update_user(created_user.id, update_data)
        
        assert updated_user.name == "Only Name Updated"
        assert updated_user.email == sample_user_data["email"]  # Unchanged
        assert updated_user.description == sample_user_data["description"]  # Unchanged

