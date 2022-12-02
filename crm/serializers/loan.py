from rest_framework import serializers
from crm.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]
