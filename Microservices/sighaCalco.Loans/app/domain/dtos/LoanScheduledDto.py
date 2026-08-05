from pydantic import BaseModel, Field
from datetime import date

class LoanScheduledDto(BaseModel):
    executionDate: date
    cycleName: str
    targetInstallmentDate: date
    reviewedLoans: int = 0
    activatedLoans: int = 0
    paidInstallments: int = 0
    finishedLoans: int = 0
    skippedLoans: int = 0
    failedLoans: int = 0
    processedLoanIds: list[int] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)