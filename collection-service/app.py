from flask import Flask, request, jsonify
import logging
import os
from sqlalchemy.ext.declarative import declarative_base
from repayment_manager import RepaymentManager

# Assuming a simplified database setup for this service
# In a real microservices setup, this service would communicate with the Loan Service
# to get and update loan data, rather than having its own direct access

# Configure logging
from python_json_logger import JsonFormatter

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()

from sqlalchemy import create_engine, orm

# Database setup
def get_config_from_consul(key):
    """Simulates fetching configuration from Consul Key-Value store."""
    # In a real scenario, you would use a Consul client library here
    # For now, we return hardcoded values or environment variables
    logger.info(f"Attempting to fetch config key from Consul: {key}")
    config_values = {
 'database_url': os.environ.get('DATABASE_URL', 'sqlite:///./collection-service.db'),
 'loan_service_url': os.environ.get('LOAN_SERVICE_URL', 'http://loan-service:5002') # Default for testing/docker-compose
    }
    return config_values.get(key)

formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
DATABASE_URL = get_config_from_consul('database_url')
Base = declarative_base() # Define Base for this service - important if this service has models if any
engine = create_engine(DATABASE_URL)

app = Flask(__name__)

# Initialize database - create tables for models defined in this service
def init_db():
    # This service might not have its own models, but we keep init_db for consistency
    Base.metadata.create_all(bind=engine)

# Database session setup
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = orm.scoped_session(SessionLocal)
logger.setLevel(logging.INFO)

# Endpoint for processing repayments
@app.route('/loans/<int:loan_id>/repay', methods=['POST'])
def process_repayment(loan_id):
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
        logger.error(f"Error processing repayment for loan {loan_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db() # Initialize the database for this service
    app.run(debug=True, port=5003)
