## Microservices Architecture Example

This repository contains an example of a microservices architecture built with Python (Flask), SQLAlchemy, and orchestrated with Docker Compose and Kubernetes.

### Services

The application is composed of the following microservices:

- **User Service:** Manages user registration, authentication, and profile information.
- **Loan Service:** Handles loan creation, retrieval, and management.
- **Collection Service:** Processes loan repayments.
- **Reporting Service:** Generates reports based on data from other services.
- **API Gateway:** Acts as a single entry point for external clients, routing requests to the appropriate microservices.

### Prerequisites

To run and deploy this application, you will need the following tools installed:

- [**Docker**](https://www.docker.com/get-started)
- [**Docker Compose**](https://docs.docker.com/compose/install/)
- [**kubectl**](https://kubernetes.io/docs/tasks/tools/install-kubectl/) (for Kubernetes deployment)
- A **Kubernetes Cluster** (e.g., Minikube, Docker Desktop Kubernetes, a cloud provider's managed Kubernetes service)

### Local Deployment

You can run all the microservices locally using Docker Compose. This is useful for development and testing.

1.  Navigate to the root directory of the project.
2.  Build and start the services:


