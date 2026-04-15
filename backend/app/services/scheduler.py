import logging
from datetime import date, timedelta, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from app.services.database import engine
from app.models import SchedulerRun
from app.crud import tracking_item as tracking_item_crud, otp as otp_crud
from app.notifications import get_notification_service
from app.services.settings import settings


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)


def get_last_run_time(session: Session, job_name: str) -> datetime | None:
    statement = select(SchedulerRun).where(SchedulerRun.job_name == job_name)
    scheduler_run = session.exec(statement).first()
    return scheduler_run.last_run_at if scheduler_run else None


def save_last_run_time(session: Session, job_name: str, run_time: datetime):
    statement = select(SchedulerRun).where(SchedulerRun.job_name == job_name)
    scheduler_run = session.exec(statement).first()

    if scheduler_run:
        # Update existing record
        scheduler_run.last_run_at = run_time
        scheduler_run.updated_at = datetime.now()
    else:
        # Create new record
        scheduler_run = SchedulerRun(
            job_name=job_name,
            last_run_at=run_time
        )
        session.add(scheduler_run)

    session.commit()


def should_run_on_startup(session: Session, job_name: str, next_run_hour: int) -> bool:
    """Check if a job should run on startup.

    Returns True if:
    - Job has never run before, OR
    - Last run was before today's scheduled time, AND
    - Next scheduled run is more than 1-2 hours away
    """
    last_run = get_last_run_time(session, job_name)

    # If job has never run, run it
    if last_run is None:
        return True

    try:
        now = datetime.now()

        # Calculate today's scheduled run time
        today_scheduled = now.replace(hour=next_run_hour, minute=0, second=0, microsecond=0)

        # If we're past today's scheduled time and job hasn't run today, run it
        if now > today_scheduled and last_run < today_scheduled:
            return True

        # If we're before today's scheduled time, check if it's more than 2 hours away
        if now < today_scheduled:
            hours_until_next_run = (today_scheduled - now).total_seconds() / 3600
            # If last run was yesterday or earlier, and next run is >2 hours away
            if last_run.date() < now.date() and hours_until_next_run > 2:
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking last run time for {job_name}: {e}")
        return False


async def check_reminders_and_send_notifications() -> None:
    """Daily job to check reminders and send notifications.
    """
    logger.info(f"Running reminder check at {datetime.now()}")

    with Session(engine) as session:
        items_due_today = tracking_item_crud.get_items_due_today(session)

        if not items_due_today:
            logger.info("No reminders due today")
            save_last_run_time(session, 'check_reminders', datetime.now())
            return
        logger.info(f"Found {len(items_due_today)} item(s) due today")

        # Send notifications
        #! restructure it to send batch notification
        notification_service = get_notification_service(settings.NOTIFICATION_MODE) # type: ignore
        # notification_service.send_batch_reminders()
        for item in items_due_today:
            user_email = item.user.email if item.user else None
            if not user_email:
                continue
            try:
                logger.debug(f"Sending reminder to {user_email} for {item.title}")
                notification_service.send_reminder(user_email, item)
                tracking_item_crud.mark_item_done(session, item.id) # type: ignore
                logger.debug("Reminder sent")
            except Exception as e:
                logger.error(f"Failed for {e}")

        logger.info(f"Reminder job completed: {len(items_due_today)} reminders processed")
        save_last_run_time(session, 'check_reminders', datetime.now())


async def cleanup_old_records():
    """Daily job to cleanup old tracking items (older than 180 days).
    """
    logger.info(f"Running old records cleanup at {datetime.now()}")

    with Session(engine) as session:
        cutoff_date = date.today() - timedelta(days=180)
        deleted_count = tracking_item_crud.delete_old_records(session, cutoff_date)

        logger.info(f"Cleanup job completed: {deleted_count} old record(s) deleted (older than {cutoff_date})")
        save_last_run_time(session, 'cleanup_old_records', datetime.now())


async def cleanup_expired_otps():
    logger.info(f"Running OTP cleanup at {datetime.now()}")

    with Session(engine) as session:
        deleted_count = otp_crud.cleanup_expired_otps(session)
        logger.info(f"OTP cleanup completed: {deleted_count} expired OTP(s) deleted")
        save_last_run_time(session, 'cleanup_expired_otps', datetime.now())


async def run_startup_jobs():
    """Run jobs on startup if they haven't run recently."""
    logger.info("Checking if any jobs need to run on startup...")

    with Session(engine) as session:
        if should_run_on_startup(session, 'check_reminders', 8):
            logger.info("[STARTUP] Running check_reminders job (missed or not run recently)")
            await check_reminders_and_send_notifications()
        else:
            logger.info("[STARTUP] check_reminders job: Up to date, skipping")

        if should_run_on_startup(session, 'cleanup_old_records', 2):
            logger.info("[STARTUP] Running cleanup_old_records job (missed or not run recently)")
            await cleanup_old_records()
        else:
            logger.info("[STARTUP] cleanup_old_records job: Up to date, skipping")

        # Always run OTP cleanup on startup (it's safe and quick)
        logger.info("Running cleanup_expired_otps job (runs on every startup)")
        await cleanup_expired_otps()

    logger.info("Startup jobs check completed")


def start_scheduler():
    # Check reminders at 8 AM SCHEDULER_TIMEZONE (daily)
    scheduler.add_job(
        check_reminders_and_send_notifications,
        trigger=CronTrigger(hour=8, minute=0, timezone=settings.SCHEDULER_TIMEZONE),
        id='check_reminders',
        name='Check reminders at 8 AM SCHEDULER_TIMEZONE',
        replace_existing=True
    )

    # Cleanup old records at 2 AM SCHEDULER_TIMEZONE (daily)
    scheduler.add_job(
        cleanup_old_records,
        trigger=CronTrigger(hour=2, minute=0, timezone=settings.SCHEDULER_TIMEZONE),
        id='cleanup_old_records',
        name='Cleanup old records at 2 AM SCHEDULER_TIMEZONE',
        replace_existing=True
    )

    # Cleanup expired OTPs (every hour)
    scheduler.add_job(
        cleanup_expired_otps,
        trigger=CronTrigger(minute=0, timezone=settings.SCHEDULER_TIMEZONE),
        id='cleanup_expired_otps',
        name='Cleanup expired OTPs every hour',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started successfully - Timezone: {settings.SCHEDULER_TIMEZONE}")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped successfully.")
