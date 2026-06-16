from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.contract import Contract
from app.models.workstation import Workstation
from app.schemas.contract import ContractCreate, ContractUpdate


def list_contracts(db: Session, status: str | None = None) -> list[Contract]:
    stmt = (
        select(Contract)
        .options(joinedload(Contract.workstation))
        .order_by(Contract.end_date.asc())
    )
    if status:
        stmt = stmt.where(Contract.status == status)
    return list(db.scalars(stmt).all())


def create_contract(db: Session, payload: ContractCreate) -> Contract:
    workstation = db.get(Workstation, payload.workstation_id)
    if not workstation:
        raise ValueError("workstation_not_found")
    if workstation.status not in {"available", "reserved"}:
        raise ValueError("workstation_not_available")
    if payload.end_date <= payload.start_date:
        raise ValueError("invalid_contract_dates")

    contract = Contract(
        **payload.model_dump(),
        contract_no=f"CT-{date.today().strftime('%Y%m%d')}-{payload.workstation_id:03d}",
        status="active",
    )
    workstation.status = "leased"
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def update_contract(db: Session, contract_id: int, payload: ContractUpdate) -> Contract | None:
    contract = db.get(Contract, contract_id)
    if not contract:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(contract, key, value)
    if contract.status in {"terminated", "expired"} and contract.workstation:
        contract.workstation.status = "available"
    db.commit()
    db.refresh(contract)
    return contract


def expiring_contracts(db: Session, days: int) -> list[Contract]:
    today = date.today()
    until = date.fromordinal(today.toordinal() + days)
    stmt = (
        select(Contract)
        .options(joinedload(Contract.workstation))
        .where(Contract.status == "active", Contract.end_date >= today, Contract.end_date <= until)
        .order_by(Contract.end_date.asc())
    )
    return list(db.scalars(stmt).all())
