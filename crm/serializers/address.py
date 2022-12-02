from rest_framework.serializers import ModelSerializer
from crm.models import Address


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["id", "created_at", "customer", "estate", "land"]
