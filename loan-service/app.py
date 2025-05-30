from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import logging
import os
from sqlalchemy.exc import IntegrityError
from python_json_logger import JsonFormatter
from models import Base, Loan, Borrower
from flasgger import Swagger
from loan_manager import LoanManager
from borrower_manager import BorrowerManager
# You might need to import modules for inter-service communication (e.g., requests)
# if you need to fetch borrower details from the User Service.
import requests
import yaml # Import yaml for configuration loading (if still used)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set logging level

try:
 with open(CONFIG_PATH, 'r') as f:
 config = yaml.safe_load(f)
except FileNotFoundError:
 logger.error(f"Configuration file not found at {CONFIG_PATH}")
except yaml.YAMLError as e:
 logger.error(f"Error parsing configuration file: {e}")

def get_config_from_consul(key):
 # Configure logging with JsonFormatter
 logHandler = logging.StreamHandler()
 formatter = JsonFormatter()
 logHandler.setFormatter(formatter)
 logger.addHandler(logHandler)
 # Simulate fetching configuration from Consul's K/V store
 # In a real application, you would use a Consul client library here
 # For now, we return hardcoded values or environment variables
 if key == 'database_url':
 return os.environ.get('DATABASE_URL', 'sqlite:////app/loan-service.db')
 elif key == 'user_service_url':
 return os.environ.get('USER_SERVICE_URL', 'http://user-service:5001')
 return None

app = Flask(__name__)
swagger = Swagger(app) # Initialize Flasgger
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
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check
    This endpoint is used to check the health and readiness of the Loan Service.
    ---
    responses:
      200:
        description: Loan Service is healthy.
        schema:
          type: object
          properties:
            status:
              type: string"""
def get_all_loans():
    """
    Get all loans.
    This endpoint retrieves a list of all loans in the system.
    ---
    responses:
      200:
        description: A list of loans.
        schema:
          type: array
          items:
            $ref: '#/definitions/Loan'
      500:
        description: Internal server error.
    """
    logger.info("Loan Service: Get all loans endpoint accessed")

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
    """
    Get a loan by ID.
    This endpoint retrieves a specific loan by its ID.
    ---
    parameters:
      - name: loan_id
        in: path
        type: integer
        required: true
        description: The ID of the loan to retrieve.
    responses:
      200:
        description: The loan details.
        schema:
          $ref: '#/definitions/Loan'
      404:
        description: Loan not found.
      500:
        description: Internal server error.
    """
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
    """
    Create a new loan.
    This endpoint creates a new loan record.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            borrower_id:
              type: integer
              description: The ID of the borrower.
            amount:
              type: number
              format: float
              description: The loan amount.
            interest_rate:
              type: number
              format: float
              description: The annual interest rate.
            term:
              type: integer
              description: The loan term in months.
            start_date:
              type: string
              format: date"""
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
