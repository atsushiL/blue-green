from crm.models import EarningsSim
from rest_framework.serializers import ModelSerializer


class EarningsSimSerializer(ModelSerializer):
    class Meta:
        model = EarningsSim
        fields = "__all__"
        read_only_fields = ["created_at", "estate", "created_by"]

    def to_representation(self, instance):
        rep = super(EarningsSimSerializer, self).to_representation(instance)
        rep["created_by"] = instance.created_by.name
        return rep
