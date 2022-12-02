from rest_framework import serializers
from crm.models import Kouku


class KoukuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kouku
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
