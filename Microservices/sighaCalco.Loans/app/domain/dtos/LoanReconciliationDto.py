from datetime import date
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional

class LoanReconciliationItemDto(BaseModel):
    status: str
    fileDocumentNumber: Optional[str] = None
    fileFullName: Optional[str] = None
    fileAmount: Optional[Decimal] = None
    IdLoan: Optional[int] = None
    isLoan: Optional[bool] = None
    sighaDocumentNumber: Optional[str] = None
    sighaFullName: Optional[str] = None
    conceptName: Optional[str] = None
    lastDiscountDate: Optional[date] = None
    sighaAmount: Optional[Decimal] = None
    difference: Optional[Decimal] = None

class LoanReconciliationGroupDto(BaseModel):
    conceptName: str
    total: int = 0
    equals: int = 0
    different: int = 0
    notInFile: int = 0
    notInSigha: int = 0
    items: List[LoanReconciliationItemDto]

class LoanReconciliationResultDto(BaseModel):
    total: int = 0
    equals: int = 0
    different: int = 0
    notInFile: int = 0
    notInSigha: int = 0
    groups: List[LoanReconciliationGroupDto]