import requests

# Replace with the actual URLs of your services
LOAN_SERVICE_URL = 'http://loan-service:5002'
# COLLECTION_SERVICE_URL = 'http://collection-service:5003' # Uncomment if needed for reports

class ReportingManager:
    def __init__(self):
        pass

    def get_active_loans(self):
        """
        Retrieves a list of all active loans.
        """
        try:
            response = requests.get(f'{LOAN_SERVICE_URL}/loans')
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            all_loans = response.json()
            return [loan for loan in all_loans if loan.get('status') == 'active']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching loans from Loan Service: {e}")
            return [] # Return empty list or raise an exception

    def get_paid_off_loans(self):
        """
        Retrieves a list of all paid-off loans.
        """
        try:
            response = requests.get(f'{LOAN_SERVICE_URL}/loans')
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            all_loans = response.json()
            return [loan for loan in all_loans if loan.get('status') == 'paid-off']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching loans from Loan Service: {e}")
            return [] # Return empty list or raise an exception

    # Add more reporting functions as needed
    # def get_delinquent_loans(self):
    #     """
    #     Retrieves a list of all delinquent loans.
    #     (Requires implementing due dates and tracking payments)
    #     """
    #     pass

    # def get_loan_book_summary(self):
    #     """
    #     Generates a summary of the loan book (e.g., total outstanding balance).
    #     """
    #     pass