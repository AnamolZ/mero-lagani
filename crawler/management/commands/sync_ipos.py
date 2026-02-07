
import os
import logging
import json
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django_redis import get_redis_connection
from crawler.services.meroshare import MeroShare
from crawler.services.email_service import EmailService
from crawler.models import IPO
from crawler.serializers import IPOSerializer

# Configure logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrapes MeroShare for current IPOs, updates Redis cache, and notifies users of new opportunities.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting IPO refresh job...")
        
        dp_id = os.getenv("MEROSHARE_DP_ID")
        username = os.getenv("MEROSHARE_USERNAME")
        password = os.getenv("MEROSHARE_PASSWORD")

        if not all([dp_id, username, password]):
            self.stdout.write(self.style.ERROR("Missing credentials in .env"))
            return

        mero_share = MeroShare()
        email_service = EmailService()
        recipients = ["anmoldkl971@gmail.com", "danamol22@tbc.edu.np"]

        try:
            mero_share.login(dp_id, username, password) # type: ignore
            issues = mero_share.get_current_issues()
            
            saved_ipos = []
            new_ipos = []

            for issue in issues:
                ipo_obj, created = IPO.objects.update_or_create(
                    company_name=issue['company_name'],
                    share_group=issue['sub_group'],
                    defaults={
                        'share_type': issue['share_type']
                    }
                )
                saved_ipos.append(ipo_obj)
                
                if created:
                    new_ipos.append(ipo_obj)
            
            # Serialize for Cache
            serializer = IPOSerializer(saved_ipos, many=True)
            data = serializer.data
            
            # Convert to JSON string
            json_data = json.dumps(data)
            
            # Store in Redis
            try:
                con = get_redis_connection("default")
                # Set Key with 65 minute (3900s) Expiration to allow buffer for 60m scheduler
                con.setex("ipo_list", 3900, json_data)
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(saved_ipos)} IPOs in Redis."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to connect to Redis: {e}"))

            # Send Notifications if new IPOs found
            if new_ipos:
                self.stdout.write(self.style.SUCCESS(f"Found {len(new_ipos)} new IPOs. Sending notifications..."))
                email_sent = email_service.send_ipo_notification(recipients, new_ipos)
                if email_sent:
                    self.stdout.write(self.style.SUCCESS("Notification emails sent successfully."))
                else:
                    self.stdout.write(self.style.WARNING("Failed to send notification emails."))
            else:
                self.stdout.write("No new IPOs detected.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Job failed: {e}"))
        finally:
            mero_share.close()