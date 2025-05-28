import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loan_service.models import Base, Borrower
from loan_service.borrower_manager import BorrowerManager

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_borrower(db_session):
    manager = BorrowerManager(db_session)
    borrower_data = {"name": "John Doe", "email": "john.doe@example.com"}
    borrower = manager.create_borrower(borrower_data)

    assert borrower is not None
    assert borrower.name == "John Doe"
    assert borrower.email == "john.doe@example.com"
    assert borrower.id is not None

    retrieved_borrower = db_session.query(Borrower).filter_by(email="john.doe@example.com").first()
    assert retrieved_borrower is not None
    assert retrieved_borrower.name == "John Doe"


def test_get_borrower(db_session):
    manager = BorrowerManager(db_session)
    borrower_data = {"name": "Jane Smith", "email": "jane.smith@example.com"}
    created_borrower = manager.create_borrower(borrower_data)

    retrieved_borrower = manager.get_borrower(created_borrower.id)

    assert retrieved_borrower is not None
    assert retrieved_borrower.id == created_borrower.id
    assert retrieved_borrower.name == "Jane Smith"
    assert retrieved_borrower.email == "jane.smith@example.com"

def test_get_borrower_not_found(db_session):
    manager = BorrowerManager(db_session)
    retrieved_borrower = manager.get_borrower(999) # Non-existent ID
    assert retrieved_borrower is None