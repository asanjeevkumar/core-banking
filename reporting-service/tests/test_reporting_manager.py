import pytest
import requests_mock

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
    @requests_mock.mock
    def test_generate_active_loans_report(self, m, reporting_manager):
        # Configure the mock to return a specific response for the Loan Service endpoint
        # Simulate the data structure returned by the Loan Service for active loans
        loan_service_url = 'http://loan-service:5002/loans/active' # Adjust URL as per your implementation
        m.get(loan_service_url, json=[
            {'id': 1, 'amount': 1000, 'status': 'active', 'borrower_id': 101},
            {'id': 2, 'amount': 2000, 'status': 'active', 'borrower_id': 102},
        ], status_code=200)

        # Call the method under test
        active_loans = reporting_manager.generate_active_loans_report()

        # Assertions to check the report content
        assert isinstance(active_loans, list)
        assert len(active_loans) == 2
        assert all(loan['status'] == 'active' for loan in active_loans)

        # Verify that the correct HTTP request was made
        assert m.called_once_with(loan_service_url)

    # Example test for generating paid-off loans report, mocking HTTP requests
    @requests_mock.mock
    def test_generate_paid_off_loans_report(self, m, reporting_manager):
        loan_service_url = 'http://loan-service:5002/loans/paid-off' # Adjust URL as per your implementation
        m.get(loan_service_url, json=[
            {'id': 3, 'amount': 500, 'status': 'paid_off', 'borrower_id': 103},
        ], status_code=200)

        paid_off_loans = reporting_manager.generate_paid_off_loans_report()

        assert isinstance(paid_off_loans, list)
        assert len(paid_off_loans) == 1
        assert paid_off_loans[0]['status'] == 'paid_off'

        assert m.called_once_with(loan_service_url)

    # Add test for generating a report that requires data from both Loan and Collection Services
    @requests_mock.mock
    def test_generate_loans_with_repayments_report(self, m, reporting_manager):
        loan_service_url = 'http://loan-service:5002/loans' # Adjust URL as per your implementation
        collection_service_url = 'http://collection-service:5003/repayments' # Adjust URL as per your implementation

        m.get(loan_service_url, json=[
            {'id': 1, 'amount': 1000, 'status': 'active', 'borrower_id': 101},
            {'id': 2, 'amount': 2000, 'status': 'paid_off', 'borrower_id': 102},
        ], status_code=200)

        m.get(collection_service_url, json=[
            {'id': 10, 'loan_id': 1, 'amount': 500, 'payment_date': '2023-01-15'},
            {'id': 11, 'loan_id': 1, 'amount': 500, 'payment_date': '2023-02-15'},
            {'id': 12, 'loan_id': 2, 'amount': 2000, 'payment_date': '2022-12-01'},
        ], status_code=200)

        # Assuming ReportingManager has a method for this report, e.g., generate_loans_with_repayments
        # This part of the test needs to be adapted based on your ReportingManager implementation
        # For demonstration, let's assume it fetches all loans and all repayments and combines them

        # Since ReportingManager currently only has generate_active_loans_report and generate_paid_off_loans_report
        # and doesn't combine data from both services in those methods, this test needs a corresponding method
        # in ReportingManager or would be testing a different report type.

        # For now, let's just assert the mocks were called as expected
        # In a real scenario, you would call a reporting_manager method and assert the output
        # Example: report_data = reporting_manager.generate_loans_with_repayments()
        # assert ... assertions on report_data ...

        # Assert that the correct HTTP requests were made
        assert m.called_with(loan_service_url)
        assert m.called_with(collection_service_url)

    # Add more tests for other report types and edge cases (e.g., empty results, errors)