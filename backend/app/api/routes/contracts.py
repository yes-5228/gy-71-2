from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contract import ContractCreate, ContractRead, ContractUpdate
from app.services.contract_service import create_contract, list_contracts, update_contract

router = APIRouter()


@router.get("", response_model=list[ContractRead])
def read_contracts(status: str | None = None, db: Session = Depends(get_db)):
    return list_contracts(db, status=status)


@router.post("", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def sign_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    try:
        return create_contract(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="合同编号冲突，请稍后重试") from exc
    except ValueError as exc:
        messages = {
            "workstation_not_found": "工位不存在",
            "workstation_not_available": "工位当前不可租赁",
            "invalid_contract_dates": "合同结束日期必须晚于开始日期",
        }
        raise HTTPException(status_code=400, detail=messages.get(str(exc), "合同数据无效")) from exc


@router.patch("/{contract_id}", response_model=ContractRead)
def edit_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db)):
    contract = update_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract
