from rest_framework import serializers
from crm.models import Family


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]
