# State Diagrams

This document illustrates the lifecycles of core entities in the "You Want Ticket" system, organized by complexity levels.

---

## Version 1: Core User & Event Lifecycles
This version focuses on the basic activation states for users and the scheduling of events.

### 1.1 User Account State
```plantuml
@startuml
title 1.1 User Account State Diagram

[*] --> ACTIVE : User Registered

state ACTIVE {
  ACTIVE --> INACTIVE : Deactivated by Admin
}

state INACTIVE {
  INACTIVE --> ACTIVE : Reactivated by Admin
}

ACTIVE --> [*]
INACTIVE --> [*]
@enduml
```

### 1.2 Event Lifecycle
```plantuml
@startuml
title 1.2 Event Lifecycle Diagram

[*] --> SCHEDULED : Event Created

state SCHEDULED {
  SCHEDULED --> ACTIVE : Start Time Reached\n(Scheduler)
  SCHEDULED --> CANCELLED : Cancelled by Organizer\n(Service Call)
}

state ACTIVE {
  ACTIVE --> FINISHED : End Time Reached\n(Scheduler)
}

state CANCELLED
state FINISHED

CANCELLED --> [*]
FINISHED --> [*]
@enduml
```

---

## Version 2: Integrated Purchase State Machine
This version illustrates the interconnected lifecycles of Orders and Tickets during a successful purchase.

```plantuml
@startuml
title Version 2 - Purchase State Machine

[*] --> ORDER_IN_PROGRESS : Order Created\n(Inventory Locked)

state ORDER_IN_PROGRESS {
  ORDER_IN_PROGRESS --> ORDER_FINALIZED : User Finalizes\n(Service Call)
  ORDER_IN_PROGRESS --> ORDER_CANCELLED : User Cancels\n(Service Call)
}

state ORDER_FINALIZED {
  ORDER_FINALIZED --> TICKET_SCHEDULED : Generate Tickets\n(Ticket Service)
}

state TICKET_SCHEDULED {
  TICKET_SCHEDULED --> TICKET_COMPLETED : Ticket Used\n(Service Call)
  TICKET_SCHEDULED --> TICKET_CANCELLED : Refund/Cancel\n(Service Call)
}

ORDER_CANCELLED --> [*] : Release Inventory
TICKET_COMPLETED --> [*]
TICKET_CANCELLED --> [*]
@enduml
```

---

## Version 3: Advanced Failure & Cleanup States
The final state model focusing on automated cleanup, timeout handling, and inventory resolution.

### 3.1 Order Expiration & Recovery
```plantuml
@startuml
title 3.1 Order Expiration Lifecycle

[*] --> IN_PROGRESS : Order Created\n(Tickets Reserved)

state IN_PROGRESS {
  IN_PROGRESS --> EXPIRED : 5-Minute Timeout\n(Order Cleanup Service)
  IN_PROGRESS --> COMPLETED : Finalize Request\n(User)
}

state EXPIRED {
  EXPIRED --> INVENTORY_RELEASED : Restore Available Tickets\n(Event Service)
}

state INVENTORY_RELEASED {
  INVENTORY_RELEASED --> [*] : Transaction Committed
}

COMPLETED --> [*]
@enduml
```

### 3.2 System Terminal States
```plantuml
@startuml
title 3.2 Ticket Terminal States

state TICKET_SCHEDULED {
  TICKET_SCHEDULED --> TICKET_EXPIRED : Event Finished\n(Scheduler)
}

state TICKET_EXPIRED : Ticket Invalidated\n(No Entry Allowed)

TICKET_EXPIRED --> [*]
@enduml
```

### State Transition Logic
- **Event Transitions:** Managed by `APScheduler` in `EventService`. Status updates are atomic database operations.
- **Order Expiration:** The `OrderCleanupService` runs every 5 minutes, identifying `IN_PROGRESS` orders older than 5 minutes and transitioning them to `EXPIRED`.
- **Inventory Restoration:** When an order enters the `EXPIRED` or `CANCELLED` state, a service call automatically increments the event's `available_number_of_tickets`.
- **User States:** Managed via the `is_active` boolean in the `User` model, affecting the `AuthService` login flow.
