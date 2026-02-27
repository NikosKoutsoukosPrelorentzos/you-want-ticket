# Activity Diagrams

This document contains Activity Diagrams representing the operational flows of the "You Want Ticket" system using PlantUML.

## 1. Create Event Process
This diagram shows the steps taken by an organizer to create a new event, including validation and scheduling.

```plantuml
@startuml
title Create Event Activity Diagram
start
:Organizer submits event details (EventCreate);
if (Start date < End date?) then (yes)
  if (Available tickets > 0?) then (yes)
    :Save Event to Database (Status: SCHEDULED);
    :Schedule 'Start Event' job (APScheduler);
    :Schedule 'End Event' job (APScheduler);
    :Return EventDTO (201 Created);
    stop
  else (no)
    :Raise HTTPException (400: Invalid tickets);
    stop
  endif
else (no)
  :Raise HTTPException (400: Invalid dates);
  stop
endif
@enduml
```

---

## 2. Ticket Purchase Lifecycle
This diagram illustrates the two-step process: creating an initial order and then finalizing it to receive tickets.

```plantuml
@startuml
title Ticket Purchase Lifecycle
|Customer|
start
:Submit Order Request (Event, Quantity);
|Order Service|
:Check Event existence and dates;
if (Event has not passed?) then (yes)
  :Check ticket availability;
  if (Available >= Quantity?) then (yes)
    :Remove tickets from Event inventory;
    :Create Order (Status: IN_PROGRESS);
    :Return OrderDTO;
    |Customer|
    :Review Order;
    :Submit Finalize Request;
    |Order Service|
    :Verify Order status and owner;
    if (Status is IN_PROGRESS?) then (yes)
      :Update Order status (COMPLETED);
      :Generate Ticket records;
      :Commit transaction;
      :Return list of TicketDTOs;
      stop
    else (no)
      :Raise HTTPException (409: Conflict);
      stop
    endif
  else (no)
    :Raise HTTPException (400: Not enough tickets);
    stop
  endif
else (no)
  :Raise HTTPException (400: Event has passed);
  stop
endif
@enduml
```

---

## 3. Expired Order Cleanup (Background Task)
This background process ensures that tickets held by unfinalized orders are released back to the event inventory after a timeout.

```plantuml
@startuml
title Expired Order Cleanup
start
:Scheduler triggers Cleanup Job (Every 5 mins);
:Calculate Cutoff Time (Now - 5 minutes);
:Query for orders in 'IN_PROGRESS' status before Cutoff;
if (Found expired orders?) then (yes)
  repeat
    :Select next expired order;
    :Cancel Order (Update status to CANCELLED);
    :Return tickets to Event (Available += Quantity);
    :Commit DB Transaction;
  repeat while (More expired orders?)
  :Log cleanup summary;
else (no)
  :Log: "No expired orders found";
endif
stop
@enduml
```

### Key Workflow Principles
- **Inventory Locking:** Tickets are temporarily "locked" (removed from inventory) as soon as an order is created to prevent overbooking.
- **Fail-Safe Cleanup:** The background cleanup service prevents permanent loss of inventory from abandoned or timed-out carts.
- **Atomic Operations:** Most service actions are wrapped in transactions (commit/rollback) to ensure data consistency.
