from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.deps import get_order_cleanup_service, get_event_repository, get_db, get_order_repository, \
    get_event_service, get_order_service
from app.core.logger import setup_logger

logger = setup_logger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Starts the background scheduler and adds the cleanup job.
    """
    if not scheduler.running:
        # Run every 1 minute
        trigger = IntervalTrigger(minutes=1)

        scheduler.add_job(
            __run_order_cleanup_job,
            trigger=trigger,
            id="order_cleanup",
            name="Cleanup expired orders",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started with order cleanup job (interval: 1 min).")


def stop_scheduler():
    """
    Shuts down the scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")


def __run_order_cleanup_job():
    """
    Job function that creates a new DB session, runs the cleanup service,
    and then closes the session.
    """
    logger.info("Starting scheduled order cleanup job...")
    db_gen = get_db()

    db = next(db_gen)
    try:
        event_repository = get_event_repository(db)
        order_repository = get_order_repository(db)
        event_service = get_event_service(event_repository)
        order_service = get_order_service(order_repository, event_service)
        service = get_order_cleanup_service(db, order_service, event_service)

        service.cancel_expired_orders()
    except Exception as e:
        logger.error(f"Error during order cleanup job: {str(e)}")
    finally:
        db.close()
        logger.info("Finished scheduled order cleanup job.")
