import pytest
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user_service.app import app
from user_service.models import Base, User
from user_service.user_manager import UserManager

# Use a separate database for testing
TEST_DATABASE_URL = "sqlite:///./test_user_service.db"

@pytest.fixture(scope="session")
def db_engine():
    """Fixture to provide a database engine for the test session."""
    engine = create_engine(TEST_DATABASE_URL)
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    yield engine
    # Drop tables after the session finishes
    Base.metadata.drop_all(engine)
    # Remove the test database file
    if os.path.exists("./test_user_service.db"):
        os.remove("./test_user_service.db")


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fixture to provide a database session for each test function."""
    connection = db_engine.connect()
    # Begin a non-autocommitting transaction
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    # Roll back the transaction after each test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture to provide a Flask test client with a mocked database session."""
    app.config['TESTING'] = True
    # Temporarily override the db_session in the app context for testing
    # This is a simplified approach, in a real app you might use dependency injection
    # or mock the session at a lower level.
    original_db_session = app.config.get('DB_SESSION')
    app.config['DB_SESSION'] = db_session

    with app.test_client() as client:
        yield client

    # Restore the original db_session
    if original_db_session is not None:
        app.config['DB_SESSION'] = original_db_session
    else:
         del app.config['DB_SESSION']


def test_create_user(client):
    """Test creating a new user."""
    user_data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
        "full_name": "Test User"
    }
    response = client.post('/users', data=json.dumps(user_data), content_type='application/json')

    assert response.status_code == 201
    response_data = response.json
    assert "user_id" in response_data
    assert response_data["username"] == "testuser"
    assert response_data["email"] == "test@example.com"
    assert response_data["full_name"] == "Test User"


def test_get_user_by_id(client, db_session):
    """Test getting a user by their ID."""
    # Create a user directly in the database
    created_user = User(username="anotheruser", password="securepass", email="another@example.com", full_name="Another User")
    db_session.add(created_user)
    db_session.commit()

    response = client.get(f'/users/{created_user.user_id}')

    assert response.status_code == 200
    response_data = response.json
    assert response_data["user_id"] == created_user.user_id
    assert response_data["username"] == "anotheruser"


def test_get_user_by_id_not_found(client):
    """Test getting a non-existent user by ID."""
    response = client.get('/users/9999')
    assert response.status_code == 404


def test_get_user_by_username(client, db_session):
    """Test getting a user by their username."""
    # Create a user directly in the database
    created_user = User(username="usernameonly", password="mypass", email="username@example.com", full_name="Username User")
    db_session.add(created_user)
    db_session.commit()

    response = client.get(f'/users?username={created_user.username}')

    assert response.status_code == 200
    response_data = response.json
    assert response_data["user_id"] == created_user.user_id
    assert response_data["username"] == "usernameonly"


def test_get_user_by_username_not_found(client):
    """Test getting a non-existent user by username."""
    response = client.get('/users?username=nonexistent')
    assert response.status_code == 404


def test_update_user(client, db_session):
    """Test updating an existing user."""
    # Create a user directly in the database
    created_user = User(username="updateuser", password="oldpass", email="old@example.com", full_name="Old Name")
    db_session.add(created_user)
    db_session.commit()

    update_data = {
        "email": "new@example.com",
        "full_name": "New Name"
    }
    response = client.put(f'/users/{created_user.user_id}', data=json.dumps(update_data), content_type='application/json')

    assert response.status_code == 200
    response_data = response.json
    assert response_data["user_id"] == created_user.user_id
    assert response_data["email"] == "new@example.com"
    assert response_data["full_name"] == "New Name"

    # Verify user was updated in the database
    updated_user = User.query.filter_by(user_id=created_user.user_id).first() # Assuming User model has a query attribute or similar
    assert updated_user.email == "new@example.com"
    assert updated_user.full_name == "New Name"


def test_update_user_not_found(client):
    """Test updating a non-existent user."""
    update_data = {"email": "new@example.com"}
    response = client.put('/users/9999', data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 404


def test_delete_user(client, db_session):
    """Test deleting a user."""
    # Create a user directly in the database
    user_to_delete = User(username="todelete", password="pass", email="delete@example.com", full_name="To Delete User")
    db_session.add(user_to_delete)
    db_session.commit()

    response = client.delete(f'/users/{user_to_delete.user_id}')

    assert response.status_code == 200
    response_data = response.json
    assert response_data["message"] == "User deleted successfully"

    # Verify user was deleted from the database
    deleted_user = User.query.filter_by(user_id=user_to_delete.user_id).first() # Assuming User model has a query attribute or similar
    assert deleted_user is None


def test_delete_user_not_found(client):
    """Test deleting a non-existent user."""
    response = client.delete('/users/9999')
    assert response.status_code == 404


def test_create_user_invalid_data(client):
    """Test creating a user with invalid data."""
    user_data = {
        "username": "", # Invalid username
        "password": "password123",
        "email": "test@example.com",
        "full_name": "Test User"
    }
    response = client.post('/users', data=json.dumps(user_data), content_type='application/json')
    assert response.status_code == 400 # Or appropriate validation error code


def test_update_user_invalid_data(client, db_session):
    """Test updating a user with invalid data."""
    user_to_update = User(username="invalidupdate", password="pass", email="valid@example.com", full_name="Valid User")
    db_session.add(user_to_update)
    db_session.commit()

    update_data = {
        "email": "not-an-email", # Invalid email
    }
    response = client.put(f'/users/{user_to_update.user_id}', data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 400 # Or appropriate validation error code