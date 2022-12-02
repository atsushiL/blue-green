from rest_framework import serializers
from crm.models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]
