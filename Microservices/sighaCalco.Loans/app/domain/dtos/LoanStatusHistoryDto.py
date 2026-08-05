from app.domain.dtos.LoanStatusDto import LoanStatusDto
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LoanStatusHistoryDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdLoanStatusHistory: int
    IdLoan: int
    IdLoanStatus: int
    observation: str
    createdAt: datetime
    createdByUserName: str
    loanStatus: LoanStatusDto