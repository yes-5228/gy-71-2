from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_workstations: int
    available_workstations: int
    leased_workstations: int
    active_contracts: int
    unpaid_amount: float
    overdue_amount: float
    expiring_contracts: int
