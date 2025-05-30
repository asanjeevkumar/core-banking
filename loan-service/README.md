# Loan Service

## Overview

The Loan Service is responsible for managing loan information and borrower details. It provides APIs for creating, retrieving, and managing loans and the individuals or entities who take them out.

## Getting Started

To run the Loan Service locally, follow these steps:

1.  Navigate to the `loan-service` directory.
2.  Install the required dependencies:
```
bash
    pip install -r requirements.txt
    
```
3.  Ensure your configuration is set up. The service reads configuration from `../config/loan-service.yaml` by default. You can also use environment variables.
4.  Run the Flask application:
```
bash
    flask run --port 5002
    
```
The service will be available at `http://localhost:5002`.

## API Documentation

The interactive API documentation (Swagger UI) is available at the `/apidocs` endpoint when the service is running.

Access it at: `http://localhost:5002/apidocs`

This documentation provides details on the available endpoints, request formats, and responses.

## Database

The Loan Service uses a SQLite database (`loan-service.db`) by default for local development. In production, a more robust database solution is recommended.

## Dependencies

The Loan Service depends on the following service:

*   **User Service:** Used for potentially retrieving user information related to borrowers.

Ensure the User Service is running and accessible based on the `user_service_url` configured for the Loan Service.

## Tests

To run the unit and integration tests for the Loan Service:

1.  Navigate to the `loan-service` directory.
2.  Execute pytest:
```
bash
    pytest
    
```
The tests cover the `LoanManager`, `BorrowerManager`, and the service's API endpoints.