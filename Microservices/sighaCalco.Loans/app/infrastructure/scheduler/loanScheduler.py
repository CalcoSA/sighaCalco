from app.infrastructure.repositories.LoanLogRepository import LoanLogRepository
from app.infrastructure.repositories.LoanRepository import LoanRepository
from app.application.services.LoanApplication import LoanApplication
from apscheduler.schedulers.background import BackgroundScheduler
from app.infrastructure.logging.loggerConfig import getLogger
from app.infrastructure.db.connection import getDb
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo

logger = getLogger(__name__)
scheduler = BackgroundScheduler(timezone=ZoneInfo("America/Bogota"))

def executeLoanScheduled() -> None:
    dbGenerator = getDb()
    db = next(dbGenerator)

    try:
        loanRepository = LoanRepository(db)
        loanLogRepository = LoanLogRepository(db)
        service = LoanApplication(loanRepository=loanRepository, loanLogRepository=loanLogRepository,)
        result = service.processScheduledLoans(actorUserName="TAREA_PROGRAMADA")

        logger.info(
            "Tarea programada de préstamos finalizada "
            "| executionDate=%s "
            "| cycleName=%s "
            "| targetInstallmentDate=%s "
            "| reviewedLoans=%s "
            "| activatedLoans=%s "
            "| paidInstallments=%s "
            "| finishedLoans=%s "
            "| skippedLoans=%s "
            "| failedLoans=%s",
            result.executionDate,
            result.cycleName,
            result.targetInstallmentDate,
            result.reviewedLoans,
            result.activatedLoans,
            result.paidInstallments,
            result.finishedLoans,
            result.skippedLoans,
            result.failedLoans,
        )

        if result.errors:
            logger.warning("La tarea programada terminó con errores " "| errors=%s", result.errors,)

    except Exception:
        db.rollback()
        logger.exception("Error ejecutando la tarea programada " "de préstamos.")

    finally:
        dbGenerator.close()

def configureLoanScheduler() -> None:
    scheduler.add_job(
        func=executeLoanScheduled,
        trigger=CronTrigger(day="10,20", hour=5, minute=0, second=0, timezone=ZoneInfo("America/Bogota"),),
        id="loan-scheduled-process",
        name="Proceso quincenal de préstamos",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )