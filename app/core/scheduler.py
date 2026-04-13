from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.logger import setup_logger

logger = setup_logger(__name__)

scheduler = BackgroundScheduler()


def get_scheduler():
    """
    Dependency to get the running scheduler instance.
    """
    return scheduler


def start_scheduler():
    """
    Starts the background scheduler and adds the cleanup jobs.
    """
    if not scheduler.running:
        # Run every 1 minute
        trigger = IntervalTrigger(minutes=1)
        # Order cleanup job that runs every minute
        scheduler.add_job(
            __run_order_cleanup_job,
            trigger=trigger,
            id="order_cleanup",
            name="Cleanup expired orders",
            replace_existing=True
        )
        # Event status update job that runs every minute
        scheduler.add_job(
            __run_event_status_update_job,
            trigger=trigger,
            id="event_status_update",
            name="Update event statuses",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started with order cleanup job and event status update (interval: 1 min).")


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
    from app.api.deps import get_order_cleanup_service, get_event_repository, get_db, get_order_repository, \
        get_event_service, get_order_service, get_ticket_service, get_ticket_repository

    logger.info("Starting scheduled order cleanup job...")
    db_gen = get_db()

    db = next(db_gen)
    try:
        event_repository = get_event_repository(db)
        order_repository = get_order_repository(db)
        ticket_repository = get_ticket_repository(db)
        event_service = get_event_service(event_repository)
        ticket_service = get_ticket_service(ticket_repository, event_repository)
        order_service = get_order_service(order_repository, event_service, ticket_service)
        service = get_order_cleanup_service(db, order_service, event_service)

        service.cancel_expired_orders()
    except Exception as e:
        logger.error(f"Error during order cleanup job: {str(e)}")
    finally:
        db.close()
        logger.info("Finished scheduled order cleanup job.")


def __run_event_status_update_job():
    from app.api.deps import get_db, get_event_service, get_event_repository

    logger.info("Starting scheduled event status update job...")
    db_gen = get_db()
    db = next(db_gen)
    try:
        event_repository = get_event_repository(db)
        event_service = get_event_service(event_repository)
        event_service.update_events_status_with_scheduler()
    except Exception as e:
        logger.error(f"Error during event status update job: {str(e)}")
    finally:
        db.close()
        logger.info("Finished scheduled event status update job.")
