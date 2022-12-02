from rest_framework import serializers
from crm.models import PromotionMethod


class PromotionMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionMethod
        fields = [
            "id",
            "method",
            "created_at",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by"]

    # interview_itemのモデルを取得して、created_byのフィールドを変更する
    def to_representation(self, instance):
        rep = super(PromotionMethodSerializer, self).to_representation(instance)
        rep["created_by"] = instance.created_by.name
        return rep
