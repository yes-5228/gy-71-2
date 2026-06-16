from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contract import ContractRead
from app.schemas.payment import PaymentRead
from app.services.contract_service import expiring_contracts
from app.services.payment_service import overdue_payments

router = APIRouter()


@router.get("/expiring-contracts", response_model=list[ContractRead])
def read_expiring_contracts(days: int = Query(default=30, ge=1, le=180), db: Session = Depends(get_db)):
    return expiring_contracts(db, days)


@router.get("/overdue-payments", response_model=list[PaymentRead])
def read_overdue_payments(db: Session = Depends(get_db)):
    items = []
    for payment in overdue_payments(db):
        data = PaymentRead.model_validate(payment).model_dump()
        if payment.contract:
            data["tenant_name"] = payment.contract.tenant_name
            data["contract_no"] = payment.contract.contract_no
        items.append(data)
    return items
