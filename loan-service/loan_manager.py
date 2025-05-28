# loan_manager.py

from datetime import date
from sqlalchemy.orm import Session
from .models import Loan, Borrower
import requests # Import the requests library

# In a real application, this would interact with a database
class LoanManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.borrower_manager = BorrowerManager(db_session) # Instantiate the BorrowerManager with the session

    def create_loan(self, borrower_data: dict, amount: float, interest_rate: float, term: int, start_date: date):
        """Creates a new loan and adds it to the system."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Loan amount must be a positive number.")
        if not isinstance(interest_rate, (int, float)) or interest_rate < 0:
            raise ValueError("Interest rate must be a non-negative number.")
        if not isinstance(start_date, date):
            raise ValueError("Start date must be a valid date object.")

        # --- Inter-Service Communication: Interact with User Service to get or create borrower ---
        user_service_url = 'http://localhost:5001' # Replace with actual User Service URL
        borrower_id = borrower_data.get('id') # Assuming borrower_data might contain an existing ID

        borrower = None
        if borrower_id:
            try:
                response = requests.get(f'{user_service_url}/users/{borrower_id}')
                response.raise_for_status() # Raise an exception for bad status codes
                borrower_data_from_service = response.json()
                # You would likely need to create a Borrower object from this data if not using a shared model
                # For simplicity, we'll assume the response structure matches our needs or we get enough info
            except requests.exceptions.RequestException as e:
            borrower = self.borrower_manager.create_borrower(borrower_data.get('name'), borrower_data.get('contact_info'), borrower_data.get('credit_score'))

        new_loan = Loan(amount=amount, interest_rate=interest_rate, term=term, start_date=start_date, status="active", borrower=borrower)

        self.db_session.add(new_loan)
        self.db_session.commit()
        return new_loan

    def get_loan(self, loan_id: int):
        """Retrieves a specific loan by its ID."""
        return self.db_session.query(Loan).filter_by(id=loan_id).first()

    def update_loan(self, loan_id: int, updated_data: dict):
        """Updates the attributes of an existing loan."""
        loan = self.get_loan(loan_id)
        if loan:
            for key, value in updated_data.items():
                setattr(loan, key, value)
            self.db_session.commit()
            return loan
        return None

    def get_all_loans(self):
        """Retrieves a list of all loans in the system."""
        return self.db_session.query(Loan).all()