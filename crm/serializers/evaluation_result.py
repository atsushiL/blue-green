from rest_framework.serializers import ModelSerializer
from crm.models import EvaluationResult


class EvaluationResultSerializer(ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = "__all__"
        read_only_fields = ["estate", "created_by", "created_at",
                            "updated_by", "updated_at"]

    def to_representation(self, instance):
        rep = super(EvaluationResultSerializer, self).to_representation(instance)
        rep["standard"] = instance.evaluation_standard.standard
        rep["standard_content"] = instance.evaluation_standard.standard_content
        return rep
