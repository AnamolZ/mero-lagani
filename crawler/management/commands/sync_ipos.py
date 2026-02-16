"""
IPO Synchronization Command

Coordinates the IPO refresh workflow:
- Authenticates with MeroShare
- Scrapes current IPO issues
- Updates Redis cache for API consumption
- Detects newly listed IPOs
- Dispatches asynchronous email notifications
"""

import os
import logging
import json
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection
from crawler.services.meroshare import MeroShare
from crawler.services.email_service import EmailService
from crawler.models import IPO

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scrapes MeroShare, refreshes Redis cache, and triggers notifications."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting IPO refresh job...")

        dp_id = os.getenv("MEROSHARE_DP_ID")
        username = os.getenv("MEROSHARE_USERNAME")
        password = os.getenv("MEROSHARE_PASSWORD")

        if not all([dp_id, username, password]):
            self.stdout.write(self.style.ERROR("Missing credentials in environment"))
            return

        mero_share = MeroShare()
        email_service = EmailService()
        recipients = [
            "anmoldkl971@gmail.com",
            "danamol22@tbc.edu.np",
        ]

        try:
            mero_share.login(dp_id, username, password)  # type: ignore
            issues = mero_share.get_current_issues()

            try:
                redis_conn = get_redis_connection("default")
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f"Redis connection failed: {exc}")
                )
                return

            saved_ipos = []
            new_ipos = []

            for issue in issues:
                identifier = f"{issue['company_name']}:{issue['sub_group']}"

                if not redis_conn.sismember("seen_ipos", identifier):
                    new_ipos.append(issue)
                    redis_conn.sadd("seen_ipos", identifier)

                saved_ipos.append(issue)

                try:
                    IPO.objects.update_or_create(
                        company_name=issue["company_name"],
                        share_group=issue["sub_group"],
                        defaults={"share_type": issue["share_type"]},
                    )
                except Exception as db_exc:
                    logger.warning(f"Database sync failed: {db_exc}")

            json_data = json.dumps(saved_ipos)

            try:
                redis_conn.setex("ipo_list", 3900, json_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {len(saved_ipos)} IPOs in Redis cache."
                    )
                )
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Redis update failed: {exc}"))

            if new_ipos:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Detected {len(new_ipos)} new IPOs. Queueing notifications..."
                    )
                )

                from crawler.tasks import send_ipo_email_task

                send_ipo_email_task.delay(recipients, new_ipos)

                self.stdout.write(
                    self.style.SUCCESS("Notification task queued.")
                )
            else:
                self.stdout.write("No new IPOs detected.")

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Job failed: {exc}"))
            logger.exception("IPO sync job failed")

        finally:
            mero_share.close()