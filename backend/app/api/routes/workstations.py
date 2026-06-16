from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.workstation import WorkstationCreate, WorkstationRead, WorkstationUpdate
from app.services.workstation_service import create_workstation, list_workstations, update_workstation

router = APIRouter()


@router.get("", response_model=list[WorkstationRead])
def read_workstations(status: str | None = None, db: Session = Depends(get_db)):
    return list_workstations(db, status=status)


@router.post("", response_model=WorkstationRead, status_code=status.HTTP_201_CREATED)
def add_workstation(payload: WorkstationCreate, db: Session = Depends(get_db)):
    try:
        return create_workstation(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="工位编号已存在") from exc


@router.patch("/{workstation_id}", response_model=WorkstationRead)
def edit_workstation(workstation_id: int, payload: WorkstationUpdate, db: Session = Depends(get_db)):
    workstation = update_workstation(db, workstation_id, payload)
    if not workstation:
        raise HTTPException(status_code=404, detail="工位不存在")
    return workstation
