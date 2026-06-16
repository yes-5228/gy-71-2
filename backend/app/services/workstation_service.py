from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workstation import Workstation
from app.schemas.workstation import WorkstationCreate, WorkstationUpdate


def list_workstations(db: Session, status: str | None = None) -> list[Workstation]:
    stmt = select(Workstation).order_by(Workstation.area, Workstation.code)
    if status:
        stmt = stmt.where(Workstation.status == status)
    return list(db.scalars(stmt).all())


def create_workstation(db: Session, payload: WorkstationCreate) -> Workstation:
    workstation = Workstation(**payload.model_dump())
    db.add(workstation)
    db.commit()
    db.refresh(workstation)
    return workstation


def update_workstation(db: Session, workstation_id: int, payload: WorkstationUpdate) -> Workstation | None:
    workstation = db.get(Workstation, workstation_id)
    if not workstation:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(workstation, key, value)
    db.commit()
    db.refresh(workstation)
    return workstation
