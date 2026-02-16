from rest_framework import serializers
from .models import IPO

class IPOSerializer(serializers.ModelSerializer):
    """
    Serializer for the IPO model.

    Converts IPO model instances to JSON and validates incoming data
    for API endpoints.
    """

    class Meta:
        model = IPO  # The model to serialize
        fields = '__all__'  # Include all fields from the IPO model