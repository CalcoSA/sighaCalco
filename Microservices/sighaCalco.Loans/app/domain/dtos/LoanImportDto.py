from pydantic import BaseModel

class LoanImportResultDto(BaseModel):
    totalRows: int
    loansCreated: int
    servicesCreated: int
    installmentsCreated: int