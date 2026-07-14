from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional
from datetime import date

class LoanInstallmentDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdLoanInstallment: int
    IdLoan: int
    installmentNumber: int
    installmentValue: Decimal
    isPaid: bool
    commitmentDate: date
    paymentDate: Optional[date] = None

class LoanInstallmentCreateDto(BaseModel):
    installmentNumber: int
    installmentValue: Decimal
    isPaid: bool = False
    commitmentDate: date
    paymentDate: Optional[date] = None