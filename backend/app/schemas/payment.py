from datetime import date, datetime

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    contract_id: int
    period: str = Field(..., min_length=4, max_length=24)
    amount: float = Field(..., ge=0)
    due_date: date
    note: str = ""
    expense_type: str = "rent"


class PaymentCreate(PaymentBase):
    pass


class PaymentMarkPaid(BaseModel):
    method: str = "bank_transfer"
    note: str | None = None


class PaymentRead(PaymentBase):
    id: int
    paid_at: datetime | None
    status: str
    method: str
    tenant_name: str | None = None
    contract_no: str | None = None
    floor: str | None = None

    model_config = {"from_attributes": True}


class PaymentSummary(BaseModel):
    total_amount: float
    paid_amount: float
    unpaid_amount: float
    overdue_amount: float
    overdue_count: int
