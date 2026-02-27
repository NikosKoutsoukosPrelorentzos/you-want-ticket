# Sequence Diagrams

This document illustrates the step-by-step interaction between objects for key workflows in the "You Want Ticket" system using PlantUML Sequence Diagrams.

## 1. Create Event (Organizer Workflow)
This diagram shows the sequence of calls from the moment an organizer submits a new event until it is persisted and scheduled.

```plantuml
@startuml
title Create Event Sequence Diagram
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

ES -> ES : _validations(dto)
ES -> ER : create_event(dto, user_uuid)
activate ER

ER -> DB : INSERT event
activate DB
DB --> ER : Event Record
deactivate DB

ER --> ES : db_event
deactivate ER

ES -> SCH : add_job(start_date, event_uuid_start)
ES -> SCH : add_job(end_date, event_uuid_end)

ES --> EC : EventDTO
deactivate ES

EC --> Organizer : 201 Created (EventDTO)
deactivate EC
@enduml
```

---

## 2. Place Order (Customer Workflow)
This diagram shows how a customer reserves tickets for an event. It highlights the inventory management (decrementing tickets) and order creation.

```plantuml
@startuml
title Place Order Sequence Diagram
autonumber

actor Customer
boundary "Orders Controller" as OC
control "Order Service" as OS
control "Event Service" as ES
entity "Order Repository" as OR
entity "Event Repository" as ER
database "PostgreSQL" as DB

Customer -> OC : POST /orders/ (OrderCreate)
activate OC

OC -> OS : create_order(dto, user_uuid)
activate OS

OS -> ES : get_event_by_uuid(event_uuid)
activate ES
ES -> ER : get_event_by_uuid(event_uuid)
ER -> DB : SELECT event
DB --> ER : Event Record
ER --> ES : db_event
deactivate ES

OS -> ES : remove_available_tickets(event_uuid, count)
activate ES
ES -> ER : remove_available_tickets(event_uuid, count)
ER -> DB : UPDATE event (SET available = available - count)
DB --> ER : rows affected
ER --> ES : result
deactivate ES

OS -> OR : create_order(dto, user_uuid)
activate OR
OR -> DB : INSERT order (Status: IN_PROGRESS)
OR --> OS : db_order
deactivate OR

OS -> OR : commit()
OS --> OC : OrderDTO
deactivate OS

OC --> Customer : 201 Created (OrderDTO)
deactivate OC
@enduml
```

---

## 3. Finalize Order (Customer Workflow)
This diagram illustrates the process of completing a purchase, which triggers the generation of unique tickets.

```plantuml
@startuml
title Finalize Order Sequence Diagram
autonumber

actor Customer
boundary "Orders Controller" as OC
control "Order Service" as OS
control "Ticket Service" as TS
entity "Order Repository" as OR
entity "Ticket Repository" as TR
database "PostgreSQL" as DB

Customer -> OC : PUT /orders/{uuid}/finalize
activate OC

OC -> OS : finalize_order_by_user(uuid, user_uuid)
activate OS

OS -> OR : get_order_by_uuid(uuid)
OR -> DB : SELECT order
DB --> OR : db_order

OS -> OR : finalize_order_by_user(uuid, user_uuid)
OR -> DB : UPDATE order (Status: FINALIZED)

OS -> TS : create_tickets(list[TicketCreate])
activate TS
loop For each ticket in order
    TS -> TR : create_ticket(request)
    TR -> DB : INSERT ticket
end
TS --> OS : list[TicketDTO]
deactivate TS

OS -> OR : commit()

OS --> OC : list[TicketDTO]
deactivate OS

OC --> Customer : 200 OK (list[TicketDTO])
deactivate OC
@enduml
```

### Key Interaction Details
- **Transaction Scope:** Each high-level service call (like `create_order` or `finalize_order`) is responsible for committing or rolling back the database transaction to ensure data consistency.
- **Service Orchestration:** `OrderService` acts as an orchestrator, coordinating calls between `EventService` (for inventory) and `TicketService` (for generation).
- **Asynchronous Actions:** The `APScheduler` is invoked during event creation to handle future state changes independently of the request/response cycle.
