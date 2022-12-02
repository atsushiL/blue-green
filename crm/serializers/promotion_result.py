from rest_framework import serializers
from crm.models import PromotionResult


class PromotionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionResult
        fields = [
            "id",
            "result",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    # interview_itemのモデルを取得して、created_byのフィールドを変更する
    def to_representation(self, instance):
        rep = super(PromotionResultSerializer, self).to_representation(instance)
        rep["created_by"] = instance.created_by.name
        return rep
