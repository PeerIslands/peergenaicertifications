"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.config.database import Base, get_db
# Import User model to ensure it's registered with Base
from src.api.repositories.user_repository import User
from main import app

# Test database URL (use file-based SQLite for tests to avoid connection issues)
TEST_DATABASE_URL = "sqlite:///./test_users.db"

# Create test engine with pool_pre_ping to ensure connections are valid
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after test
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    session = TestSessionLocal()
    try:
        yield session
        # Only commit if there are pending changes and no errors
        if session.in_transaction():
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "description": "Test Description"
    }


@pytest.fixture
def sample_users_data():
    """Multiple sample users for testing."""
    return [
        {"name": "John Doe", "email": "john@example.com", "description": "Developer"},
        {"name": "Jane Smith", "email": "jane@example.com", "description": "Manager"},
        {"name": "Bob Johnson", "email": "bob@example.com", "description": "Analyst"},
    ]

