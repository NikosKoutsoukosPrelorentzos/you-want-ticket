# Component Diagrams

This document illustrates the structural architecture of the "You Want Ticket" system using PlantUML Component Diagrams.

## 1. High-Level System Components
The system is divided into three primary layers: the **API Layer** (FastAPI), the **Service Layer** (Business Logic), and the **Infrastructure Layer** (Data Access and External Services).

```plantuml
@startuml
title You Want Ticket - System Components

package "Client Application" {
  [Web/Mobile Client] as Client
}

package "FastAPI Application" {
  component "API Layer" as API {
    [Auth Middleware]
    [Events Controller]
    [Orders Controller]
    [Users Controller]
  }

  component "Service Layer" as Service {
    [Auth Service]
    [Event Service]
    [Order Service]
    [Ticket Service]
    [Order Cleanup Service]
  }

  component "Data Access Layer" as DAL {
    [Event Repository]
    [Order Repository]
    [Ticket Repository]
    [User Repository]
  }
}

package "External Infrastructure" {
  database "PostgreSQL DB" as DB
  component "APScheduler" as Scheduler
}

Client --> API : HTTP/REST
API --> Service : Dependency Injection
Service --> DAL : Dependency Injection
Service --> Scheduler : Job Registration
DAL --> DB : SQLAlchemy (Engine/Session)
@enduml
```

---

## 2. Service-Level Dependencies
This diagram shows how individual services collaborate to fulfill complex business processes, such as order finalization.

```plantuml
@startuml
title Service-Level Dependencies

package "Services" {
  [Order Service] as OS
  [Event Service] as ES
  [Ticket Service] as TS
  [Auth Service] as AS
}

package "Repositories" {
  [Order Repository] as OR
  [Event Repository] as ER
  [Ticket Repository] as TR
  [User Repository] as UR
}

OS ..> ES : "Validates Availability"
OS ..> TS : "Generates Tickets"
OS ..> OR : "Data Access"

ES ..> ER : "Data Access"
TS ..> TR : "Data Access"
TS ..> ER : "Fetches Event Info"
AS ..> UR : "Verifies Credentials"

@enduml
```

### Component Breakdown
- **API Layer:** Handles request routing, parameter validation (via Pydantic), and HTTP response formatting. It is the entry point for all external traffic.
- **Service Layer:** The core of the application. It orchestrates business processes and ensures that complex operations (like decrementing inventory and creating an order) are executed within a consistent transaction.
- **Data Access Layer (DAL):** Encapsulates SQLAlchemy logic, keeping the service layer decoupled from the specific ORM implementation and SQL queries.
- **Infrastructure:**
    - **APScheduler:** An in-process scheduler used for time-sensitive tasks like automatically starting/ending events or cleaning up expired orders.
    - **PostgreSQL:** The persistent data store for all entities (Events, Users, Orders, Tickets).
