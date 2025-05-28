from models import Loan  # Import the Loan model from models.py
from sqlalchemy.orm import Session # Import Session for type hinting

import requests

class RepaymentManager:
    def process_repayment(self, db: Session, loan_id: int, payment_amount: float):
        """
        Processes a repayment for a given loan.

        Args:
            db: The SQLAlchemy database session.
            loan_id: The ID of the loan.
            payment_amount: The amount of the repayment.

        Returns:
            True if the repayment was processed successfully, False otherwise.
        """
        # Communicate with the Loan Service to get loan details
        loan_service_url = 'http://loan-service:5002' # Replace with the actual Loan Service URL
        try:
            response = requests.get(f"{loan_service_url}/loans/{loan_id}")
            response.raise_for_status() # Raise an exception for bad status codes
            loan_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Loan Service: {e}")
            return False

        # Create a Loan object from the received data for calculations
        # This assumes the Loan model has a constructor that can handle this data
        # In a real scenario, you might use a DTO (Data Transfer Object)
        loan = Loan(**loan_data)
            return False

        if payment_amount <= 0:
            print("Error: Payment amount must be positive.")
            return False

        # For simplicity, we'll assume a simple interest calculation for the current period
        # In a real system, this would be more complex based on the loan type and schedule
        interest_due = loan.outstanding_balance * (loan.interest_rate / 12) # Assuming monthly interest

        principal_paid = max(0, payment_amount - interest_due)

        if principal_paid > loan.outstanding_balance:
            principal_paid = loan.outstanding_balance

        loan.outstanding_balance -= principal_paid

        print(f"Processed repayment of {payment_amount} for loan {loan_id}.")
        # print(f"Interest portion: {min(payment_amount, interest_due):.2f}") # These prints might be better in the service endpoint
        # print(f"Principal portion: {principal_paid:.2f}")
        # print(f"Remaining balance: {loan.outstanding_balance:.2f}")

        updated_loan_data = {
            "outstanding_balance": loan.outstanding_balance,
            "status": loan.status # Need to update status based on outstanding_balance
        }
        if loan.outstanding_balance <= 0:
            updated_loan_data["outstanding_balance"] = 0
            updated_loan_data["status"] = "paid off"
            # print(f"Loan {loan_id} fully paid off.") # This print might be better in the service endpoint

        # Communicate with the Loan Service to update loan details
        try:
            response = requests.put(f"{loan_service_url}/loans/{loan_id}", json=updated_loan_data)
            response.raise_for_status() # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Loan Service to update loan: {e}")
            return False
        return True

if __name__ == '__main__':
    # Example Usage (assuming you have a way to create and get loans)
    # Database session management would be handled in the application's entry point (e.g., app.py)
    pass
    pass