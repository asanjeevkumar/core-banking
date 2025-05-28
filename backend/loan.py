class Loan:
    def __init__(self, loan_amount, interest_rate, term, start_date, borrower_info, status="active"):
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.term = term  # in months
        self.start_date = start_date
        self.status = status
        self.borrower_info = borrower_info # This could be a reference to a Borrower object
        self.outstanding_balance = loan_amount

    def __str__(self):
        return f"Loan Amount: {self.loan_amount}, Interest Rate: {self.interest_rate}, Term: {self.term} months, Status: {self.status}"

    # You will add methods here for things like calculating payments, processing payments, etc.
    pass