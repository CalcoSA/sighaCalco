from app.api.typeBankAccountController import router as typeBankAccountRouter
from app.api.typeWithdrawalController import router as typeWithdrawalRouter
from app.infrastructure.logging.loggerConfig import setupLogging, getLogger
from app.api.payrollSinergyController import router as payrollSinergyRouter
from app.api.deductionPlanController import router as deductionPlanRouter
from app.api.bukEmployeeController import router as bukEmployeeRouter
from app.api.descTsueldoController import router as descTsueldoRouter
from app.api.absenteeismController import router as absenteeismRouter
from app.api.loanStatusController import router as loanStatusRouter
from app.api.incapacityController import router as incapacityRouter
from app.api.diagnosisController import router as diagnosisRouter
from app.api.descCen1Controller import router as descCen1Router
from app.api.descCen2Controller import router as descCen2Router
from app.api.descCen3Controller import router as descCen3Router
from app.api.descCen4Controller import router as descCen4Router
from app.api.exceptionHandler import registerExceptionHandlers
from app.api.loanLogController import router as loanLogRouter
from app.infrastructure.db.connection import Base, engine
from app.api.bankController import router as bankRouter
from app.api.loanController import router as loanRouter
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.db.base import Base
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from time import time
import os

load_dotenv()
setupLogging()
logger = getLogger(__name__)

#app = FastAPI(title="Assistance API", version="1.0.0", root_path="/api")
app = FastAPI(title="SighaCalco Loans API", version="1.0.0")

def getCorsOrigins() -> list[str]:
    rawOrigins = os.getenv("CORS_ALLOWED_ORIGINS", "")

    return [
        origin.strip()
        for origin in rawOrigins.split(",")
        if origin.strip()
    ]

registerExceptionHandlers(app)

@app.middleware("http")
async def logRequests(request: Request, call_next):
    startTime = time()
    try:
        response = await call_next(request)
        durationMs = round((time() - startTime) * 1000, 2)
        logger.info(
            "Request finalizado | method=%s | path=%s | status=%s | duration_ms=%s | client=%s",
            request.method,
            request.url.path,
            response.status_code,
            durationMs,
            request.client.host if request.client else "unknown"
        )
        return response
    except Exception:
        durationMs = round((time() - startTime) * 1000, 2)
        logger.exception(
            "Error no controlado en request | method=%s | path=%s | duration_ms=%s | client=%s",
            request.method,
            request.url.path,
            durationMs,
            request.client.host if request.client else "unknown"
        )
        raise

origins = getCorsOrigins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(typeBankAccountRouter)
app.include_router(typeWithdrawalRouter)
app.include_router(payrollSinergyRouter)
app.include_router(deductionPlanRouter)
app.include_router(descTsueldoRouter)
app.include_router(bukEmployeeRouter)
app.include_router(absenteeismRouter)
app.include_router(loanStatusRouter)
app.include_router(incapacityRouter)
app.include_router(diagnosisRouter)
app.include_router(descCen1Router)
app.include_router(descCen2Router)
app.include_router(descCen3Router)
app.include_router(descCen4Router)
app.include_router(loanLogRouter)
app.include_router(loanRouter)
app.include_router(bankRouter)

@app.get("/")
def root():
    logger.info("Health check ejecutado")
    return { "message": "API sighaCalco.Loans funcionando correctamente" }