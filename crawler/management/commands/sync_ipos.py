
import os
import logging
import json
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django_redis import get_redis_connection
from crawler.services.meroshare import MeroShare
from crawler.models import IPO
from crawler.serializers import IPOSerializer

# Configure logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrapes MeroShare for current IPOs and updates Redis cache'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting IPO refresh job...")
        
        dp_id = os.getenv("MEROSHARE_DP_ID")
        username = os.getenv("MEROSHARE_USERNAME")
        password = os.getenv("MEROSHARE_PASSWORD")

        if not all([dp_id, username, password]):
            self.stdout.write(self.style.ERROR("Missing credentials in .env"))
            return

        mero_share = MeroShare()
        try:
            mero_share.login(dp_id, username, password) # type: ignore
            issues = mero_share.get_current_issues()
            
            saved_ipos = []
            for issue in issues:
                ipo_obj, created = IPO.objects.update_or_create(
                    company_name=issue['company_name'],
                    share_group=issue['sub_group'],
                    defaults={
                        'share_type': issue['share_type']
                    }
                )
                saved_ipos.append(ipo_obj)
            
            # Serialize
            serializer = IPOSerializer(saved_ipos, many=True)
            data = serializer.data
            
            # Convert to JSON string
            json_data = json.dumps(data)
            
            # Store in Redis using raw connection to avoid Django Pickling, Ensuring go read it as plain string.
            con = get_redis_connection("default")
            # Set Key with 15 minute (900s) Expiration
            con.setex("ipo_list", 900, json_data)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(saved_ipos)} IPOs in Redis (Key: ipo_list)."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Job failed: {e}"))
        finally:
            mero_share.close()