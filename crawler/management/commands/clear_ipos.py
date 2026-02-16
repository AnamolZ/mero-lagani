"""
Management command to remove all IPO records.

Deletes every IPO entry from the database and prints a success message
showing how many records were removed.
"""

from django.core.management.base import BaseCommand
from crawler.models import IPO


class Command(BaseCommand):
    help = "Deletes all IPOs from the local database."

    def handle(self, *args, **kwargs):
        count, _ = IPO.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {count} IPOs.")
        )