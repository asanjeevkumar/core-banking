import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loan_service.app import app
from loan_service.models import Base

# Define a temporary database URL for testing
TEST_DATABASE_URL = "sqlite:///./test_loan_service.db"


@pytest.fixture(scope="module")
def test_app():
    """Fixture to provide the Flask app for testing."""
    app.config['TESTING'] = True
    # Temporarily override database URL for testing
    original_db_url = app.config.get('DATABASE_URL')
    app.config['DATABASE_URL'] = TEST_DATABASE_URL

    # Create the database and tables
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    # Use a context manager to ensure the app context is pushed
    with app.app_context():
        yield app

    # Clean up the database after tests
    Base.metadata.drop_all(bind=engine)
    # Restore original database URL
    app.config['DATABASE_URL'] = original_db_url


@pytest.fixture(scope="function")
def client(test_app):
    """Fixture to provide a test client for the Flask app."""
    return test_app.test_client()


@pytest.fixture(scope="function")
def db_session(test_app):
    """Fixture to provide a database session for testing."""
    engine = create_engine(TEST_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()  # Roll back any changes made during the test
    session.close()


def test_create_borrower(client):
    """Test the endpoint for creating a borrower."""
    borrower_data = {
        "name": "Test Borrower",
        "email": "test.borrower@example.com",
        "user_id": "borrower123"  # Assuming user_id from User Service
    }
    response = client.post("/borrowers", json=borrower_data)
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert "id" in response_data
    assert response_data["name"] == borrower_data["name"]


def test_get_borrower_by_id(client, db_session):
    """Test the endpoint for getting a borrower by ID."""
    # Create a borrower directly in the database for testing
    from loan_service.models import Borrower
    borrower = Borrower(name="Existing Borrower", email="existing.borrower@example.com", user_id="existing456")
    db_session.add(borrower)
    db_session.commit()
    borrower_id = borrower.id

    response = client.get(f"/borrowers/{borrower_id}")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["id"] == borrower_id
    assert response_data["name"] == "Existing Borrower"


def test_create_loan(client, db_session):
    """Test the endpoint for creating a loan."""
    # Create a borrower directly in the database for testing (needed for loan creation)
    from loan_service.models import Borrower
 borrower = Borrower(name="Loan Taker", email="loan.taker@example.com", user_id="user123")  # Use a consistent user ID for potential future mocking
    db_session.add(borrower)
    db_session.commit()
    borrower_id = borrower.id

    loan_data = {
        "borrower_id": borrower_id,
        "amount": 10000.00,
        "interest_rate": 5.5,
        "term_months": 60
    }

    # Note: Mocking the User Service call would be needed here for a true integration test
    # For simplicity, this test assumes the User Service call in create_loan succeeds or is mocked elsewhere
    # Example of how you might mock:
    # import requests_mock
    # with requests_mock.mock() as m:
    #     m.get(f"http://user-service:5001/users/{borrower_data['user_id']}", json={"id": borrower_data['user_id'], "username": "testuser"})
    response = client.post("/loans", json=loan_data)

    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert "id" in response_data
    assert response_data["borrower_id"] == borrower_id
    assert response_data["amount"] == loan_data["amount"]
    assert response_data["status"] == "active"


def test_get_loan_by_id(client, db_session):
    """Test the endpoint for getting a loan by ID."""
    # Create a borrower and a loan directly in the database for testing
    from loan_service.models import Borrower, Loan
    borrower = Borrower(name="Loan Getter", email="loan.getter@example.com", user_id="getter101")
    db_session.add(borrower)
    db_session.commit()
    borrower_id = borrower.id

    loan = Loan(
        borrower_id=borrower_id,
        amount=5000.00,
        outstanding_balance=5000.00,
        interest_rate=6.0,
        term_months=36,
        status="active"
    )
    db_session.add(loan)
    db_session.commit()
    loan_id = loan.id

    response = client.get(f"/loans/{loan_id}")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["id"] == loan_id
    assert response_data["borrower_id"] == borrower_id
    assert response_data["amount"] == 5000.00


def test_get_all_loans(client, db_session):
    """Test the endpoint for getting all loans."""
    # Create some borrowers and loans directly in the database
 from loan_service.models import Borrower, Loan
 borrower1 = Borrower(name="Borrower One", email="one@example.com", user_id="user456") # Use consistent user IDs
    borrower2 = Borrower(name="Borrower Two", email="two@example.com", user_id="two2")
    db_session.add_all([borrower1, borrower2])
    db_session.commit()

    loan1 = Loan(borrower_id=borrower1.id, amount=1000, outstanding_balance=1000, interest_rate=5, term_months=12, status="active")
    loan2 = Loan(borrower_id=borrower2.id, amount=2000, outstanding_balance=2000, interest_rate=6, term_months=24, status="active")
    db_session.add_all([loan1, loan2])
    db_session.commit()

    response = client.get("/loans")
    assert response.status_code == 200
    response_data = json.loads(response.data)
 assert isinstance(response_data, list)
    assert len(response_data) >= 2 # Account for other tests potentially adding loans
    # Basic check for structure
    assert "id" in response_data[0]
    assert "borrower_id" in response_data[0]
    assert "amount" in response_data[0]


# Add more specific assertions based on the data created
# Add tests for handling invalid requests and errors
def test_create_borrower_invalid_data(client):
    """Test creating a borrower with invalid data."""
    invalid_data = {"name": "Invalid Borrower"} # Missing email and user_id
    response = client.post("/borrowers", json=invalid_data)
    assert response.status_code == 400


def test_get_nonexistent_borrower(client):
    """Test getting a borrower that does not exist."""
    response = client.get("/borrowers/9999") # Assuming 9999 is a non-existent ID
 assert response.status_code == 404 # Or the appropriate error status code


def test_create_loan_invalid_data(client):
    """Test creating a loan with invalid data."""
    invalid_data = {"borrower_id": 1, "amount": -100} # Invalid amount
    response = client.post("/loans", json=invalid_data)
    assert response.status_code == 400


def test_get_nonexistent_loan(client):
    """Test getting a loan that does not exist."""
    response = client.get("/loans/9999") # Assuming 9999 is a non-existent ID
 assert response.status_code == 404 # Or the appropriate error status code