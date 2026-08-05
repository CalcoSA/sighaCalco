from pydantic import BaseModel, ConfigDict

class LoanStatusDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    IdLoanStatus: int
    nameLoanStatus: str