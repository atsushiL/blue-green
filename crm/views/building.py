from rest_framework.viewsets import ModelViewSet
from crm.permission import IsGeneralUser, IsSuperUser

from crm.serializers.building import (
    ListBuildingSerializer,
    BuildingSerializer,
)
from crm.models import (
    Estate,
    BuildingInfo,
    EstateCertificate,
    Address,
)
from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from crm.serializers.building_info import BuildingInfoSerializer
from crm.serializers.estate_certificate import EstateCertificateSerializer
from crm.serializers.address import AddressSerializer
from django.forms import model_to_dict


class BuildingViewSet(ModelViewSet):
    def get_queryset(self):
        return BuildingInfo.objects.filter(estate_id=self.kwargs["estate_pk"])

    def get_serializer_class(self):
        if self.action == "list":
            return ListBuildingSerializer
        else:
            return BuildingSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        building_info_data = serializer.validated_data.get("building_info")
        estate_certificate_data = serializer.validated_data.get("estate_certificate")
        address_data = serializer.validated_data.get("address")
        estate_data = serializer.validated_data.get("estate")

        if "id" in building_info_data:
            building_info_data.pop("id")
        if "id" in address_data:
            address_data.pop("id")

        for attr, value in estate_data.items():
            setattr(estate, attr, value)
        estate.updated_at = request.user
        estate.save()

        building_info = BuildingInfo.objects.create(
            estate_id=estate.id, created_by=request.user, **building_info_data
        )

        estate_certificate = []
        for certificate in estate_certificate_data:
            c = EstateCertificate.objects.create(estate_id=estate.id, **certificate)
            estate_certificate.append(c)

        address = Address.objects.create(estate_id=estate.id, **address_data)

        data = {
            "building_info": BuildingInfoSerializer(instance=building_info).data,
            "estate_certificate": EstateCertificateSerializer(
                instance=estate_certificate,
                many=True,
            ).data,
            "address": AddressSerializer(instance=address).data,
        }
        return JsonResponse(data=data)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        building_info_data = BuildingInfo.objects.filter(estate_id=estate.id).latest(
            "created_at"
        )
        address_data = Address.objects.filter(estate_id=estate.id).latest("created_at")

        for attr, value in request.data["building_info"].items():
            setattr(building_info_data, attr, value)
        for attr, value in request.data["address"].items():
            setattr(address_data, attr, value)
        for attr, value in request.data["estate"].items():
            setattr(estate, attr, value)

        building_info = model_to_dict(building_info_data)
        address = model_to_dict(address_data)
        estate_certificate = request.data["estate_certificate"]
        estate_dict = model_to_dict(estate)

        input_data = {
            "building_info": building_info,
            "estate_certificate": estate_certificate,
            "address": address,
            "estate": estate_dict,
        }

        serializer = self.get_serializer(data=input_data)
        serializer.is_valid(raise_exception=True)
        building_info = serializer.validated_data.get("building_info")
        estate_certificate = serializer.validated_data.get("estate_certificate")
        address = serializer.validated_data.get("address")

        building_info["estate_id"] = estate.id
        address["estate_id"] = estate.id

        estate.updated_by = request.user
        estate.save()

        if "id" in building_info:
            building_info.pop("id")
        if "id" in address:
            address.pop("id")

        new_estate_certificate = []
        for certificate in estate_certificate:
            c = EstateCertificate.objects.create(estate_id=estate.id, **certificate)
            new_estate_certificate.append(c)

        data = {
            "building_info": BuildingInfoSerializer(
                instance=BuildingInfo.objects.create(
                    created_by=request.user, **building_info
                )
            ).data,
            "estate_certificate": EstateCertificateSerializer(
                instance=new_estate_certificate, many=True
            ).data,
            "address": AddressSerializer(
                instance=Address.objects.create(**address)
            ).data,
        }
        return JsonResponse(data=data)

    def get_permissions(self):
        if self.action == "destroy" or self.action == "create":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
