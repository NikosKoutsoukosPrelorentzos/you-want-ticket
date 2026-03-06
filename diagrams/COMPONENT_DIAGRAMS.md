# Component Diagrams

This document illustrates the structural architecture of the "You Want Ticket" system, organized by complexity levels.

---

## Version 1: Core User & Event Architecture
This version focuses on the basic administrative and identity management layers, excluding ticketing and orders.

```plantuml
@startuml
allowmixing
title Version 1 - Core User & Event Components

package "Client" {
  component "Web/Mobile Client" as Client
}

package "FastAPI Application" {
  component "API Layer" as API {
    component "Auth Middleware" as AM
    component "Users Controller" as UC
    component "Events Controller" as EC
  }

  component "Service Layer" as Service {
    component "Auth Service" as AS
    component "User Service" as US
    component "Event Service" as ES
  }

  component "Data Access Layer" as DAL {
    component "User Repository" as UR
    component "Event Repository" as ER
  }
}

database "PostgreSQL DB" as DB

Client --> AM : "Bearer Token"
AM --> UC : "Authorize"
AM --> EC : "Authorize"

UC --> US : "Business Logic"
EC --> ES : "Business Logic"

US --> UR : "Data Access"
ES --> ER : "Data Access"
AS --> UR : "Verify Credentials"

UR --> DB
ER --> DB
@enduml
```

---

## Version 2: Integrated Ticketing System
This version introduces the purchase lifecycle, showing how the Order and Ticket components integrate with the existing services.

```plantuml
@startuml
allowmixing
title Version 2 - Integrated Purchase Architecture

package "API Layer" {
  component "Events Controller" as EC
  component "Orders Controller" as OC
}

package "Service Layer" {
  component "Order Service" as OS
  component "Event Service" as ES
  component "Ticket Service" as TS
}

package "Data Access Layer" {
  component "Order Repository" as OR
  component "Event Repository" as ER
  component "Ticket Repository" as TR
}

database "PostgreSQL DB" as DB

OC --> OS : "Process Purchase"
EC --> ES : "Event Mgmt"

' Cross-Service Dependencies
OS --> ES : "Check/Lock Inventory"
OS --> TS : "Trigger Ticket Issuance"

' DAL Mappings
OS --> OR
ES --> ER
TS --> TR
TS --> ER : "Fetch Event Details"

OR --> DB
ER --> DB
TR --> DB
@enduml
```

---

## Version 3: Full System Architecture
The complete system, including background maintenance services and external job scheduling.

```plantuml
@startuml
allowmixing
title Version 3 - Full System with Background Tasks

package "FastAPI Application" {
  component "API Layer" as API
  
  component "Service Layer" as Service {
    component "Order Service" as OS
    component "Event Service" as ES
    component "Order Cleanup Service" as OCS
  }

  component "Data Access Layer" as DAL {
    component "Order Repository" as OR
    component "Event Repository" as ER
  }
}

package "Infrastructure" {
  database "PostgreSQL DB" as DB
  component "APScheduler" as Scheduler
}

' Interactions
ES --> Scheduler : "Register Start/End Jobs"
Scheduler --> Service : "Trigger Transitions"

' Cleanup Logic
OCS --> OR : "Identify Expired"
OCS --> ER : "Restore Tickets"
Scheduler --> OCS : "Trigger Every 5 Min"

DAL --> DB
@enduml
```

### Component Breakdown
- **API Layer:** Handles request routing, parameter validation, and security (JWT).
- **Service Layer:** Orchestrates business rules. In the full system, it includes **Orchestrators** (OrderService) and **Background Services** (OrderCleanupService).
- **Data Access Layer (DAL):** Decouples the service logic from SQLAlchemy and the database schema.
- **Infrastructure:**
    - **APScheduler:** Manages the lifecycle of events and ensures unfinalized orders are cleaned up automatically.
    - **PostgreSQL:** The single source of truth for all persistent data.
