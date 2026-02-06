from django.urls import path
from .views import IPOListView

urlpatterns = [
    path("ipos/", IPOListView.as_view()),
]