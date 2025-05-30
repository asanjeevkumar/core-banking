import pytest
from collection_service.app import app
from collection_service.app import db as collection_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests_mock
import json

# Define the database URL for the test database
TEST_DATABASE_URL = "sqlite:///:memory:" # Use in-memory SQLite for faster integration tests

@pytest.fixture(scope='function')
def db_session():
    """Fixture to set up a test database and session for each test function."""
    engine = create_engine(TEST_DATABASE_URL)
    # Create tables - assuming Collection Service has its own models or interacts with a shared DB schema
    # For this example, we'll assume it might interact with the Loan Service schema conceptually
    # In a real microservices setup with separate databases, you wouldn't create Loan tables here.
    # This is a simplification for the test setup where we might need a db_session for testing.
    # If the Collection Service purely makes HTTP calls and has no DB of its own, this fixture
    # might not be needed or would be minimal.
    # If it has its own tables, import and create them here.
    # from collection_service.models import Base # Example if collection had models
    # Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    # Clean up the database after each test
    # Base.metadata.drop_all(engine) # Example if collection had models
    session.close()


@pytest.fixture(scope='function')
def client(db_session):
    """Fixture to provide a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URL # Point Flask-SQLAlchemy to test DB
    # Bind the test session to Flask-SQLAlchemy if you are using it in the app
    # collection_db.session = db_session # Example if using Flask-SQLAlchemy directly
    with app.test_client() as client:
        yield client


def test_process_repayment_success(client, db_session):
    """Test the /repayments endpoint for successful repayment processing."""
    loan_id = 123
    # Use Decimal for currency to avoid floating point issues
    from decimal import Decimal
    repayment_amount = 100.0
    initial_outstanding_balance = 500.0
    expected_new_outstanding_balance = initial_outstanding_balance - repayment_amount

    # Mock the HTTP GET request to the Loan Service to get loan details
    with requests_mock.mock() as m:
        m.get(f'http://loan-service:5002/loans/{loan_id}', json={
            'id': loan_id,
            'borrower_id': 456,
            'amount': 1000.0,
            'term': 12,
            'interest_rate': 5.0, # Assuming interest_rate is float
            'outstanding_balance': initial_outstanding_balance,
            'status': 'active'
        }, status_code=200)

        # Mock the HTTP PUT request to the Loan Service to update loan details
        m.put(f'http://loan-service:5002/loans/{loan_id}', status_code=200)

        # Make the POST request to the repayment endpoint
        response = client.post('/repayments', json={
            'loan_id': loan_id,
            'amount': repayment_amount
        })

        # Assert the response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['message'] == 'Repayment processed successfully'
        # In a real scenario, you might assert the updated loan status/balance from the mocked response
        # or if Collection Service had its own DB, check recorded repayment.

        # Verify that the mocked HTTP requests were made
        assert m.called
        assert m.call_count == 2
        assert m.request_history[0].method == 'GET'
        assert m.request_history[0].url == f'http://loan-service:5002/loans/{loan_id}'
        assert m.request_history[1].method == 'PUT'
        assert m.request_history[1].url == f'http://loan-service:5002/loans/{loan_id}'
        # Verify the data sent in the PUT request
        put_data = m.request_history[1].json() # Use .json() for JSON body
        assert put_data['outstanding_balance'] == expected_new_outstanding_balance
        assert put_data['status'] == 'active' # Assuming not fully paid

# Add tests for different scenarios:
# - Repaying more than the outstanding balance
# - Repaying when the loan is already paid off
# - Invalid loan ID
# - Loan Service returns an error (e.g., 404, 500)
# - Invalid request payload (missing loan_id or amount)

def test_process_repayment_loan_not_found(client, db_session):
    """Test the /repayments endpoint when the loan is not found in the Loan Service."""
    loan_id = 999
    repayment_amount = 100.0

    with requests_mock.mock() as m:
        # Mock the HTTP GET request to return 404 (Not Found)
        m.get(f'http://loan-service:5002/loans/{loan_id}', status_code=404)

        # Make the POST request
        response = client.post('/repayments', json={
            'loan_id': loan_id,
            'amount': repayment_amount
        })

        # Assert the response
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'Loan not found' in response_data['message']

        # Verify that the GET request was made and PUT was not
        assert m.called
        assert m.call_count == 1
        assert m.request_history[0].method == 'GET'
        assert m.request_history[0].url == f'http://loan-service:5002/loans/{loan_id}'


def test_process_repayment_loan_service_error(client, db_session):
    """Test the /repayments endpoint when the Loan Service returns an error during GET."""
    loan_id = 123
    repayment_amount = 100.0

    with requests_mock.mock() as m:
        # Mock the HTTP GET request to return 500 (Internal Server Error)
        m.get(f'http://loan-service:5002/loans/{loan_id}', status_code=500)

        # Make the POST request
        response = client.post('/repayments', json={
            'loan_id': loan_id,
            'amount': repayment_amount
        })

        # Assert the response
        assert response.status_code == 500 # Or whatever status code your error handling returns
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'Error communicating with Loan Service' in response_data['message']

        # Verify that the GET request was made and PUT was not
        assert m.called
        assert m.call_count == 1
        assert m.request_history[0].method == 'GET'
        assert m.request_history[0].url == f'http://loan-service:5002/loans/{loan_id}'


def test_process_repayment_invalid_input(client):
    """Test the /repayments endpoint with invalid input payload."""
    # Missing amount
    response_missing_amount = client.post('/repayments', json={'loan_id': 123})
    assert response_missing_amount.status_code == 400
    response_data_missing_amount = json.loads(response_missing_amount.data)
    assert 'message' in response_data_missing_amount

    # Missing loan_id
    response_missing_loan_id = client.post('/repayments', json={'amount': 100.0})
    assert response_missing_loan_id.status_code == 400
    response_data_missing_loan_id = json.loads(response_missing_loan_id.data)
    assert 'message' in response_data_missing_loan_id

    # Invalid amount type
    response_invalid_amount = client.post('/repayments', json={'loan_id': 123, 'amount': 'abc'})
    assert response_invalid_amount.status_code == 400
    response_data_invalid_amount = json.loads(response_invalid_amount.data)
    assert 'message' in response_data_invalid_amount