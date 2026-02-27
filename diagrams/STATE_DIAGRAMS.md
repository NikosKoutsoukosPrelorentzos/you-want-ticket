# State Diagrams

This document contains State Diagrams representing the lifecycles of core entities in the "You Want Ticket" system using PlantUML.

## 1. Event Lifecycle
The `Event` entity transitions through states based on time-based scheduler jobs or manual cancellation by the organizer.

```plantuml
@startuml
title Event State Diagram

[*] --> SCHEDULED : Event Created

state SCHEDULED {
  SCHEDULED --> ACTIVE : Start Time Reached
(Scheduler)
  SCHEDULED --> CANCELLED : Cancelled by Organizer
}

state ACTIVE {
  ACTIVE --> FINISHED : End Time Reached
(Scheduler)
}

state CANCELLED
state FINISHED

CANCELLED --> [*]
FINISHED --> [*]
@enduml
```

---

## 2. Order Lifecycle
The `Order` entity tracks the progress of a ticket purchase from initiation to completion or expiration.

```plantuml
@startuml
title Order State Diagram

[*] --> IN_PROGRESS : Order Created
(Tickets Reserved)

state IN_PROGRESS {
  IN_PROGRESS --> FINALIZED : User Finalizes Purchase
  IN_PROGRESS --> CANCELLED : User Cancels Order
  IN_PROGRESS --> EXPIRED : 5-Minute Timeout
(Cleanup Service)
}

state FINALIZED : Tickets Generated
state CANCELLED : Tickets Released to Inventory
state EXPIRED : Tickets Released to Inventory

FINALIZED --> [*]
CANCELLED --> [*]
EXPIRED --> [*]
@enduml
```

---

## 3. Ticket Lifecycle
The `Ticket` entity is created when an order is finalized and moves through states until it is either used or cancelled.

```plantuml
@startuml
title Ticket State Diagram

[*] --> SCHEDULED : Order Finalized

state SCHEDULED {
  SCHEDULED --> COMPLETED : Ticket Finalized/Used
(Service Call)
  SCHEDULED --> CANCELLED : Order/Ticket Cancelled
  SCHEDULED --> EXPIRED : Event Finished
}

state COMPLETED : Entry Granted
state CANCELLED : Invalidated
state EXPIRED : Invalidated

COMPLETED --> [*]
CANCELLED --> [*]
EXPIRED --> [*]
@enduml
```

### State Transition Logic
- **Event Transitions:** Managed by `APScheduler` in `EventService`. When an event transitions to `ACTIVE` or `FINISHED`, the corresponding repository method updates the database status.
- **Order Expiration:** The `OrderCleanupService` runs every 5 minutes, identifying `IN_PROGRESS` orders older than 5 minutes and moving them to `EXPIRED`.
- **Atomic State Changes:** Most status updates are performant repository calls (e.g., `update().where()`) to ensure consistent state across the distributed system.
