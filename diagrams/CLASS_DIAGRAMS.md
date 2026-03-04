# Class Diagrams

This document illustrates the internal structure and static relationships of the "You Want Ticket" system, organized by complexity levels.

---

## Version 1: Core User & Event Structure
This version focuses on user authentication and event management, excluding orders and tickets.

### 1.1 Domain Models & DTOs
```plantuml
@startuml
title Version 1 - User & Event Domain
skinparam classAttributeIconSize 0

class User {
    +uuid: UUID
    +email: String
    +hashed_password: String
    +is_active: Boolean
}

class Event {
    +uuid: UUID
    +type: EventType
    +title: String
    +owner_uuid: UUID
    +status: EventStatus
    +available_number_of_tickets: Integer
}

class UserDTO {
    +uuid: UUID
    +email: String
}

class EventDTO {
    +uuid: UUID
    +title: String
    +status: EventStatus
}

User "1" -- "*" Event : "organizes"
@enduml
```

### 1.2 Service Layer Architecture
```plantuml
@startuml
title Version 1 - Auth & Event Services

class AuthService {
    -user_repository: UserRepository
    +login(email, password)
    +get_current_user(token)
}

class UserService {
    -user_repository: UserRepository
    +create_user(dto)
    +get_user_by_email(email)
}

class EventService {
    -event_repository: EventRepository
    +create_event(dto, user_uuid)
    +get_all_events(filters)
}

AuthService --> UserRepository : "Uses"
UserService --> UserRepository : "Uses"
EventService --> EventRepository : "Uses"
@enduml
```

---

## Version 2: Integrated Ticketing System
This version adds the Order and Ticket domains and shows how the services interact to process purchases.

### 2.1 Complete Domain Model
```plantuml
@startuml
title Version 2 - Integrated Domain Model
skinparam classAttributeIconSize 0

class User {
    +uuid: UUID
}

class Event {
    +uuid: UUID
    +available_number_of_tickets: Integer
}

class Order {
    +uuid: UUID
    +owner_uuid: UUID
    +event_uuid: UUID
    +status: OrderStatus
    +number_of_tickets: Integer
}

class Ticket {
    +uuid: UUID
    +order_uuid: UUID
    +status: TicketStatus
}

User "1" -- "*" Order : "places"
Event "1" -- "*" Order : "receives"
Order "1" -- "*" Ticket : "contains"
@enduml
```

### 2.2 Integrated Service Layer
```plantuml
@startuml
title Version 2 - Purchase Logic Interaction

class OrderService {
    -order_repository: OrderRepository
    -event_service: EventService
    -ticket_service: TicketService
    +create_order(dto, user_uuid)
    +finalize_order(uuid, user_uuid)
}

class EventService {
    +remove_tickets(uuid, count)
}

class TicketService {
    +create_tickets(order_uuid, count)
}

OrderService --> EventService : "Checks/Updates Inventory"
OrderService --> TicketService : "Triggers Generation"
OrderService --> OrderRepository : "Persists State"
@enduml
```

---

## Version 3: Full System & Background Tasks
The complete architecture including maintenance services and advanced state management.

### 3.1 Advanced Service Architecture
```plantuml
@startuml
title Version 3 - Full System Architecture

package "Business Logic" {
    class OrderService
    class EventService
    class TicketService
    class AuthService
}

package "Background Tasks" {
    class OrderCleanupService {
        -order_repository: OrderRepository
        -event_repository: EventRepository
        +cleanup_expired_orders()
    }
}

package "Data Access" {
    class OrderRepository
    class EventRepository
    class TicketRepository
}

OrderCleanupService --> OrderRepository : "Queries/Updates"
OrderCleanupService --> EventRepository : "Restores Inventory"
OrderService ..> OrderCleanupService : "Initializes state"
@enduml
```

### Key Structural Principles
- **Dependency Inversion:** Services depend on repositories (abstractions of data access).
- **Service Orchestration:** `OrderService` acts as an orchestrator for complex cross-domain logic.
- **Separation of Concerns:** Background services handle long-running or periodic maintenance tasks without blocking the main API flows.
- **DTO Usage:** Data Transfer Objects are used consistently for all API boundaries.
