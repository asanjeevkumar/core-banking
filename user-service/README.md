# User Service

## Service Overview

The User Service is responsible for managing user accounts, including registration, authentication, and authorization. It provides APIs for creating, retrieving, updating, and deleting user information, as well as endpoints for user login and token management.

## API Endpoints

For detailed API documentation, including endpoints, parameters, request/response formats, and examples, please refer to the generated OpenAPI documentation available at the `/apidocs` endpoint when the service is running.

Common endpoints include:

*   `POST /users`: Register a new user.
*   `GET /users/{user_id}`: Retrieve user details by ID.
*   `GET /users/username/{username}`: Retrieve user details by username.
*   `PUT /users/{user_id}`: Update user details.
*   `DELETE /users/{user_id}`: Delete a user.
*   `POST /login`: User login and token generation.
*   `POST /refresh`: Refresh access token using refresh token.
*   `GET /health`: Health check endpoint.

## Dependencies

The User Service primarily serves as a dependency for other services (like the Loan Service for borrower association) but does not have significant external service dependencies itself within this architecture.

## Configuration

The User Service is configured using a combination of environment variables, Kubernetes ConfigMaps, and Secrets when deployed to a Kubernetes cluster.

*   **Kubernetes:** Non-sensitive configuration like external service URLs (if any) are managed via ConfigMaps (`kubernetes/configmaps.yaml`), and sensitive information like database credentials and JWT secrets are managed via Secrets (`kubernetes/secrets.yaml`).
*   **Local:** For local development, configuration can be read from `config/user-service.yaml` (though we simulated fetching from a config service in the code).

Key configuration parameters include:

*   `DATABASE_URL`: Connection string for the database.
*   `JWT_SECRET_KEY`: Secret key for signing JWT access tokens.
*   `REFRESH_TOKEN_SECRET_KEY`: Secret key for signing JWT refresh tokens.
*   `ACCESS_TOKEN_EXPIRY`: Expiry time for access tokens.
*   `REFRESH_TOKEN_EXPIRY`: Expiry time for refresh tokens.

## Running Locally

You can run the entire microservices stack locally using Docker Compose from the project root:

# User Service

## Service Overview

The User Service is responsible for managing user accounts, including registration, authentication, and authorization. It provides APIs for creating, retrieving, updating, and deleting user information, as well as endpoints for user login and token management.

## API Endpoints

For detailed API documentation, including endpoints, parameters, request/response formats, and examples, please refer to the generated OpenAPI documentation available at the `/apidocs` endpoint when the service is running.

Common endpoints include:

*   `POST /users`: Register a new user.
*   `GET /users/{user_id}`: Retrieve user details by ID.
*   `GET /users/username/{username}`: Retrieve user details by username.
*   `PUT /users/{user_id}`: Update user details.
*   `DELETE /users/{user_id}`: Delete a user.
*   `POST /login`: User login and token generation.
*   `POST /refresh`: Refresh access token using refresh token.
*   `GET /health`: Health check endpoint.

## Dependencies

The User Service primarily serves as a dependency for other services (like the Loan Service for borrower association) but does not have significant external service dependencies itself within this architecture.

## Configuration

The User Service is configured using a combination of environment variables, Kubernetes ConfigMaps, and Secrets when deployed to a Kubernetes cluster.

*   **Kubernetes:** Non-sensitive configuration like external service URLs (if any) are managed via ConfigMaps (`kubernetes/configmaps.yaml`), and sensitive information like database credentials and JWT secrets are managed via Secrets (`kubernetes/secrets.yaml`).
*   **Local:** For local development, configuration can be read from `config/user-service.yaml` (though we simulated fetching from a config service in the code).

Key configuration parameters include:

*   `DATABASE_URL`: Connection string for the database.
*   `JWT_SECRET_KEY`: Secret key for signing JWT access tokens.
*   `REFRESH_TOKEN_SECRET_KEY`: Secret key for signing JWT refresh tokens.
*   `ACCESS_TOKEN_EXPIRY`: Expiry time for access tokens.
*   `REFRESH_TOKEN_EXPIRY`: Expiry time for refresh tokens.

## Running Locally

You can run the entire microservices stack locally using Docker Compose from the project root:
```
bash
docker-compose up --build user-service
```
Alternatively, you can build and run the User Service Docker image individually:
```
bash
docker build -t user-service ./user-service
docker run -p 5001:5001 user-service
```
Ensure the required environment variables or configuration files are set up when running individually.

## Testing

Unit tests for the User Service are located in `tests/test_user_manager.py`. Integration tests for the User Service API are in `tests/test_user_api.py`.

To run the tests:
```
bash
cd user-service
pytest
```
## Deployment

The User Service is deployed to Kubernetes using the manifest file located at `kubernetes/user-service.yaml`. This file defines the Deployment and Service for the User Service.

Configuration in Kubernetes is managed via ConfigMaps (`kubernetes/configmaps.yaml`) and Secrets (`kubernetes/secrets.yaml`). External access is configured via the Ingress (`kubernetes/ingress.yaml`).

## Key Files

*   `app.py`: Flask application entry point, API endpoints, and logging setup.
*   `user_manager.py`: Handles user-related business logic and database interactions.
*   `models.py`: SQLAlchemy models for user data.
*   `requirements.txt`: Python dependencies for the service.
*   `Dockerfile`: Defines the Docker image for the service.
*   `tests/test_user_manager.py`: Unit tests for `UserManager`.
*   `tests/test_user_api.py`: Integration tests for the User Service API.