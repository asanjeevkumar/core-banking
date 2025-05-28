from models import Loan  # Import the Loan model from models.py
from sqlalchemy.orm import Session # Import Session for type hinting

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
        loan = db.query(Loan).filter(Loan.id == loan_id).first()

        if not loan:
            print(f"Error: Loan with ID {loan_id} not found.")
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
        print(f"Interest portion: {min(payment_amount, interest_due):.2f}")
        print(f"Principal portion: {principal_paid:.2f}")
        print(f"Remaining balance: {loan.outstanding_balance:.2f}")

        if loan.outstanding_balance <= 0:
            loan.outstanding_balance = 0
            loan.status = "paid off"
            print(f"Loan {loan_id} fully paid off.") # This line should probably be inside the commit block or handled by the caller

        db.commit() # Commit the changes to the database
        db.refresh(loan) # Refresh the loan object to get the latest data from the database
        return True

if __name__ == '__main__':
    # Example Usage (assuming you have a way to create and get loans)
    # Database session management would be handled in the application's entry point (e.g., app.py)
    pass
    pass