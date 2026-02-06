
import os
from django.apps import AppConfig

class CrawlerConfig(AppConfig):
    name = 'crawler'

    def ready(self):
        # Ensure this only run once (in the main server process, not the reloader)
        if os.environ.get('RUN_MAIN') == 'true':
            from .services.scheduler import start_scheduler
            start_scheduler()
