# Collection Service

## Overview

The Collection Service is responsible for processing loan repayments. It receives repayment information and interacts with the Loan Service to update loan balances and statuses.

## Getting Started

To get the Collection Service up and running locally:

1.  Navigate to the `collection-service` directory.
2.  Ensure you have Python and `pip` installed.
3.  Install dependencies: `pip install -r requirements.txt`
4.  Set environment variables or configure the service using the `config/collection-service.yaml` file. Key configurations include the Loan Service URL.
5.  Run the Flask application: `python app.py`

Alternatively, you can use Docker Compose from the project root: `docker-compose up collection-service`

## API Documentation

The interactive API documentation (Swagger UI) is available at the `/apidocs` endpoint when the service is running.

For example, if running locally on the default port: `http://localhost:5003/apidocs`

## Database

The Collection Service interacts with the Loan Service's database via its API. It does not maintain its own primary database for loan or repayment data.

## Dependencies

The Collection Service depends on the:

*   **Loan Service:** To retrieve loan details and update loan status and balance after processing a repayment.

## Tests

To run the unit and integration tests for the Collection Service:

1.  Navigate to the `collection-service` directory.
2.  Ensure you have `pytest` and `requests_mock` installed (`pip install pytest requests_mock`).
3.  Run pytest: `pytest`