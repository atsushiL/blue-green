from rest_framework import serializers
from crm.models import IntroductionCompany


class IntroductionCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = IntroductionCompany
        fields = "__all__"
        read_only_fields = ["id", "created_at", "created_by", "updated_at", "updated_by"]

    # interview_itemのモデルを取得して、created_byのフィールドを変更する
    def to_representation(self, instance):
        rep = super(IntroductionCompanySerializer, self).to_representation(instance)
        rep["created_by"] = instance.created_by.name
        rep["updated_by"] = instance.updated_by.name
        rep["introduction_count"] = instance.introduced_provisional_customer.count()
        return rep
