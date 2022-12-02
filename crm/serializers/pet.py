from rest_framework import serializers
from crm.models import Pet


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
