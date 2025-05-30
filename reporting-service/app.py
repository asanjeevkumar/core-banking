from flask import Flask, jsonify
from reporting_manager import ReportingManager, LoanServiceError, CollectionServiceError
import logging
from flasgger import Swagger
import os

from python_json_logger import JsonFormatter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

def get_config_from_consul(key):
    """
    Simulates fetching configuration from a conceptual Consul Key-Value store.
    In a real microservice, you would use a Consul client library here.
    """
    # For demonstration, return hardcoded values or environment variables
    config_values = {
        'database_url': os.environ.get('DATABASE_URL', 'sqlite:///reporting-service.db'),
        'loan_service_url': os.environ.get('LOAN_SERVICE_URL', 'http://loan-service:5002'), # Placeholder
        'collection_service_url': os.environ.get('COLLECTION_SERVICE_URL', 'http://collection-service:5003') # Placeholder
    }
    return config_values.get(key)

Base = declarative_base()

# Database setup
engine = create_engine(get_config_from_consul('database_url'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Use a default session if no db needed
db_session = scoped_session(SessionLocal)

app = Flask(__name__)
Swagger(app) # Initialize Swagger

# Configure logging
formatter = JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d')
logHandler = logging.StreamHandler()
logHandler.setFormatter(formatter)

# Configure logging
logger = logging.getLogger(__name__)

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.
    # from . import models # Uncomment if you have models in this service
    Base.metadata.create_all(bind=engine)
    print("Reporting Service database initialized.")

init_db()

@app.route('/')
def index():
    logger.addHandler(logHandler)
    logger.info("Reporting Service index endpoint accessed.")
    return 'Reporting Service'


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the Reporting Service.
    ---
    responses:
      200:
        description: Service is healthy.
        schema:
          type: object
          properties:
            status:
              type: string
      500:
        description: Service is unhealthy.
    """
    try:
        # Add more comprehensive health checks here, e.g., database connection,
        # attempt basic calls to Loan and Collection services.
        # ReportingManager.check_dependencies() # Example of calling a manager method for dependency checks
        return jsonify({"status": "UP"}), 200
    except (LoanServiceError, CollectionServiceError, Exception) as e:
        logger.addHandler(logHandler)
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "DOWN", "error": str(e)}), 500

@app.route('/reports/active-loans', methods=['GET'])
def get_active_loans_report():
    """
    Get a report of active loans.
    ---
    responses:
      200:
        description: A list of active loans.
    """
    return ReportingManager.get_active_loans_report()


if __name__ == '__main__':
    app.run(debug=True, port=5004, host='0.0.0.0')
