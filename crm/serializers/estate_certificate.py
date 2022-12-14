from rest_framework import serializers
from crm.models import EstateCertificate


class EstateCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateCertificate
        fields = "__all__"
        read_only_fields = [
            "estate",
            "created_at",
            "created_by",
        ]
