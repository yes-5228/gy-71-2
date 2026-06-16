from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import get_dashboard_stats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
def read_stats(db: Session = Depends(get_db)) -> DashboardStats:
    return get_dashboard_stats(db)
