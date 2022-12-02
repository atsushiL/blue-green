from rest_framework import serializers
from crm.models import EstateCertificate


class EstateCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateCertificate
        fields = "__all__"
        read_only_fields = [
            "estate",
            "updated_by",
            "updated_at",
            "created_at",
            "created_by",
        ]
