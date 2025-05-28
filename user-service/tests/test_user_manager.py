import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user_service.models import Base, User, RefreshToken
from user_service.user_manager import UserManager

@pytest.fixture(scope='function')
def db_session():
    """Fixture to provide a in-memory SQLite database session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_user(db_session):
    """Test creating a new user."""
    user_manager = UserManager(db_session)
    user_data = {'username': 'testuser', 'password': 'password123', 'role': 'user'}
    user = user_manager.create_user(user_data)

    assert user is not None
    assert user.username == 'testuser'
    assert user.role == 'user'
    # Note: Password hashing is handled within create_user, so we don't check the raw password here

    # Verify the user is in the database
    retrieved_user = db_session.query(User).filter_by(username='testuser').first()
    assert retrieved_user is not None
    assert retrieved_user.username == 'testuser'

def test_get_user_by_id(db_session):
    """Test getting a user by their ID."""
    user_manager = UserManager(db_session)
    user_data = {'username': 'userbyid', 'password': 'password123', 'role': 'user'}
    created_user = user_manager.create_user(user_data)

    retrieved_user = user_manager.get_user(created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.username == 'userbyid'
    assert retrieved_user.id == created_user.id

    non_existent_user = user_manager.get_user(999)
    assert non_existent_user is None

def test_get_user_by_username(db_session):
    """Test getting a user by their username."""
    user_manager = UserManager(db_session)
    user_data = {'username': 'userbyname', 'password': 'password123', 'role': 'user'}
    user_manager.create_user(user_data)

    retrieved_user = user_manager.get_user_by_username('userbyname')
    assert retrieved_user is not None
    assert retrieved_user.username == 'userbyname'

    non_existent_user = user_manager.get_user_by_username('nonexistent')
    assert non_existent_user is None

def test_update_user(db_session):
    """Test updating user information."""
    user_manager = UserManager(db_session)
    user_data = {'username': 'updateuser', 'password': 'password123', 'role': 'user'}
    created_user = user_manager.create_user(user_data)

    updated_data = {'role': 'admin', 'permissions': 'user:manage'}
    updated_user = user_manager.update_user(created_user.id, updated_data)

    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.role == 'admin'
    assert updated_user.permissions == 'user:manage'

    # Verify changes in the database
    retrieved_user = db_session.query(User).get(created_user.id)
    assert retrieved_user.role == 'admin'
    assert retrieved_user.permissions == 'user:manage'

def test_delete_user(db_session):
    """Test deleting a user."""
    user_manager = UserManager(db_session)
    user_data = {'username': 'deleteuser', 'password': 'password123', 'role': 'user'}
    created_user = user_manager.create_user(user_data)

    user_manager.delete_user(created_user.id)

    # Verify the user is deleted from the database
    deleted_user = db_session.query(User).get(created_user.id)
    assert deleted_user is None

    # Test deleting a non-existent user (should not raise an error)
    user_manager.delete_user(999)