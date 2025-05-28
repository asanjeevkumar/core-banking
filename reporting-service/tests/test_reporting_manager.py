import pytest
from unittest.mock import patch, Mock
# If you prefer using requests_mock, install it and import here
# import requests_mock

from reporting_service.reporting_manager import ReportingManager

# Assuming your ReportingManager is a class and requires a db_session
# If it's just functions, you might adjust this.
# Also, assuming a basic structure of data returned by other services

class TestReportingManager:

    @pytest.fixture
    def mock_db_session(self):
        # Provide a mock database session if ReportingManager interacts with its own DB
        # Otherwise, you might not need this.
        return Mock()

    @pytest.fixture
    def reporting_manager(self, mock_db_session):
        return ReportingManager(mock_db_session)

    # Example test for generating active loans report, mocking HTTP requests
    @patch('requests.get')
    def test_generate_active_loans_report(self, mock_get, reporting_manager):
        # Configure the mock to return a specific response for the Loan Service endpoint
        mock_loan_service_response = Mock()
        mock_loan_service_response.status_code = 200
        # Simulate the data structure returned by the Loan Service for active loans
        mock_loan_service_response.json.return_value = [
            {'id': 1, 'amount': 1000, 'status': 'active', 'borrower_id': 101},
            {'id': 2, 'amount': 2000, 'status': 'active', 'borrower_id': 102},
        ]
        # Map the URL to the mock response
        mock_get.return_value = mock_loan_service_response

        # Call the method under test
        active_loans = reporting_manager.generate_active_loans_report()

        # Assertions to check the report content
        assert isinstance(active_loans, list)
        assert len(active_loans) == 2
        assert active_loans[0]['status'] == 'active'
        assert active_loans[1]['status'] == 'active'

        # Verify that the correct HTTP request was made
        mock_get.assert_called_once_with('http://loan-service:5002/loans/active') # Adjust URL as per your implementation

    # Example test for generating paid-off loans report, mocking HTTP requests
    @patch('requests.get')
    def test_generate_paid_off_loans_report(self, mock_get, reporting_manager):
        mock_loan_service_response = Mock()
        mock_loan_service_response.status_code = 200
        mock_loan_service_response.json.return_value = [
            {'id': 3, 'amount': 500, 'status': 'paid_off', 'borrower_id': 103},
        ]
        mock_get.return_value = mock_loan_service_response

        paid_off_loans = reporting_manager.generate_paid_off_loans_report()

        assert isinstance(paid_off_loans, list)
        assert len(paid_off_loans) == 1
        assert paid_off_loans[0]['status'] == 'paid_off'

        mock_get.assert_called_once_with('http://loan-service:5002/loans/paid-off') # Adjust URL as per your implementation

    # Add more tests for other report types and edge cases (e.g., empty results, errors)