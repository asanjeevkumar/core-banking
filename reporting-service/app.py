from flask import Flask
from reporting_manager import ReportingManager
import logging
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


if __name__ == '__main__':
    app.run(debug=True, port=5004, host='0.0.0.0')
