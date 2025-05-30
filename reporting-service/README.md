# Reporting Service

## Overview

The Reporting Service is responsible for generating various reports related to loans and repayments. It interacts with the Loan Service and the Collection Service to gather the necessary data for reporting.

## Getting Started

To get the Reporting Service up and running locally:

1.  **Navigate** to the `reporting-service` directory:
```
bash
    cd reporting-service
    
```
2.  **Install dependencies**:
```
bash
    pip install -r requirements.txt
    
```
(Make sure you have Python and pip installed).
3.  **Configure the service**: The service reads its configuration from `../config/reporting-service.yaml`. Ensure this file exists and is configured correctly, or set the necessary environment variables (e.g., for database connection and URLs of dependent services).
4.  **Run the application**:
```
bash
    python app.py
    
```
The service should start and be accessible at `http://localhost:5004`.

## API Documentation

The Reporting Service provides an API for generating reports. You can find the interactive API documentation (Swagger UI) at:
```
http://localhost:5004/apidocs
```
Explore this endpoint in your browser when the service is running to see the available endpoints, their parameters, and response formats.

## Database

The Reporting Service currently uses an SQLite database for potential caching or reporting-specific data, as configured in `../config/reporting-service.yaml` (or environment variables).

## Dependencies

The Reporting Service depends on the following services:

*   **Loan Service**: To fetch loan details.
*   **Collection Service**: To fetch repayment information.

Ensure these services are running and accessible at the configured URLs for the Reporting Service to function correctly.

## Tests

To run the unit and integration tests for the Reporting Service:

1.  **Navigate** to the `reporting-service` directory.
2.  **Run pytest**: