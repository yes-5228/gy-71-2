from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import Base, engine
from app.models.contract import Contract
from app.models.payment import Payment
from app.models.workstation import Workstation


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        has_data = db.scalar(select(Workstation.id).limit(1))
        if has_data:
            return

        today = date.today()
        workstations = [
            Workstation(code="A-0801", area="A座共享办公区", floor="8F", seats=4, monthly_rent=6800, status="leased", facilities="独立储物柜,高速网络"),
            Workstation(code="A-0802", area="A座共享办公区", floor="8F", seats=2, monthly_rent=3600, status="available", facilities="高速网络"),
            Workstation(code="B-1206", area="B座景观区", floor="12F", seats=6, monthly_rent=12800, status="leased", facilities="会议屏,电话亭"),
            Workstation(code="C-0503", area="C座创意区", floor="5F", seats=3, monthly_rent=5200, status="maintenance", facilities="升降桌"),
        ]
        db.add_all(workstations)
        db.flush()

        contracts = [
            Contract(
                contract_no=f"CT-{today.strftime('%Y%m%d')}-001",
                tenant_name="星云科技有限公司",
                tenant_contact="李经理 13800000001",
                workstation_id=workstations[0].id,
                start_date=today - timedelta(days=120),
                end_date=today + timedelta(days=18),
                monthly_rent=6800,
                deposit=13600,
                status="active",
            ),
            Contract(
                contract_no=f"CT-{today.strftime('%Y%m%d')}-002",
                tenant_name="远景设计工作室",
                tenant_contact="周女士 13800000002",
                workstation_id=workstations[2].id,
                start_date=today - timedelta(days=40),
                end_date=today + timedelta(days=210),
                monthly_rent=12800,
                deposit=25600,
                status="active",
            ),
        ]
        db.add_all(contracts)
        db.flush()

        db.add_all(
            [
                Payment(contract_id=contracts[0].id, period=today.strftime("%Y-%m"), amount=6800, due_date=today - timedelta(days=5), status="overdue", note="本月租金"),
                Payment(contract_id=contracts[1].id, period=today.strftime("%Y-%m"), amount=12800, due_date=today + timedelta(days=7), status="unpaid", note="本月租金"),
                Payment(contract_id=contracts[1].id, period=(today + timedelta(days=31)).strftime("%Y-%m"), amount=12800, due_date=today + timedelta(days=37), status="unpaid", note="下月租金"),
            ]
        )
        db.commit()
