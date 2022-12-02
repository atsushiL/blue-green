from rest_framework import serializers
from crm.models import EvaluateCompany, EvaluateCompanyEvaluations


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluateCompanyEvaluations
        fields = "__all__"
        read_only_fields = ["id", "estate", "created_at", "created_by"]

    def to_representation(self, instance):
        rep = super(EvaluationSerializer, self).to_representation(instance)
        evaluate_company = EvaluateCompany.objects.get(id=instance.evaluate_company_id)
        rep["name"] = evaluate_company.name
        rep["total_valuation_fee"] = (
            instance.estate_valuation_fee + instance.land_valuation_fee
        )
        return rep
