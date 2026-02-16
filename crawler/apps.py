import os
from django.apps import AppConfig

class CrawlerConfig(AppConfig):
    """
    Configuration for the 'crawler' app.

    Initializes the app and starts the scheduler when the main server process runs.
    Ensures scheduler does not start multiple times during development auto-reloads.
    """

    name = 'crawler'

    def ready(self):
        """
        Called when the Django app is ready.

        Starts the scheduler service only in the main process to avoid duplicate jobs.
        """
        if os.environ.get('RUN_MAIN') == 'true':  # Prevent running during autoreload
            from .services.scheduler import start_scheduler
            start_scheduler()  # Launch scheduled tasks