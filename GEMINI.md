# GEMINI.md - You Want Ticket

## Project Overview

**You Want Ticket** is a backend service for a ticketing system built with **FastAPI**. It manages events, users, and ticket orders, featuring a layered architecture for maintainability and scalability.

### Core Technologies
- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Data Validation:** Pydantic (v2)
- **Authentication:** JWT (python-jose) with Passlib (bcrypt)
- **Background Tasks:** APScheduler for event state transitions and order cleanups
- **Deployment:** Docker Compose for local development (PostgreSQL)

### Architecture
The project follows a modular, layered structure:
- `app/api/`: REST API endpoints (v1) and dependency injection (`deps.py`).
- `app/services/`: Business logic layer coordinating between repositories and external services (like the scheduler).
- `app/repositories/`: Data access layer using SQLAlchemy.
- `app/models/`: SQLAlchemy database models.
- `app/dtos/`: Pydantic models for data transfer and validation.
- `app/enums/`: Domain-specific enumerations (EventStatus, OrderStatus, etc.).
- `app/core/`: Centralized configuration, security, and logging.

---

## Building and Running

### Prerequisites
- Python 3.10+ (Tested on 3.12)
- Docker and Docker Compose

### Environment Setup
1. **Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Database:**
   Start the PostgreSQL container:
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. **Configuration:**
   The application uses Pydantic Settings. Update `app/core/config.py` or set environment variables as needed.

### Running the Application
Start the development server:
```bash
uvicorn main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

### Testing
Run the test suite using pytest:
```bash
pytest
```

---

## Development Conventions

### Coding Style
- **Formatting:** Adhere to `black` and `isort` standards.
- **Linting:** Check for errors with `flake8`.
- **Typing:** Strict type hinting is required. Use `mypy` for static type checking:
  ```bash
  mypy .
  ```

### Design Patterns
- **Dependency Injection:** Use FastAPI's `Depends` for services and database sessions.
- **Service Layer:** All business logic must reside in `app/services/`. Controllers (endpoints) should only handle request/response mapping.
- **Repository Pattern:** Encapsulate database queries in repository classes to keep services clean.
- **UUIDs:** Use UUIDs for public-facing identifiers instead of auto-incrementing IDs.

### Database Migrations
Currently, the application uses `Base.metadata.create_all(bind=engine)` in `main.py` for table creation. For production environments, consider integrating Alembic.
