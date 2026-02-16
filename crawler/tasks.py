from celery import shared_task
from celery.utils.log import get_task_logger
from .services.email_service import EmailService

logger = get_task_logger(__name__)

@shared_task
def send_ipo_email_task(recipients, new_ipos):
    """
    Celery task to send IPO email notifications asynchronously.

    This task is triggered by the sync_ipos command when new IPOs are detected.
    It uses the EmailService to dispatch emails to the provided recipients.

    Args:
        recipients (list): List of email addresses.
        new_ipos (list): List of new IPO dictionaries.
    """
    logger.info(f"Starting email task for {len(new_ipos)} new IPOs to {len(recipients)} recipients.")
    
    email_service = EmailService()
    success = email_service.send_ipo_notification(recipients, new_ipos)
    
    if success:
        logger.info("Email task completed successfully.")
        return "Emails sent successfully."
    else:
        logger.warning("Email task finished but reported failure in sending.")
        return "Emails failed to send."
