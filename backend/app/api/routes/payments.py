from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentMarkPaid, PaymentRead
from app.services.payment_service import create_payment, list_payments, mark_payment_paid

router = APIRouter()


def serialize_payment(payment) -> dict:
    data = PaymentRead.model_validate(payment).model_dump()
    if payment.contract:
        data["tenant_name"] = payment.contract.tenant_name
        data["contract_no"] = payment.contract.contract_no
    return data


@router.get("", response_model=list[PaymentRead])
def read_payments(status: str | None = None, db: Session = Depends(get_db)):
    return [serialize_payment(payment) for payment in list_payments(db, status=status)]


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
