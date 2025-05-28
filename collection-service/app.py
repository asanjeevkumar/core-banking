from flask import Flask, request, jsonify
import logging
import os
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from repayment_manager import RepaymentManager

# Assuming a simplified database setup for this service
# In a real microservices setup, this service would communicate with the Loan Service
# to get and update loan data, rather than having its own direct access

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine


# Database setup (replace with actual database URL)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./collection-service.db")  # Dedicated SQLite database
Base = declarative_base() # Define Base for this service
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

app = Flask(__name__)

# Dependency to the Loan Service - Placeholder communication
LOAN_SERVICE_URL = "http://localhost:5002" # Example URL for Loan Service

# Initialize database - create tables for models defined in this service
def init_db():
    # This service might not have its own models, but we keep init_db for consistency
    Base.metadata.create_all(bind=engine)

# Endpoint for processing repayments
@app.route('/loans/<int:loan_id>/repay', methods=['POST'])
def process_repayment(loan_id):
    try:
        data = request.get_json()
        payment_amount = data.get('payment_amount')

        if payment_amount is None:
            return jsonify({'error': 'Payment amount is required'}), 400
        logger.info(f"Processing repayment for loan {loan_id} with amount {payment_amount}")

        repayment_manager = RepaymentManager(db_session)
        # In a real scenario, RepaymentManager would interact with the Loan Service
        # to get loan details and update them. For now, we simulate this or
        # assume direct DB access (less ideal for microservices).
        success = repayment_manager.process_repayment(loan_id, payment_amount)

        logger.info(f"Repayment processing result for loan {loan_id}: {success}")
        return jsonify({'message': 'Repayment processed successfully'}) if success else jsonify({'error': 'Failed to process repayment'}), 400
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error processing repayment for loan {loan_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    finally:
 db_session.remove()

if __name__ == '__main__':
    init_db() # Initialize the database for this service
    app.run(debug=True, port=5003)
