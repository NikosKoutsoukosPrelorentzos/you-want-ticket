# Deployment Diagrams

This document illustrates the physical deployment architecture of the "You Want Ticket" system using PlantUML Deployment Diagrams.

## 1. Local Development Deployment
The current development environment uses a combination of a locally running FastAPI application and a containerized PostgreSQL database.

```plantuml
@startuml
title Local Development Deployment

node "Developer Machine" {
  node "Python Virtual Environment" {
    artifact "FastAPI Application" as app
    artifact "Uvicorn Server" as server
    app -- server
  }

  node "Docker Engine" {
    node "PostgreSQL Container" {
      database "PostgreSQL DB" as db
    }
  }

  server -- db : "SQLAlchemy / TCP (Port 5433:5432)"
}

cloud "External Client" {
  [Web Browser / Postman] as client
}

client -- server : "HTTP (Port 8000)"
@enduml
```

---

## 2. Typical Production Deployment (Target)
A standard production deployment would typically involve a container orchestration platform (like Kubernetes or Docker Swarm) with a load balancer.

```plantuml
@startuml
title Target Production Deployment

cloud "Internet" as internet

node "Load Balancer (e.g., Nginx / AWS ALB)" as lb

node "Application Node" as app_node {
  node "Docker Container: API" {
    artifact "FastAPI App" as api_pod
  }
}

node "Database Node (e.g., AWS RDS / Managed DB)" as db_node {
  database "PostgreSQL Instance" as prod_db
}

internet -- lb : "HTTPS (Port 443)"
lb -- api_pod : "HTTP (Port 8000)"
api_pod -- prod_db : "TCP (Port 5432)"

@enduml
```

### Deployment Details
- **Environment Management:** Python dependencies are managed within a virtual environment (`.venv`), and configuration is handled via Pydantic Settings, which reads from environment variables.
- **Containerization:** The PostgreSQL database is containerized for easy setup and consistency across development machines.
- **Networking:** In local development, the application connects to the database via `localhost:5433`. In a containerized or production environment, this would typically point to a service name (e.g., `db:5432`) or a managed database endpoint.
- **Scalability:** The stateless nature of the FastAPI application allows it to be easily scaled horizontally behind a load balancer.
