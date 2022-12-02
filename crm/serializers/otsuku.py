from rest_framework import serializers
from crm.models import Otsuku


class OtsukuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otsuku
        fields = "__all__"
        read_only_fields = [
            "id",
            "estate",
            "land",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
