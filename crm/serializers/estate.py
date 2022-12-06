from rest_framework import serializers
from crm.models import Estate


class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = "__all__"
        read_only_fields = [
            "id",
            "introduction_company",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

    # interview_itemのモデルを取得して、created_byのフィールドを変更する
    def to_representation(self, instance):
        # オブジェクトを全て取得する。
        rep = super(EstateSerializer, self).to_representation(instance)
        customer_data = instance.customer.customer_data.latest("created_at")
        provisional_customer_data = (
            instance.customer.provisional_customer.provisional_customer_data.latest(
                "created_at"
            )
        )
        # 買取確認を取得
        if instance.purchase_survey.exists():
            purchase_survey = instance.purchase_survey.latest("created_at")
            rep["status"] = purchase_survey.result
        else:
            rep["status"] = []

        # 申込日を取得
        rep["application_date"] = provisional_customer_data.application_date
        # 申込者を取得
        rep["provisional_customers_name"] = customer_data.name
        # 買取進捗
        rep["evaluation_progress"] = str(instance.evaluation_result.exclude(
            evaluation_judge=None).count()) + "/" + str(instance.evaluation_result.count())
        # 買取調査結果を取得
        rep["evaluation_result"] = instance.purchase_survey.first().result

        return rep
