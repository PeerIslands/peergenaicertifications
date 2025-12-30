"""Integration tests for User API endpoints."""
import pytest
from fastapi import status


class TestUserAPI:
    """Integration tests for user API endpoints."""
    
    def test_get_all_users_empty(self, client):
        """Test getting all users when database is empty."""
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) == 0
        assert data["total"] == 0
    
    def test_create_user(self, client, sample_user_data):
        """Test creating a new user via API."""
        response = client.post("/api/users", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert data["description"] == sample_user_data["description"]
    
    def test_create_user_duplicate_email(self, client, sample_user_data):
        """Test creating user with duplicate email returns 400."""
        # Create first user
        client.post("/api/users", json=sample_user_data)
        
        # Try to create another with same email
        response = client.post("/api/users", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_user_validation_error(self, client):
        """Test creating user with invalid data returns 422."""
        invalid_data = {
            "name": "A",  # Too short (min 2)
            "email": "invalid-email",  # Invalid email
            "description": "A" * 201  # Too long (max 200)
        }
        
        response = client.post("/api/users", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_user_by_id(self, client, sample_user_data):
        """Test getting user by ID via API."""
        # Create user
        create_response = client.post("/api/users", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Get user
        response = client.get(f"/api/users/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]
    
    def test_get_user_by_id_not_found(self, client):
        """Test getting user by ID when not found returns 404."""
        response = client.get("/api/users/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_user_by_email(self, client, sample_user_data):
        """Test getting user by email via API."""
        # Create user
        client.post("/api/users", json=sample_user_data)
        
        # Get user by email
        response = client.get(f"/api/users/email/{sample_user_data['email']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]
    
    def test_get_user_by_email_not_found(self, client):
        """Test getting user by email when not found returns 404."""
        response = client.get("/api/users/email/nonexistent@example.com")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_all_users_with_data(self, client, sample_users_data):
        """Test getting all users when data exists."""
        # Create multiple users
        for user_data in sample_users_data:
            client.post("/api/users", json=user_data)
        
        # Get all users
        response = client.get("/api/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["users"]) == len(sample_users_data)
        assert data["total"] == len(sample_users_data)
    
    def test_update_user(self, client, sample_user_data):
        """Test updating a user via API."""
        # Create user
        create_response = client.post("/api/users", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Update user
        update_data = {
            "name": "Updated Name",
            "description": "Updated Description"
        }
        response = client.put(f"/api/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated Description"
        assert data["email"] == sample_user_data["email"]  # Unchanged
    
    def test_update_user_not_found(self, client):
        """Test updating user that doesn't exist returns 404."""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/users/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_user_duplicate_email(self, client, sample_users_data):
        """Test updating user with duplicate email returns 400."""
        # Create two users
        user1_response = client.post("/api/users", json=sample_users_data[0])
        user2_response = client.post("/api/users", json=sample_users_data[1])
        
        user1_id = user1_response.json()["id"]
        user2_email = user2_response.json()["email"]
        
        # Try to update user1 with user2's email
        update_data = {"email": user2_email}
        response = client.put(f"/api/users/{user1_id}", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_delete_user(self, client, sample_user_data):
        """Test deleting a user via API."""
        # Create user
        create_response = client.post("/api/users", json=sample_user_data)
        user_id = create_response.json()["id"]
        
        # Delete user
        response = client.delete(f"/api/users/{user_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify user is deleted
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_user_not_found(self, client):
        """Test deleting user that doesn't exist returns 404."""
        response = client.delete("/api/users/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/users/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert "running" in response.json()["message"].lower()
    
    def test_root_health_check(self, client):
        """Test root health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    def test_crud_workflow(self, client):
        """Test complete CRUD workflow."""
        # Create
        user_data = {
            "name": "Workflow User",
            "email": "workflow@example.com",
            "description": "Testing workflow"
        }
        create_response = client.post("/api/users", json=user_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        user_id = create_response.json()["id"]
        
        # Read
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["name"] == user_data["name"]
        
        # Update
        update_data = {"name": "Updated Workflow User"}
        update_response = client.put(f"/api/users/{user_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["name"] == "Updated Workflow User"
        
        # Delete
        delete_response = client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_after_delete = client.get(f"/api/users/{user_id}")
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND

