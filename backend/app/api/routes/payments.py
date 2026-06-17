from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentMarkPaid, PaymentRead
from app.services.payment_service import (
    create_payment,
    export_payments_csv,
    get_filter_options,
    get_payment_summary,
    list_payments,
    mark_payment_paid,
)

router = APIRouter()


def serialize_payment(payment) -> dict:
    data = PaymentRead.model_validate(payment).model_dump()
    if payment.contract:
        data["tenant_name"] = payment.contract.tenant_name
        data["contract_no"] = payment.contract.contract_no
        if payment.contract.workstation:
            data["floor"] = payment.contract.workstation.floor
    return data


def _filter_params(floor: str | None = None, tenant: str | None = None,
                   period: str | None = None, status: str | None = None,
                   expense_type: str | None = None) -> dict:
    return dict(floor=floor, tenant=tenant, period=period, status=status, expense_type=expense_type)


@router.get("/filter-options")
def read_filter_options(db: Session = Depends(get_db)):
    return get_filter_options(db)


@router.get("/summary")
def read_summary(floor: str | None = None, tenant: str | None = None,
                 period: str | None = None, status: str | None = None,
                 expense_type: str | None = None, db: Session = Depends(get_db)):
    return get_payment_summary(db, **_filter_params(floor, tenant, period, status, expense_type))


@router.get("/export", response_class=PlainTextResponse)
def export_csv(floor: str | None = None, tenant: str | None = None,
               period: str | None = None, status: str | None = None,
               expense_type: str | None = None, db: Session = Depends(get_db)):
    content = export_payments_csv(db, **_filter_params(floor, tenant, period, status, expense_type))
    return PlainTextResponse(content=content, media_type="text/csv; charset=utf-8-sig")


@router.get("", response_model=list[PaymentRead])
def read_payments(floor: str | None = None, tenant: str | None = None,
                  period: str | None = None, status: str | None = None,
                  expense_type: str | None = None, db: Session = Depends(get_db)):
    payments = list_payments(db, **_filter_params(floor, tenant, period, status, expense_type))
    return [serialize_payment(p) for p in payments]


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def add_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    try:
        payment = create_payment(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="合同不存在") from exc
    return serialize_payment(payment)


@router.post("/{payment_id}/mark-paid", response_model=PaymentRead)
def pay_payment(payment_id: int, payload: PaymentMarkPaid, db: Session = Depends(get_db)):
    payment = mark_payment_paid(db, payment_id, payload)
    if not payment:
        raise HTTPException(status_code=404, detail="账单不存在")
    return serialize_payment(payment)
