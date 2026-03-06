# Sequence Diagrams

This document illustrates the step-by-step interaction between system components for key workflows, organized by complexity levels.

---

## Version 1: Core User & Event Sequences
This version focuses on identity management and basic administrative flows.

### 1.1 User Registration
```plantuml
@startuml
title 1.1 User Registration Sequence
autonumber

actor User
boundary "Users Controller" as UC
control "User Service" as US
entity "User Repository" as UR
database "PostgreSQL" as DB

User -> UC : POST /users/ (UserCreate)
activate UC

UC -> US : create_user(dto)
activate US

US -> UR : get_by_email(email)
activate UR
UR -> DB : SELECT user
DB --> UR : user_obj
deactivate UR

US -> US : hash_password()
US -> UR : create(dto)
activate UR
UR -> DB : INSERT user
DB --> UR : created_user
deactivate UR

US --> UC : UserDTO
deactivate US

UC --> User : 201 Created (UserDTO)
deactivate UC
@enduml
```

### 1.2 User Login
```plantuml
@startuml
title 1.2 User Login Sequence
autonumber

actor User
boundary "Login Controller" as LC
control "Auth Service" as AS
entity "User Repository" as UR
database "PostgreSQL" as DB

User -> LC : POST /login/access-token
activate LC

LC -> AS : login(email, password)
activate AS

AS -> UR : get_by_email(email)
activate UR
UR -> DB : SELECT user
DB --> UR : user_obj
deactivate UR

AS -> AS : verify_password()
AS -> AS : create_access_token()

AS --> LC : TokenDTO
deactivate AS

LC --> User : 200 OK (TokenDTO)
deactivate LC
@enduml
```

### 1.3 Create Event
```plantuml
@startuml
title 1.3 Create Event Sequence
autonumber

actor Organizer
boundary "Events Controller" as EC
control "Event Service" as ES
entity "Event Repository" as ER
database "PostgreSQL" as DB
collections "APScheduler" as SCH

Organizer -> EC : POST /events/ (EventCreate)
activate EC

EC -> ES : create_event(dto, user_uuid)
activate ES

ES -> ER : create(dto, user_uuid)
activate ER
ER -> DB : INSERT event
DB --> ER : db_event
deactivate ER

ES -> SCH : add_job(start_date)
ES -> SCH : add_job(end_date)

ES --> EC : EventDTO
deactivate ES

EC --> Organizer : 201 Created (EventDTO)
deactivate EC
@enduml
```

---

## Version 2: Integrated Purchase Journey
This version shows the end-to-end ticketing lifecycle, including authentication verification.

### 2.1 Complete Purchase Flow
```plantuml
@startuml
title 2.1 Integrated Purchase Journey
autonumber

actor Customer
boundary "Auth Middleware" as AM
boundary "Orders Controller" as OC
control "Order Service" as OS
control "Event Service" as ES
control "Ticket Service" as TS
entity "Order Repository" as OR
database "PostgreSQL" as DB

Customer -> AM : POST /orders/ (OrderCreate with JWT)
activate AM
AM -> AM : validate_token()
AM -> OC : forward(user_uuid)
deactivate AM
activate OC

OC -> OS : create_order(dto, user_uuid)
activate OS

OS -> ES : check_availability(event_uuid)
activate ES
ES --> OS : available?
deactivate ES

OS -> ES : reserve_tickets(count)
activate ES
ES --> OS : success
deactivate ES

OS -> OR : create(IN_PROGRESS)
activate OR
OR -> DB : INSERT order
OR --> OS : db_order
deactivate OR

OS --> OC : OrderDTO
deactivate OS

OC --> Customer : 201 Created (OrderDTO)
deactivate OC

|||

Customer -> OC : PUT /orders/{uuid}/finalize
activate OC
OC -> OS : finalize_order(uuid)
activate OS

OS -> OR : update_status(COMPLETED)
OS -> TS : generate_tickets(order_uuid)
activate TS
TS -> DB : INSERT tickets
TS --> OS : list[TicketDTO]
deactivate TS

OS --> OC : list[TicketDTO]
deactivate OS
OC --> Customer : 200 OK
deactivate OC
@enduml
```

---

## Version 3: Advanced Background Operations
This version covers automated system tasks like cleanup and scheduled transitions.

### 3.1 Expired Order Cleanup
```plantuml
@startuml
title 3.1 Expired Order Cleanup Sequence
autonumber

collections "APScheduler" as SCH
control "Order Cleanup Service" as OCS
entity "Order Repository" as OR
entity "Event Repository" as ER
database "PostgreSQL" as DB

SCH -> OCS : trigger_cleanup()
activate OCS

OCS -> OR : get_expired_orders(cutoff)
activate OR
OR -> DB : SELECT orders
OR --> OCS : expired_orders_list
deactivate OR

loop for each expired order
    OCS -> OR : update_status(CANCELLED)
    OCS -> ER : return_tickets(count)
    activate ER
    ER -> DB : UPDATE available_tickets
    ER --> OCS : success
    deactivate ER
end

OCS -> DB : COMMIT transaction
deactivate OCS
@enduml
```

### 3.2 Automated Event State Transitions
```plantuml
@startuml
title 3.2 Automated Event State Transitions
autonumber

collections "APScheduler" as SCH
control "Event Service" as ES
entity "Event Repository" as ER
database "PostgreSQL" as DB

SCH -> ES : trigger_event_start(uuid)
activate ES
ES -> ER : update_status(ACTIVE)
ER -> DB : UPDATE event SET status=ACTIVE
ES --> SCH : success
deactivate ES

|||

SCH -> ES : trigger_event_end(uuid)
activate ES
ES -> ER : update_status(FINISHED)
ER -> DB : UPDATE event SET status=FINISHED
ES --> SCH : success
deactivate ES
@enduml
```

### Key Interaction Details
- **Auth Verification:** All protected endpoints in Versions 2 and 3 explicitly include the `Auth Middleware` token validation step.
- **Orchestration:** The `OrderService` coordinates complex multi-service tasks, ensuring that state is only persisted upon successful completion of all sub-tasks.
- **Async Triggers:** Background tasks are initiated by the `APScheduler` but executed within the service layer to maintain domain logic consistency.
