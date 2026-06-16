from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contract_no: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    tenant_name: Mapped[str] = mapped_column(String(80), index=True)
    tenant_contact: Mapped[str] = mapped_column(String(80), default="")
    workstation_id: Mapped[int] = mapped_column(ForeignKey("workstations.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date, index=True)
    monthly_rent: Mapped[float] = mapped_column(Numeric(10, 2))
    deposit: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    signed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workstation = relationship("Workstation", back_populates="contracts")
    payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")
