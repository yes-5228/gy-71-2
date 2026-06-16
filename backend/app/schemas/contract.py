from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.workstation import WorkstationRead


class ContractBase(BaseModel):
    tenant_name: str = Field(..., min_length=2)
    tenant_contact: str = ""
    workstation_id: int
    start_date: date
    end_date: date
    monthly_rent: float = Field(..., ge=0)
    deposit: float = Field(default=0, ge=0)


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    tenant_name: str | None = None
    tenant_contact: str | None = None
    end_date: date | None = None
    status: str | None = None


class ContractRead(ContractBase):
    id: int
    contract_no: str
    status: str
    signed_at: datetime
    workstation: WorkstationRead | None = None

    model_config = {"from_attributes": True}
