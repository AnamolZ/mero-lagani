"""
Celery application configuration for the Django project.

Initializes the Celery app, loads Django settings, auto-discovers tasks,
and provides a simple debug task for inspection.
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("mero_lagani")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")