from crm.serializers.evaluation_result import EvaluationResultSerializer
from rest_framework import serializers
from crm.models import PurchaseSurvey, EvaluationResult


class PurchaseSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSurvey
        fields = "__all__"
        read_only_fields = ["estate", "created_at", "created_by"]

    def to_representation(self, instance):
        rep = super(PurchaseSurveySerializer, self).to_representation(instance)
        rep = {
            "purchase_survey": rep,
            "evaluation_result": EvaluationResultSerializer(
                instance=EvaluationResult.objects.filter(
                    estate_id=rep["estate"]
                ), many=True
            ).data
        }
        return rep
