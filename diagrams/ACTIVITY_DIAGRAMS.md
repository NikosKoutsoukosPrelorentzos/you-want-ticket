# Activity Diagrams

This document contains Activity Diagrams representing the operational flows of the "You Want Ticket" system, organized by complexity levels.

---

## Version 1: Core User & Event CRUD
This version focus on the basic administrative and user account management flows.

### 1.1 User Registration
```plantuml
@startuml
title User Registration Activity Diagram
start
:User submits registration details (UserCreate);
:Validate input (email, password complexity);
if (Email already exists?) then (yes)
  :Raise HTTPException (400: Email registered);
  stop
else (no)
  :Hash password (bcrypt);
  :Save User to Database;
  :Return UserDTO (201 Created);
  stop
endif
@enduml
```

### 1.2 User Login
```plantuml
@startuml
title User Login Activity Diagram
start
:User submits credentials (email, password);
:Query User by email;
if (User exists?) then (yes)
  :Verify hashed password;
  if (Password valid?) then (yes)
    :Generate JWT Access Token;
    :Return TokenDTO;
    stop
  else (no)
    :Raise HTTPException (401: Unauthorized);
    stop
  endif
else (no)
  :Raise HTTPException (401: Unauthorized);
  stop
endif
@enduml
```

### 1.3 Event Management (CRUD)
```plantuml
@startuml
title Event Management Activity Diagram
|Organizer|
start
:Choose Action (Create, List, Cancel);
if (Action == Create) then (yes)
  :Submit Event details;
  if (Dates and Tickets valid?) then (yes)
    :Save Event (Status: SCHEDULED);
    :Schedule start/end jobs;
    :Return EventDTO;
  else (no)
    :Return 400 Bad Request;
  endif
elseif (Action == List) then (yes)
  :Request Events with filters;
  :Query DB for active events;
  :Return list of EventDTOs;
else (Action == Cancel)
  :Submit Event UUID;
  :Check if Event exists and belongs to user;
  :Update status to CANCELLED;
  :Cancel scheduled jobs;
  :Return 200 OK;
endif
stop
@enduml
```

---

## Version 2: Integrated Purchase Flow
This version combines authentication, event discovery, and the ticketing lifecycle into a single user journey.

```plantuml
@startuml
title Integrated Ticket Purchase Journey
|Customer|
start
:Login to application;
|Auth Service|
:Validate credentials and return JWT;
|Customer|
:Browse available Events (Filtered);
|Event Service|
:Return list of active events;
|Customer|
:Select Event and specify Quantity;
|Order Service|
:Check availability (Lock inventory);
if (Tickets available?) then (yes)
  :Create Order (Status: IN_PROGRESS);
  :Return OrderDTO;
  |Customer|
  :Confirm/Pay for Order;
  |Order Service|
  :Finalize Order;
  :Update status to COMPLETED;
  :Generate Ticket records;
  |Customer|
  :Receive TicketDTOs;
  stop
else (no)
  :Notify: "Sold Out" or "Insufficient Quantity";
  stop
endif
@enduml
```

---

## Version 3: Advanced System Tasks
This version includes background maintenance and automated state transitions.

### 3.1 Expired Order Cleanup (Background Task)
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
- **Identity First:** Most operations (except registration/login) require a valid JWT.
- **Inventory Locking:** Tickets are temporarily "locked" during the `IN_PROGRESS` order phase.
- **Fail-Safe Cleanup:** Background processes ensure data consistency if users abandon their carts.
- **State Driven:** Events and Orders move through strictly defined enums (SCHEDULED, ACTIVE, COMPLETED, CANCELLED).
