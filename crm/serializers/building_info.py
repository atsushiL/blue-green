from rest_framework import serializers
from crm.models import BuildingInfo


class BuildingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingInfo
        fields = "__all__"
        read_only_fields = ["estate", "created_at", "created_by"]
