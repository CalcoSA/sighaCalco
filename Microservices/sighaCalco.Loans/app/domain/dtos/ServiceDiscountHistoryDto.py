from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from decimal import Decimal

class ServiceDiscountHistoryDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdServiceDiscountHistory: int
    IdLoan: int
    discountValue: Decimal
    discountDate: date
    createdAt: datetime
    createdByUserName: str

class ServiceValueUpdateDto(BaseModel):
    serviceValue: Decimal = Field(..., gt=0)
    updatedByUserName: str = Field(..., min_length=1, max_length=250)