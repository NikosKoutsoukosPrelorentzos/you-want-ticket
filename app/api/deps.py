from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.event_repository import EventRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.dtos.user_dto import UserDTO
from app.services.auth_service import AuthService
from app.services.event_service import EventService
from app.services.order_cleanup_service import OrderCleanupService
from app.services.order_service import OrderService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


def get_auth_service(
        user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


def get_current_user(
        token: str = Depends(reusable_oauth2),
        auth_service: AuthService = Depends(get_auth_service),
) -> UserDTO:
    return auth_service.get_current_user(token)


def get_current_active_user(
        current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_event_repository(
        db: Session = Depends(get_db)
) -> EventRepository:
    return EventRepository(db)


def get_event_service(
        event_repository: EventRepository = Depends(get_event_repository),
) -> EventService:
    return EventService(event_repository)


def get_order_repository(
        db: Session = Depends(get_db)
) -> OrderRepository:
    return OrderRepository(db)


def get_ticket_repository(
        db: Session = Depends(get_db)
) -> TicketRepository:
    return TicketRepository(db)


def get_ticket_service(
        ticket_repository: TicketRepository = Depends(get_ticket_repository),
        event_repository: EventRepository = Depends(get_event_repository)
) -> TicketService:
    return TicketService(ticket_repository, event_repository)


def get_order_service(
        order_repository: OrderRepository = Depends(get_order_repository),
        event_service: EventService = Depends(get_event_service),
        ticket_service: TicketService = Depends(get_ticket_service)
) -> OrderService:
    return OrderService(order_repository, event_service, ticket_service)


def get_order_cleanup_service(
        db: Session = Depends(get_db),
        oder_service: OrderService = Depends(get_order_service),
        event_service: EventService = Depends(get_event_service),
) -> OrderCleanupService:
    return OrderCleanupService(db, oder_service, event_service)
