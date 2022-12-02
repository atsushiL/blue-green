from rest_framework import serializers
from crm.models import EvaluateCompany


class EvaluateCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluateCompany
        fields = "__all__"
        read_only_fields = ["id", "created_at", "created_by"]

    # interview_itemのモデルを取得して、created_byのフィールドを変更する
    def to_representation(self, instance):
        rep = super(EvaluateCompanySerializer, self).to_representation(instance)
        rep["created_by"] = instance.created_by.name
        return rep
