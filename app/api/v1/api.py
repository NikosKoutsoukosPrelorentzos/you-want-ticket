from fastapi import APIRouter

from app.api.v1.endpoints import login, users, events, orders

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])

api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
