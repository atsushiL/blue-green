from rest_framework import serializers
from crm.models import EvaluateCompanyEvaluations, EvaluateCompany


class EvaluateCompanyEvaluationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluateCompanyEvaluations
        fields = ["id", "estate_valuation_fee", "land_valuation_fee", "status", "memo"]
        read_only_fields = ["id", "estate", "created_by", "updated_by", "status"]

    def to_representation(self, instance):
        rep = super(EvaluateCompanyEvaluationsSerializer, self).to_representation(instance)
        rep['company_name'] = instance.evaluate_company.name
        rep['status'] = instance.Status(instance.status).name
        return rep
