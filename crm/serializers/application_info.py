from rest_framework import serializers
from crm.models import ApplicationInfo, ProvisionalCustomer


class ApplicationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationInfo
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]

    def to_representation(self, instance):
        rep = super(ApplicationInfoSerializer, self).to_representation(instance)
        rep["introduction_company"] = instance.provisional_customer.introduction_company.name
        return rep


class IntroductionCompanyIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalCustomer
        fields = ["introduction_company"]
