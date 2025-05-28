import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loan_service.models import Base, Loan, Borrower
from loan_service.loan_manager import LoanManager
from datetime import datetime

@pytest.fixture(scope='function')
def db_session():
    """Creates a new database session for each test."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_loan(db_session):
    manager = LoanManager(db_session)
    loan_data = {
        'borrower_id': 1,
        'amount': 1000.0,
        'term': 12,
        'interest_rate': 5.0
    }
    loan = manager.create_loan(loan_data)

    assert loan is not None
    assert loan.borrower_id == 1
    assert loan.amount == 1000.0
    assert loan.status == 'pending'
    assert loan.created_at is not None

def test_get_loan(db_session):
    manager = LoanManager(db_session)
    loan_data = {
        'borrower_id': 1,
        'amount': 1000.0,
        'term': 12,
        'interest_rate': 5.0
    }
    created_loan = manager.create_loan(loan_data)

    retrieved_loan = manager.get_loan(created_loan.id)
    assert retrieved_loan is not None
    assert retrieved_loan.id == created_loan.id
    assert retrieved_loan.borrower_id == 1

    non_existent_loan = manager.get_loan(999)
    assert non_existent_loan is None

def test_get_all_loans(db_session):
    manager = LoanManager(db_session)
    loan_data1 = {
        'borrower_id': 1,
        'amount': 1000.0,
        'term': 12,
        'interest_rate': 5.0
    }
    loan_data2 = {
        'borrower_id': 2,
        'amount': 2000.0,
        'term': 24,
        'interest_rate': 6.0
    }
    manager.create_loan(loan_data1)
    manager.create_loan(loan_data2)

    all_loans = manager.get_all_loans()
    assert len(all_loans) == 2
    assert any(loan.amount == 1000.0 for loan in all_loans)
    assert any(loan.amount == 2000.0 for loan in all_loans)

def test_update_loan_status(db_session):
    manager = LoanManager(db_session)
    loan_data = {
        'borrower_id': 1,
        'amount': 1000.0,
        'term': 12,
        'interest_rate': 5.0
    }
    loan = manager.create_loan(loan_data)

    updated_loan = manager.update_loan(loan.id, {'status': 'approved'})
    assert updated_loan is not None
    assert updated_loan.id == loan.id
    assert updated_loan.status == 'approved'

    non_existent_loan = manager.update_loan(999, {'status': 'rejected'})
    assert non_existent_loan is None

def test_update_loan_partial(db_session):
    manager = LoanManager(db_session)
    loan_data = {
        'borrower_id': 1,
        'amount': 1000.0,
        'term': 12,
        'interest_rate': 5.0
    }
    loan = manager.create_loan(loan_data)

    updated_loan = manager.update_loan(loan.id, {'term': 18})
    assert updated_loan is not None
    assert updated_loan.id == loan.id
    assert updated_loan.term == 18
    assert updated_loan.amount == 1000.0 # Ensure other fields are unchanged

    non_existent_loan = manager.update_loan(999, {'term': 36})
    assert non_existent_loan is None