from flask import Flask
import os
from reporting_manager import ReportingManager
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Database setup
engine = create_engine(os.environ.get('DATABASE_URL', 'sqlite:///reporting-service.db'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    logger.info("Reporting Service index endpoint accessed.")
    return 'Reporting Service'


if __name__ == '__main__':
    app.run(debug=True, port=5004, host='0.0.0.0')
