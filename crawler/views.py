
# Create your views here.
import os
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import IPO
from .serializers import IPOSerializer
from .scraper import MeroShare

logger = logging.getLogger(__name__)

class IPOListView(APIView):
    def get(self, request):
        dp_id = os.getenv("MEROSHARE_DP_ID")
        username = os.getenv("MEROSHARE_USERNAME")
        password = os.getenv("MEROSHARE_PASSWORD")

        if not all([dp_id, username, password]):
            return Response(
                {"error": "Missing MeroShare credentials in environment variables."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        mero_share = MeroShare()
        try:
            mero_share.login(dp_id, username, password) # type: ignore
            issues = mero_share.get_current_issues()
            
            saved_ipos = []
            for issue in issues:
                # Update or create IPO record to avoid duplicates
                ipo_obj, created = IPO.objects.update_or_create(
                    company_name=issue['company_name'],
                    share_group=issue['sub_group'], # Matching sub_group to share_group model field
                    defaults={
                        'share_type': issue['share_type']
                    }
                )
                saved_ipos.append(ipo_obj)
            
            # Serialize the updated list from DB or the scraped list
            serializer = IPOSerializer(saved_ipos, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return Response(
                {"error": f"Scraping failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            mero_share.close()