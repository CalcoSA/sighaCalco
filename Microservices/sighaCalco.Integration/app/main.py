from app.infrastructure.logging.loggerConfig import setupLogging, getLogger
from app.api.exceptionHandler import registerExceptionHandlers
from app.api.fileController import router as FileRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from time import time
import os

load_dotenv()
setupLogging()
logger = getLogger(__name__)

#app = FastAPI(title="Assistance API", version="1.0.0", root_path="/api")
app = FastAPI(title="SighaCalco Integration API", version="1.0.0")

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

app.include_router(FileRouter)

@app.get("/")
def root():
    logger.info("Health check ejecutado")
    return { "message": "API sighaCalco.Integration funcionando correctamente" }