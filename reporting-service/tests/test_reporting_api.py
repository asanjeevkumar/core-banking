import pytest
from reporting_service.app import app
from reporting_service.reporting_manager import ReportingManager
import requests_mock

# Define a fixture for the Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Define a fixture for requests_mock
@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

# Test case for generating active loans report
def test_get_active_loans_report(client, mock_requests):
    # Mock the GET request to the Loan Service to get loan data
    mock_requests.get('http://loan-service:5002/loans', json=[
        {"id": 1, "borrower_id": 101, "amount": 10000, "outstanding_balance": 5000.0, "status": "active"},
        {"id": 2, "borrower_id": 102, "amount": 20000, "outstanding_balance": 0, "status": "paid-off"},
        {"id": 3, "borrower_id": 103, "amount": 15000, "outstanding_balance": 15000, "status": "active"},
    ])

    # Mock the GET request to the Collection Service to get repayment data (if needed for this report)
    # For this example, we assume active loans report only needs loan data, so no collection service mock needed here.

    response = client.get('/reports/active-loans')
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data) == 2
    # Add assertions based on the expected active loans from the mocked data
    assert any(loan['id'] == 1 for loan in data)
    assert any(loan['id'] == 3 for loan in data)
    assert not any(loan['id'] == 2 for loan in data)

# Test case for generating paid-off loans report
def test_get_paid_off_loans_report(client, mock_requests):
    # Mock the GET request to the Loan Service to get loan data
    mock_requests.get('http://loan-service:5002/loans', json=[
        {"id": 1, "borrower_id": 101, "amount": 10000, "outstanding_balance": 5000.0, "status": "active"},
        {"id": 2, "borrower_id": 102, "amount": 20000, "outstanding_balance": 0, "status": "paid-off"},
        {"id": 3, "borrower_id": 103, "amount": 15000, "outstanding_balance": 15000, "status": "active"},
    ])

    # Mock the GET request to the Collection Service to get repayment data (if needed)
    # For this example, we assume paid-off loans report only needs loan data.

    response = client.get('/reports/paid-off-loans')
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data) == 1
    # Add assertions based on the expected paid-off loans from the mocked data
    assert data[0]['id'] == 2

# Test case for handling an invalid report type (example)
def test_get_invalid_report(client):
    response = client.get('/reports/non-existent-report')
    assert response.status_code == 404 # Assuming your app returns 404 for unknown report types
    data = response.get_json()
    assert data == {"error": "Invalid report type"} # Assuming your app returns a JSON error message

# Add more integration tests for other reporting scenarios and error cases