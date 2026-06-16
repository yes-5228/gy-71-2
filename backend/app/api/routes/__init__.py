from fastapi import APIRouter

from app.api.routes import contracts, dashboard, payments, reminders, workstations

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(workstations.router, prefix="/workstations", tags=["workstations"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
