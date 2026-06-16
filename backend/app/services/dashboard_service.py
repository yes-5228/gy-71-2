from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.payment import Payment
from app.models.workstation import Workstation
from app.schemas.dashboard import DashboardStats
from app.services.payment_service import refresh_overdue_payments


def get_dashboard_stats(db: Session) -> DashboardStats:
    refresh_overdue_payments(db)
    today = date.today()
    soon = date.fromordinal(today.toordinal() + 30)

    total_workstations = db.scalar(select(func.count()).select_from(Workstation)) or 0
    available_workstations = db.scalar(
        select(func.count()).select_from(Workstation).where(Workstation.status == "available")
    ) or 0
    leased_workstations = db.scalar(
        select(func.count()).select_from(Workstation).where(Workstation.status == "leased")
    ) or 0
    active_contracts = db.scalar(
        select(func.count()).select_from(Contract).where(Contract.status == "active")
    ) or 0
    unpaid_amount = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "unpaid")
    ) or 0
    overdue_amount = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "overdue")
    ) or 0
    expiring_contracts = db.scalar(
        select(func.count())
        .select_from(Contract)
        .where(Contract.status == "active", Contract.end_date >= today, Contract.end_date <= soon)
    ) or 0

    return DashboardStats(
        total_workstations=total_workstations,
        available_workstations=available_workstations,
        leased_workstations=leased_workstations,
        active_contracts=active_contracts,
        unpaid_amount=float(unpaid_amount),
        overdue_amount=float(overdue_amount),
        expiring_contracts=expiring_contracts,
    )
