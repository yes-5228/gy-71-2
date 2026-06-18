import csv
import io
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models.contract import Contract
from app.models.payment import Payment
from app.models.workstation import Workstation
from app.schemas.payment import PaymentCreate, PaymentMarkPaid, PaymentSummary


def _apply_filters(stmt, floor: str | None = None, tenant: str | None = None,
                   period: str | None = None, status: str | None = None,
                   expense_type: str | None = None):
    if status:
        stmt = stmt.where(Payment.status == status)
    if period:
        stmt = stmt.where(Payment.period == period)
    if expense_type:
        stmt = stmt.where(Payment.expense_type == expense_type)
    if tenant:
        stmt = stmt.where(Contract.tenant_name.contains(tenant))
    if floor:
        stmt = stmt.where(Workstation.floor == floor)
    return stmt


def _joined_stmt():
    return (
        select(Payment)
        .join(Payment.contract)
        .join(Contract.workstation)
        .options(contains_eager(Payment.contract).contains_eager(Contract.workstation))
        .order_by(Payment.due_date.asc())
    )


def list_payments(db: Session, floor: str | None = None, tenant: str | None = None,
                  period: str | None = None, status: str | None = None,
                  expense_type: str | None = None) -> list[Payment]:
    refresh_overdue_payments(db)
    stmt = _apply_filters(_joined_stmt(), floor, tenant, period, status, expense_type)
    return list(db.scalars(stmt).unique().all())


def get_payment_summary(db: Session, floor: str | None = None, tenant: str | None = None,
                        period: str | None = None, status: str | None = None,
                        expense_type: str | None = None) -> PaymentSummary:
    refresh_overdue_payments(db)

    def _filtered_sum(status_val: str | None, skip_status_filter: bool = False):
        stmt = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .select_from(Payment)
            .join(Payment.contract)
            .join(Contract.workstation)
        )
        if status_val:
            stmt = stmt.where(Payment.status == status_val)
        effective_status = None if skip_status_filter else status
        stmt = _apply_filters(stmt, floor, tenant, period, effective_status, expense_type)
        return float(db.scalar(stmt) or 0)

    def _filtered_count(status_val: str | None, skip_status_filter: bool = False):
        stmt = (
            select(func.count())
            .select_from(Payment)
            .join(Payment.contract)
            .join(Contract.workstation)
        )
        if status_val:
            stmt = stmt.where(Payment.status == status_val)
        effective_status = None if skip_status_filter else status
        stmt = _apply_filters(stmt, floor, tenant, period, effective_status, expense_type)
        return int(db.scalar(stmt) or 0)

    total_amount = _filtered_sum(None)
    paid_amount = _filtered_sum("paid")
    unpaid_amount = _filtered_sum("unpaid")
    overdue_amount = _filtered_sum("overdue")
    overdue_count = _filtered_count("overdue")

    overdue_alert_amount = _filtered_sum("overdue", skip_status_filter=True)
    overdue_alert_count = _filtered_count("overdue", skip_status_filter=True)

    return PaymentSummary(
        total_amount=total_amount,
        paid_amount=paid_amount,
        unpaid_amount=unpaid_amount,
        overdue_amount=overdue_amount,
        overdue_count=overdue_count,
        overdue_alert_amount=overdue_alert_amount,
        overdue_alert_count=overdue_alert_count,
    )


def export_payments_csv(db: Session, floor: str | None = None, tenant: str | None = None,
                        period: str | None = None, status: str | None = None,
                        expense_type: str | None = None) -> str:
    rows = list_payments(db, floor, tenant, period, status, expense_type)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["合同编号", "租户", "楼层", "账期", "费用类型", "金额", "到期日", "状态", "备注"])
    for p in rows:
        floor_val = p.contract.workstation.floor if p.contract and p.contract.workstation else ""
        writer.writerow([
            p.contract.contract_no if p.contract else "",
            p.contract.tenant_name if p.contract else "",
            floor_val,
            p.period,
            p.expense_type,
            p.amount,
            p.due_date,
            p.status,
            p.note,
        ])
    return buf.getvalue()


def get_filter_options(db: Session) -> dict:
    refresh_overdue_payments(db)
    floors = [r[0] for r in db.execute(select(Workstation.floor).distinct()).all() if r[0]]
    tenants = [r[0] for r in db.execute(select(Contract.tenant_name).distinct()).all() if r[0]]
    periods = [r[0] for r in db.execute(select(Payment.period).distinct().order_by(Payment.period.desc())).all() if r[0]]
    expense_types = [r[0] for r in db.execute(select(Payment.expense_type).distinct()).all() if r[0]]
    return {
        "floors": sorted(floors),
        "tenants": sorted(tenants),
        "periods": periods,
        "expense_types": sorted(expense_types),
    }


def create_payment(db: Session, payload: PaymentCreate) -> Payment:
    contract = db.get(Contract, payload.contract_id)
    if not contract:
        raise ValueError("contract_not_found")
    payment = Payment(**payload.model_dump(), status="unpaid")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def mark_payment_paid(db: Session, payment_id: int, payload: PaymentMarkPaid) -> Payment | None:
    payment = db.get(Payment, payment_id)
    if not payment:
        return None
    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    payment.method = payload.method
    if payload.note is not None:
        payment.note = payload.note
    db.commit()
    db.refresh(payment)
    return payment


def overdue_payments(db: Session) -> list[Payment]:
    refresh_overdue_payments(db)
    stmt = (
        select(Payment)
        .options(joinedload(Payment.contract))
        .where(Payment.status == "overdue")
        .order_by(Payment.due_date.asc())
    )
    return list(db.scalars(stmt).all())


def refresh_overdue_payments(db: Session) -> None:
    today = date.today()
    payments = db.scalars(
        select(Payment).where(Payment.status == "unpaid", Payment.due_date < today)
    ).all()
    for payment in payments:
        payment.status = "overdue"
    if payments:
        db.commit()
