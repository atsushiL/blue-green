from rest_framework import serializers
from crm.models import BuildingInfo
from crm.serializers.building_info import BuildingInfoSerializer
from crm.serializers.estate import EstateSerializer
from crm.serializers.estate_certificate import EstateCertificateSerializer
from crm.serializers.pet import PetSerializer
from crm.serializers.estate_certificate import EstateCertificateSerializer
from crm.serializers.address import AddressSerializer


class BuildingSerializer(serializers.Serializer):
    estate_certificate = EstateCertificateSerializer(many=True)
    building_info = BuildingInfoSerializer()
    address = AddressSerializer()
    estate = EstateSerializer()

    def to_representation(self, instance):
        rep = {
            "building_info": BuildingInfoSerializer(instance=instance).data,
            "estate_certificate": EstateCertificateSerializer(
                instance=instance.estate.estate_certificate.all(), many=True
            ).data,
            "address": AddressSerializer(
                instance=instance.estate.address.latest("created_at")
            ).data,
            "estate": {
                "customer": instance.estate.customer.customer_data.latest(
                    "created_at"
                ).name,
                "introduction_company": instance.estate.introduction_company.name,
            },
        }
        return rep


class ListBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingInfo
        fields = "__all__"
        read_only_fields = ["id", "created_at", "created_by"]

    def to_representation(self, instance):
        data = {}
        data["building"] = super(ListBuildingSerializer, self).to_representation(
            instance
        )

        data["address"] = AddressSerializer(
            instance=instance.estate.address.latest("created_at")
        ).data

        data["pet"] = PetSerializer(
            instance=instance.estate.customer.pet.latest("created_at")
        ).data

        data["estate_certificate"] = EstateCertificateSerializer(
            instance=instance.estate.estate_certificate.all(),
            many=True,
        ).data

        return data
