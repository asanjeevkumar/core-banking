# backend/reporting_manager.py

from .loan_manager import LoanManager  # Assuming LoanManager class is in loan_manager.py
from .loan import Loan  # Assuming Loan class is in loan.py

class ReportingManager:
    def __init__(self):
        self.loan_manager = LoanManager()

    def get_active_loans(self):
        """
        Retrieves a list of all active loans.
        """
        return [loan for loan in self.loan_manager.get_all_loans() if loan.status == 'active']

    def get_paid_off_loans(self):
        """
        Retrieves a list of all paid-off loans.
        """

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