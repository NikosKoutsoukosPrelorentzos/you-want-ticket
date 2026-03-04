# Communication Diagrams

This document illustrates the interactions between system components for key workflows, organized by complexity levels.

---

## Version 1: Core User & Event Interactions
This version covers basic identity management and event administration.

### 1.1 User Registration
```plantuml
@startuml
skinparam monochrome true
title 1.1 User Registration Interaction

agent User
boundary UsersController
control UserService
entity UserRepository
database Database

User -> UsersController : 1: POST /users/ (UserCreate)
UsersController -> UserService : 2: create_user(dto)
UserService -> UserRepository : 3: get_by_email(email)
UserRepository -> Database : 4: SELECT user
UserService -> UserService : 5: hash_password()
UserService -> UserRepository : 6: create(dto)
UserRepository -> Database : 7: INSERT user
UserService --> UsersController : 8: UserDTO
UsersController --> User : 9: 201 Created (UserDTO)
@enduml
```

### 1.2 User Login
```plantuml
@startuml
skinparam monochrome true
title 1.2 User Login Interaction

agent User
boundary LoginController
control AuthService
entity UserRepository
database Database

User -> LoginController : 1: POST /login/access-token
LoginController -> AuthService : 2: login(email, password)
AuthService -> UserRepository : 3: get_by_email(email)
UserRepository -> Database : 4: SELECT user
AuthService -> AuthService : 5: verify_password()
AuthService -> AuthService : 6: create_access_token()
AuthService --> LoginController : 7: TokenDTO
LoginController --> User : 8: 200 OK (TokenDTO)
@enduml
```

### 1.3 Event Management (CRUD)
```plantuml
@startuml
skinparam monochrome true
title 1.3 Event CRUD Interaction

agent Organizer
boundary EventsController
control EventService
entity EventRepository
database Database
collections Scheduler

Organizer -> EventsController : 1: POST /events/ (EventCreate)
EventsController -> EventService : 2: create_event(dto, user_uuid)\n\n
EventService -> EventRepository : 3: create(dto, user_uuid)\n\n\n\n\n\n\n
EventRepository -> Database : 4: INSERT event
EventService -> Scheduler : 5: schedule_jobs(start, end)
EventService --> EventsController : 6: EventDTO
EventsController --> Organizer : 7: 200 OK

Organizer -> EventsController : 8: PUT /events/{uuid}/cancel\n
EventsController -> EventService : 9: cancel_event(uuid, user_uuid)\n
EventService -> EventRepository : 10: get_by_uuid(uuid)\n\n\n\n
EventService -> EventRepository : 11: update_status(CANCELLED)
EventService -> Scheduler : 12: remove_jobs(uuid)
EventService --> EventsController : 13: Success\n\n\n\n\n\n\n\n\n
EventsController --> Organizer : 14: 200 OK
@enduml
```

---

## Version 2: Integrated Purchase Flow
This version shows the end-to-end communication required for a ticket purchase, including authentication verification.

```plantuml
@startuml
skinparam monochrome true
title Version 2 - Integrated Purchase Journey

agent Customer
boundary AuthMiddleware
boundary OrdersController
control OrderService
control EventService
control TicketService
entity OrderRepository
database Database

Customer -> AuthMiddleware : 1: POST /orders/ (with JWT)
AuthMiddleware -> AuthMiddleware : 2: validate_token()
AuthMiddleware -> OrdersController : 3: forward request (user_uuid)
OrdersController -> OrderService : 4: create_order(dto, user_uuid)
OrderService -> EventService : 5: check_availability(event_uuid)\n\n\n
OrderService -> EventService : 6: reserve_tickets(count)
OrderService -> OrderRepository : 7: create(IN_PROGRESS)
OrderRepository -> Database : 8: INSERT order
OrderService --> OrdersController : 9: OrderDTO
OrdersController --> Customer : 10: 201 Created

Customer -> OrdersController : 11: PUT /orders/{uuid}/finalize
OrdersController -> OrderService : 12: finalize_order(uuid)
OrderService -> OrderRepository : 13: update_status(COMPLETED)\n\n\n\n\n\n\n
OrderService -> TicketService : 14: generate_tickets(order_uuid)
TicketService -> Database : 15: INSERT tickets\n\n\n\n
OrderService --> OrdersController : 16: List[TicketDTO]
OrdersController --> Customer : 17: 200 OK
@enduml
```

---

## Version 3: Advanced System Tasks
This version focuses on automated background communication.

### 3.1 Expired Order Cleanup (Background)
```plantuml
@startuml
skinparam monochrome true
title Version 3 - Background Cleanup Interaction

collections Scheduler
control OrderCleanupService
entity OrderRepository
entity EventRepository
database Database

Scheduler -> OrderCleanupService : 1: trigger_cleanup()
OrderCleanupService -> OrderRepository : 2: get_expired_orders(cutoff)
OrderRepository -> Database : 3: SELECT orders
loop for each expired order
    OrderCleanupService -> OrderRepository : 4: update_status(CANCELLED)
    OrderCleanupService -> EventRepository : 5: return_tickets(count)
    EventRepository -> Database : 6: UPDATE available_tickets
end
OrderCleanupService -> Database : 7: COMMIT transaction
@enduml
```

### Key Interaction Principles
- **Stateless Auth:** Auth middleware validates the JWT for every protected request before it reaches the controller.
- **Service-to-Service:** Complex operations (like ordering) require the orchestrator service (`OrderService`) to communicate with domain services (`EventService`, `TicketService`).
- **Asynchronous Tasks:** The `Scheduler` acts as an external trigger for background service logic, which operates independently of user requests.
