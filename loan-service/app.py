from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
import os
from sqlalchemy.exc import IntegrityError
from models import Base, Loan, Borrower
from loan_manager import LoanManager
from borrower_manager import BorrowerManager
# You might need to import modules for inter-service communication (e.g., requests)
# if you need to fetch borrower details from the User Service.import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



DATABASE_URL = 'sqlite:///./loan_service.db'
DATABASE_URL = os.environ.get('DATABASE_URL', DATABASE_URL)
app = Flask(__name__)

engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

@app.teardown_request
def remove_session(exception=None):
    db_session.remove()

def init_db():
    # import all modules here that define models so that
    from models import Base
    Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    logger.info("Loan Service root endpoint accessed")
    return 'Loan Service Running'

@app.route('/loans', methods=['GET'])
def get_all_loans():
    loan_manager = LoanManager(db_session)
    loans = loan_manager.get_all_loans()
    # Convert Loan objects to dictionaries for JSON serialization
    loans_data = [{

        'id': loan.id,
        'amount': loan.amount,
        'interest_rate': loan.interest_rate,
        'term': loan.term,
        'start_date': loan.start_date.isoformat() if loan.start_date else None,
        'status': loan.status,
        'borrower_id': loan.borrower_id
    } for loan in loans]
    return jsonify(loans_data), 200


@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    loan_manager = LoanManager(db_session)
    loan = loan_manager.get_loan(loan_id)
    if loan:
        loan_data = {
            'id': loan.id,
            'amount': loan.amount,
            'interest_rate': loan.interest_rate,
            'term': loan.term,
            'start_date': loan.start_date.isoformat() if loan.start_date else None,
            'status': loan.status,
            'borrower_id': loan.borrower_id
        }
        return jsonify(loan_data), 200
    return jsonify({'message': 'Loan not found'}), 404


@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid input'}), 400

    # In a real microservices scenario, you would likely validate borrower_id
    # by calling the User Service.
    borrower_id = data.get('borrower_id')

    if not borrower_id:
         return jsonify({'message': 'borrower_id is required'}), 400

    loan_manager = LoanManager(db_session)
    try:
        # You might need to fetch borrower details from User Service here
        # to ensure the borrower exists before creating the loan.
        # For now, we assume the borrower_id is valid.
        loan = loan_manager.create_loan(
            borrower_id=borrower_id,
            amount=data.get('amount'),
            interest_rate=data.get('interest_rate'),
            term=data.get('term'),
            start_date=data.get('start_date') # Expecting ISO format string
        )
        return jsonify({'message': 'Loan created successfully', 'loan_id': loan.id}), 201
    except ValueError as e:
        logger.error(f"Error creating loan: {e}", exc_info=True)
         return jsonify({'message': str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        logger.error("Integrity error creating loan", exc_info=True)
        return jsonify({'message': 'Error creating loan'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)
