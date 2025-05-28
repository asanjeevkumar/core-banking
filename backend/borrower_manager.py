from models import Borrower

class BorrowerManager:
    def __init__(self, session):
        self.session = session

    def create_borrower(self, name, contact_info, credit_score):
        """
        Creates a new borrower and adds them to the system.
        """
        new_borrower = Borrower(name=name, contact_info=contact_info, credit_score=credit_score)
        self.session.add(new_borrower)
        self.session.commit()
        return new_borrower

    def get_borrower(self, borrower_id):
        """
        Retrieves a borrower by their ID.
        """
        return self.session.query(Borrower).get(borrower_id)

    # You might add more functions later for updating or deleting borrowers
    # The get_all_borrowers function would also need to be updated to use the session.

    def get_all_borrowers(self):
        """
        Retrieves all borrowers in the system.
        """
        return list(self.borrowers.values())