from app.domain.dtos.LoanInstallmentDto import LoanInstallmentDto, LoanInstallmentCreateDto
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

class LoanDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdLoan: int
    employeeDocumentNumber: str
    employeeFullName: str
    employeeRoleName: Optional[str] = None
    employeeCostCenterName: Optional[str] = None
    crossDocument: Optional[str] = None
    IdConcept: int
    conceptName: str
    IdDeductionPlan: int
    deductionPlanName: str
    IdLoanStatus: int
    loanStatusName: str
    loanAmount: Decimal
    numberInstallments: int
    paidInstallments: int
    remainingAmount: Decimal
    requestDate: date
    startDiscountDate: date
    endDiscountDate: Optional[date] = None
    observation: Optional[str] = None
    createdByUserName: str
    updatedByUserName: Optional[str] = None
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    loanInstallments: List[LoanInstallmentDto] = []

class LoanCreateDto(BaseModel):
    employeeDocumentNumber: str = Field(..., min_length=1, max_length=50)
    employeeFullName: str = Field(..., min_length=1, max_length=250)
    employeeRoleName: Optional[str] = Field(None, max_length=250)
    employeeCostCenterName: Optional[str] = Field(None, max_length=250)
    crossDocument: Optional[str] = Field(None, max_length=100)
    IdConcept: int
    conceptName: str = Field(..., min_length=1, max_length=250)
    IdDeductionPlan: int
    deductionPlanName: str = Field(..., min_length=1, max_length=150)
    IdLoanStatus: int
    loanStatusName: str = Field(..., min_length=1, max_length=100)
    loanAmount: Decimal
    numberInstallments: int
    requestDate: date
    startDiscountDate: date
    endDiscountDate: Optional[date] = None
    observation: Optional[str] = None
    createdByUserName: str = Field(..., min_length=1, max_length=250)
    loanInstallments: List[LoanInstallmentCreateDto]