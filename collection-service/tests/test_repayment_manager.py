import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collection_service.repayment_manager import RepaymentManager
# Assuming you have models defined somewhere accessible, e.g., in a test_models.py or within the service's models.py
# from collection_service.models import YourModel # If Collection Service has its own models
from unittest.mock import patch, Mock # Using unittest.mock for patching requests
import requests_mock
# Define a base for declarative models (if needed for in-memory db with relations)
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

# Assuming you have a simple Loan model for testing purposes, perhaps in a test_models.py
# or you might need to create a minimal one here for the in-memory db
# Example minimal Loan model (adjust based on your actual Loan model structure)
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    status = Column(String, nullable=False, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add other necessary loan fields

@pytest.fixture(scope="function")
def db_session():
    """Fixture for an in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repayment_manager(db_session):
    """Fixture for RepaymentManager instance with a test session."""
    return RepaymentManager(db_session)

# Mocking the requests library for inter-service communication
# We'll mock specific calls to the Loan Service

def test_process_repayment_success(repayment_manager, db_session):
    """Test processing a successful repayment."""
    loan_id = 1
    repayment_amount = 200.0
    loan_service_url = f'http://loan-service:5002/loans/{loan_id}'

    with requests_mock.mock() as m:
        # Mock the GET request to the Loan Service to return a sample loan
        mock_loan_data = {
            "id": 1,
            "amount": 1000.0,
            "outstanding_balance": 500.0,
            "status": "active"
        }
        m.get(loan_service_url, json=mock_loan_data, status_code=200)

        # Mock the PUT request to the Loan Service to indicate success
        m.put(loan_service_url, status_code=200)

    result = repayment_manager.process_repayment(loan_id, repayment_amount)

    # Calculate the expected new outstanding balance
    expected_new_balance = mock_loan_data['outstanding_balance'] - repayment_amount

    # Assert that the PUT request was made with the updated balance
    mock_put_data = {"outstanding_balance": expected_new_balance}
    assert m.request_history[-1].method == 'PUT'
    assert m.request_history[-1].url == loan_service_url
    assert m.request_history[-1].json() == mock_put_data

    # Assert the result from process_repayment
    assert result is not None # Or assert specific result structure

def test_process_repayment_loan_not_found(repayment_manager, db_session):
    """Test processing a repayment for a loan that does not exist."""
    loan_id = 99
    repayment_amount = 100.0
    loan_service_url = f'http://loan-service:5002/loans/{loan_id}'

    with requests_mock.mock() as m:
        # Mock the GET request to the Loan Service to return a 404
        m.get(loan_service_url, json={"message": "Loan not found"}, status_code=404)

    # Expect a specific exception or return value for loan not found
    with pytest.raises(Exception) as excinfo: # Adjust exception type as needed
        repayment_manager.process_repayment(loan_id, repayment_amount)

    # Assert that the GET request was made and the PUT request was NOT made
    with requests_mock.mock() as m: # Use a new mock context to check history without the failed GET
        repayment_manager.process_repayment(loan_id, repayment_amount) # Re-run to check PUT not called
        assert m.request_history[0].method == 'GET'
        assert m.request_history[0].url == loan_service_url
        assert len(m.request_history) == 1 # Only the GET request should be in history

    # assert "Loan not found" in str(excinfo.value) # Adjust based on actual error handling

def test_process_repayment_amount_exceeds_balance(repayment_manager, db_session):
    """Test processing a repayment amount that exceeds the outstanding balance."""
    # Mock the GET request to return a loan with a balance
    loan_id = 1
    repayment_amount = 200.0 # Exceeds outstanding balance
    loan_service_url = f'http://loan-service:5002/loans/{loan_id}'

    with requests_mock.mock() as m:
        # Mock the GET request to return a loan with a balance
        mock_loan_data = {
            "id": 1,
            "amount": 1000.0,
            "outstanding_balance": 100.0,
            "status": "active"
        }
        m.get(loan_service_url, json=mock_loan_data, status_code=200)

    # Expect a specific exception or handle this case in process_repayment
    with pytest.raises(Exception) as excinfo: # Adjust exception type as needed
         repayment_manager.process_repayment(loan_id, repayment_amount)

    # Assert that the GET request was made and the PUT request was NOT made
    with requests_mock.mock() as m: # Use a new mock context to check history without the failed GET
        # We need to mock the GET again for the second run to not fail immediately
        mock_loan_data = {
            "id": 1,
            "amount": 1000.0,
            "outstanding_balance": 100.0,
            "status": "active"
        }
        m.get(loan_service_url, json=mock_loan_data, status_code=200)

        repayment_manager.process_repayment(loan_id, repayment_amount) # Re-run to check PUT not called
        assert m.request_history[0].method == 'GET'
        assert m.request_history[0].url == loan_service_url
        assert len(m.request_history) == 1 # Only the GET request should be in history

    # Assert the error message or type
    # assert "Repayment amount exceeds outstanding balance" in str(excinfo.value) # Adjust as needed


# Add more tests for edge cases, like:
# - Repayment resulting in exactly zero balance (loan status should become 'paid_off')
# - Negative repayment amounts
# - Handling network errors when communicating with Loan Service