from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LoanLogDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdLoanLog: int
    actionType: str
    IdLoan: Optional[int] = None
    IdLoanInstallment: Optional[int] = None
    installmentNumber: Optional[int] = None
    employeeDocumentNumber: Optional[str] = None
    conceptName: Optional[str] = None
    loanStatusName: Optional[str] = None
    installmentStatusName: Optional[str] = None
    observation: Optional[str] = None
    actorUserName: Optional[str] = None
    actionDate: datetime