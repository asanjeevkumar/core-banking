class Borrower:
    def __init__(self, name, contact_information, credit_score, loan_history=None):
        self.name = name
        self.contact_information = contact_information
        self.credit_score = credit_score
        self.loan_history = loan_history if loan_history is not None else []

    def __str__(self):
        return f"Borrower: {self.name}"

    def add_loan_to_history(self, loan):
        """Adds a loan to the borrower's history."""
        if loan not in self.loan_history:
            self.loan_history.append(loan)

    def remove_loan_from_history(self, loan):
        """Removes a loan from the borrower's history."""
        if loan in self.loan_history:
            self.loan_history.remove(loan)