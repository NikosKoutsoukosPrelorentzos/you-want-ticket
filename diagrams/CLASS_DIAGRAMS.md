# Class Diagrams

This document illustrates the internal structure and static relationships of the "You Want Ticket" system using PlantUML Class Diagrams.

## 1. Domain Models and Relationships
The following diagram shows the core SQLAlchemy models, their attributes, and how they relate to each other through foreign keys.

```plantuml
@startuml
title You Want Ticket - Domain Model Class Diagram
skinparam classAttributeIconSize 0

class Base {
}

class User {
    +id: Integer
    +uuid: UUID
    +email: String
    +hashed_password: String
    +is_active: Boolean
}

class Event {
    +id: Integer
    +uuid: UUID
    +type: EventType
    +title: String
    +description: String
    +owner_uuid: UUID
    +created_date: DateTime
    +updated_date: DateTime
    +start_date: DateTime
    +end_date: DateTime
    +status: EventStatus
    +location: String
    +available_number_of_tickets: Integer
}

class Order {
    +id: Integer
    +uuid: UUID
    +owner_uuid: UUID
    +created_date: DateTime
    +updated_date: DateTime
    +status: OrderStatus
    +event_uuid: UUID
    +number_of_tickets: Integer
}

class Ticket {
    +id: Integer
    +uuid: UUID
    +created_date: DateTime
    +updated_date: DateTime
    +status: TicketStatus
    +event_uuid: UUID
    +order_uuid: UUID
    +owner_uuid: UUID
}

enum EventStatus {
    SCHEDULED
    ACTIVE
    CANCELLED
    FINISHED
}

enum OrderStatus {
    IN_PROGRESS
    FINALIZED
    CANCELLED
    EXPIRED
}

enum TicketStatus {
    SCHEDULED
    ACTIVE
    COMPLETED
    EXPIRED
    CANCELLED
}

Base <|-- User
Base <|-- Event
Base <|-- Order
Base <|-- Ticket

User "1" -- "*" Event : "organizes"
User "1" -- "*" Order : "places"
User "1" -- "*" Ticket : "owns"
Event "1" -- "*" Order : "receives"
Event "1" -- "*" Ticket : "issues"
Order "1" -- "*" Ticket : "contains"

Event -- EventStatus
Order -- OrderStatus
Ticket -- TicketStatus

@enduml
```

---

## 2. Service Layer and Dependency Injection
This diagram illustrates the architectural pattern used for business logic, showing how Services depend on Repositories and other Services.

```plantuml
@startuml
title You Want Ticket - Service Layer Architecture

class OrderService {
    -order_repository: OrderRepository
    -event_service: EventService
    -ticket_service: TicketService
    +create_order(dto, user_uuid)
    +finalize_order_by_user(uuid, user_uuid)
    +cancel_order_by_user(uuid, user_uuid)
}

class EventService {
    -event_repository: EventRepository
    -scheduler: BaseScheduler
    +create_event(dto, user_uuid)
    +get_all_events(filters)
    +cancel_event(uuid, user_uuid)
}

class TicketService {
    -ticket_repository: TicketRepository
    -event_repository: EventRepository
    +create_tickets(list[dto])
    +cancel_ticket(uuid, user_uuid)
}

class OrderRepository {
    -db: Session
    +create_order()
    +finalize_order_by_user()
}

class EventRepository {
    -db: Session
    +create_event()
    +remove_available_tickets()
}

class TicketRepository {
    -db: Session
    +create_ticket()
    +cancel_ticket()
}

OrderService --> EventService : "Depends on"
OrderService --> TicketService : "Depends on"
OrderService --> OrderRepository : "Uses"
EventService --> EventRepository : "Uses"
TicketService --> TicketRepository : "Uses"
TicketService --> EventRepository : "Uses"

@enduml
```

### Key Structural Patterns
- **Inheritance:** All models inherit from the `Base` class (Declarative Base), providing SQLAlchemy ORM capabilities.
- **Composition:** Services are composed of their respective repositories and other services they need to interact with.
- **Enumerations:** Distinct enums (`EventStatus`, `OrderStatus`, `TicketStatus`) are used to strictly define the state transitions of the domain objects.
- **Decoupling:** The Repository classes encapsulate the database access logic (SQLAlchemy sessions), keeping the Service layer focused on business rules.
