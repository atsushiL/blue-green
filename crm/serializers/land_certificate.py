from rest_framework import serializers
from crm.models import LandCertificate


class LandCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandCertificate
        fields = "__all__"
        read_only_fields = [
            "land",
            "created_at",
            "created_by",
        ]
