
import time
import threading
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

REFRESH_INTERVAL_SECONDS = 14 * 60  # 14 Minutes

def run_loop():
    logger.info("Initializing IPO Cache Heartbeat Scheduler (Threaded)...")
    logger.info(f"Schedule: Run every {REFRESH_INTERVAL_SECONDS/60} minutes.")
    
    while True:
        try:
            logger.info("Triggering background sync (call_command 'sync_ipos')...")
            call_command('sync_ipos')
            logger.info("Sync command completed successfully.")

        except Exception as e:
            logger.error(f"Unexpected error in background scheduler: {e}")

        logger.info(f"Scheduler sleeping for {REFRESH_INTERVAL_SECONDS} seconds...")
        time.sleep(REFRESH_INTERVAL_SECONDS)

def start_scheduler():
    scheduler_thread = threading.Thread(target=run_loop, daemon=True)
    scheduler_thread.start()