from crm.serializers.alb_anti_social_check import ALBAntiSocialCheckSerializer
from rest_framework import serializers
from crm.models import AntiSocialCheckResult, ALBAntiSocialCheck


class AntiSocialCheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntiSocialCheckResult
        fields = "__all__"
        read_only_fields = ["id", "created_at", "provisional_customer", "created_by"]

    def to_representation(self, instance):
        rep = super(AntiSocialCheckResultSerializer, self).to_representation(instance)
        rep["anti_social_check_status"] = instance.ANTI_SOCIAL_CHECK(
            instance.anti_social_check_status).name
        customer_data = instance.provisional_customer.customer.customer_data.first()
        rep = {
            "anti_social_check_result": rep,
            "alb_anti_social_check": ALBAntiSocialCheckSerializer(
                instance=ALBAntiSocialCheck.objects.filter(
                    name=customer_data.name, birthday=customer_data.birthday
                ), many=True
            ).data
        }
        return rep
