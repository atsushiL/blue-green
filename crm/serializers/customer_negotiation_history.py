from rest_framework import serializers
from django.utils import timezone

from crm.models import (
    CustomerNegotiationHistory,
)


class CustomerNegotiationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNegotiationHistory
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class ListCustomerNegotiationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNegotiationHistory
        fields = ["id", "negotiation_datetime", "conversation"]

    def to_representation(self, instance):
        rep = super(ListCustomerNegotiationHistorySerializer, self).to_representation(
            instance
        )
        # 交渉日時,交渉結果,交渉方法,交渉内容
        rep["negotiation_datetime"] = timezone.localtime(
            instance.negotiation_datetime).strftime("%Y-%m-%d %H:%M")
        rep["promotion_method"] = instance.promotion_method.method
        rep["result"] = instance.result.result
        rep["created_by"] = instance.created_by.name
        return rep


class CreateCustomerNegotiationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNegotiationHistory
        fields = "__all__"
        read_only_fields = [
            "id",
            "customer",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
