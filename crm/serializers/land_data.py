from rest_framework import serializers
from crm.models import LandData


class LandDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandData
        fields = "__all__"
        read_only_fields = ["land", "created_by"]
