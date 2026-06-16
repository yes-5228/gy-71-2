from datetime import datetime

from pydantic import BaseModel, Field


class WorkstationBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=32)
    area: str
    floor: str
    seats: int = Field(default=1, ge=1)
    monthly_rent: float = Field(..., ge=0)
    status: str = "available"
    facilities: str = ""


class WorkstationCreate(WorkstationBase):
    pass


class WorkstationUpdate(BaseModel):
    area: str | None = None
    floor: str | None = None
    seats: int | None = Field(default=None, ge=1)
    monthly_rent: float | None = Field(default=None, ge=0)
    status: str | None = None
    facilities: str | None = None


class WorkstationRead(WorkstationBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
