
# Create your views here.
import os
import logging
import json
from django.core.cache import cache
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import IPO
from .serializers import IPOSerializer
from .services.meroshare import MeroShare

logger = logging.getLogger(__name__)

class IPOListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        logger.info(f"Admin {request.user} triggered force IPO refresh.")

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
                ipo_obj, created = IPO.objects.update_or_create(
                    company_name=issue['company_name'],
                    share_group=issue['sub_group'],
                    defaults={
                        'share_type': issue['share_type']
                    }
                )
                saved_ipos.append(ipo_obj)
            
            serializer = IPOSerializer(saved_ipos, many=True)
            data = serializer.data
            
            # Store as JSON string for Go compatibility
            json_data = json.dumps(data)
            con = get_redis_connection("default")
            con.set("ipo_list", json_data)
            
            logger.info("Admin refresh complete. Cache updated.")
            return Response({"message": "Refreshed successfully", "data": data})

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return Response(
                {"error": f"Scraping failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            mero_share.close()