from rest_framework import serializers
from crm.models import WorkplaceInfo


class WorkplaceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkplaceInfo
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]
