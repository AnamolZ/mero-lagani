from django.urls import path
from .views import IPOListView

"""
URL configuration for the IPO app.

Defines API endpoints for accessing IPO data.
"""

urlpatterns = [
    path("ipos/", IPOListView.as_view()),  # Endpoint to list all IPOs
]