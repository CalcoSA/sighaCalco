from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date

class LoanExportDto(BaseModel):
    IdLoan: int
    employeeDocumentNumber: str
    employeeFullName: str
    employeeRoleName: Optional[str] = None
    employeeCostCenterName: Optional[str] = None
    isLoan: bool
    crossDocument: Optional[str] = None
    conceptName: str
    deductionPlanName: str
    loanStatusName: str
    loanAmount: Optional[Decimal] = None
    serviceValue: Optional[Decimal] = None
    numberInstallments: Optional[int] = None
    paidInstallments: Optional[int] = None
    remainingAmount: Optional[Decimal] = None
    requestDate: date
    startDiscountDate: date
    endDiscountDate: Optional[date] = None
    installmentNumber: Optional[int] = None
    installmentValue: Optional[Decimal] = None
    isPaid: Optional[bool] = None
    commitmentDate: Optional[date] = None
    paymentDate: Optional[date] = None
    serviceDiscountValue: Optional[Decimal] = None
    serviceDiscountDate: Optional[date] = None