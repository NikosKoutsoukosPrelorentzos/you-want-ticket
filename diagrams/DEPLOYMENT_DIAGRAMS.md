# Deployment Diagrams

This document illustrates the physical deployment architecture of the "You Want Ticket" system, organized by complexity levels.

---

## Version 1: Core Development Deployment
This version represents the initial local setup focused on User and Event management.

```plantuml
@startuml
allowmixing
title Version 1 - Local Development (Basic)

node "Developer Machine" {
  node "Python Environment" {
    artifact "FastAPI Application" as app
    component "User/Event Services" as logic
    app -- logic
  }

  node "Docker Engine" {
    database "PostgreSQL DB" as db
  }

  app -- db : "SQLAlchemy / TCP (Port 5433:5432)"
}

cloud "External Client" {
  component "Postman / CLI" as client
}

client -- app : "HTTP (Port 8000)"
@enduml
```

---

## Version 2: Integrated Development (Docker Compose)
This version containerizes the entire stack and includes the integrated ticketing and order flows.

```plantuml
@startuml
allowmixing
title Version 2 - Containerized Local Stack

node "Docker Compose Environment" {
  node "Container: FastAPI App" {
    artifact "Uvicorn Server" as server
    component "Auth/Event/Order/Ticket Services" as services
    server -- services
  }

  node "Container: Database" {
    database "PostgreSQL DB" as db
  }

  server -- db : "Internal Network (Port 5432)"
}

cloud "External Client" {
  component "Web Browser / Mobile" as client
}

client -- server : "HTTP (Port 8000)"
@enduml
```

---

## Version 3: Full System & Production Readiness
The final architecture including background task execution (internal scheduler) and production infrastructure components.

```plantuml
@startuml
allowmixing
title Version 3 - Production Ready Architecture

cloud "Internet" as internet

node "Infrastructure Node" {
  node "Load Balancer (Nginx / ALB)" as lb
}

node "Application Node" {
  node "FastAPI Container" {
    artifact "App Code" as code
    component "Business Services" as logic
    component "APScheduler (Internal)" as scheduler
    code -- logic
    logic -- scheduler : "In-Process"
  }
}

node "Managed Database" {
  database "PostgreSQL Instance" as db
}

internet -- lb : "HTTPS (Port 443)"
lb -- code : "HTTP (Port 8000)"
logic -- db : "TCP (Port 5432)"

cloud "User Devices" {
  component "Web App / Mobile App" as client
}

client -- internet
@enduml
```

### Deployment Details
- **Environment Management:** Python dependencies are managed via `.venv`, and configuration is handled via environment variables (Pydantic Settings).
- **Process Context:** The **APScheduler** runs as a background thread within the FastAPI process (internal), ensuring it has direct access to the application context and database sessions.
- **Networking:** Development uses Port 5433 (mapping to 5432), while production uses standard internal networking or managed service endpoints.
- **Security:** Production environments enforce HTTPS at the Load Balancer level before traffic enters the Application Node.
