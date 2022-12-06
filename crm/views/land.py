from django.db import transaction
from crm.models import Land, Customer, Address, LandData, Estate
from crm.serializers.land import LandSerializer, ListLandSerializer
from crm.utils.base_view_set import BaseViewSet
from django.http import JsonResponse
from rest_framework import status
from crm.serializers.land_data import LandDataSerializer
from crm.serializers.address import AddressSerializer
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404


class LandViewSet(BaseViewSet):

    def get_queryset(self):
        estate = get_object_or_404(Estate, id=self.kwargs["estate_pk"])
        return Land.objects.filter(customer_id=estate.customer_id)

    def get_serializer_class(self):
        if self.action == "list":
            return ListLandSerializer
        else:
            return LandSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # データを受け取る
        serializer = self.get_serializer(data=request.data)
        # データを検証する。raise_exceptionはerrorメッセージを返す。
        serializer.is_valid(raise_exception=True)
        # 受け取ったデータの中からland_dataを抜き取る
        land_data = serializer.validated_data.get("land_data")
        # 受け取ったデータの中からaddressを抜き取る
        address = serializer.validated_data.get("address")

        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        customer = get_object_or_404(Customer, pk=estate.customer_id)
        # 不足しているデータを入れてLandにインサートする
        land = Land.objects.create(customer=customer, created_by=request.user)
        # land_idをaddressのland_idに入れる
        address["land_id"] = land.id
        # 担当者をland_dataの作成者に入れる
        land_data["created_by"] = request.user
        # アドレスのデータをインサートする
        address_data = Address.objects.create(**address)
        # 不足しているデータを入れる
        land_data["land_id"] = land.id
        data = {
            "land_data": LandDataSerializer(
                instance=LandData.objects.create(**land_data)
            ).data,
            "address": AddressSerializer(instance=address_data).data,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        land = get_object_or_404(Land, id=kwargs["pk"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        land_data = serializer.validated_data.get("land_data")
        address = serializer.validated_data.get("address")

        if "id" in land_data:
            land_data.pop("id")
        land_data["created_by"] = request.user
        address["land_id"] = land.id
        address_data = Address.objects.create(**address)
        land_data["land_id"] = land.id
        data = {
            "land_data": LandDataSerializer(
                instance=LandData.objects.create(**land_data)
            ).data,
            "address": AddressSerializer(instance=address_data).data,
        }
        return JsonResponse(data=data)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        land = get_object_or_404(Land, id=kwargs["pk"])
        land_data = LandData.objects.filter(land_id=land.id).latest("created_at")
        address = Address.objects.filter(land_id=land.id).latest("created_at")

        # リクエストデータのlandデータのそれぞれのアイテムをとってキーとバリューにセットしていく
        for attr, value in request.data["land_data"].items():
            setattr(land_data, attr, value)
        # リクエストデータのaddressデータのそれぞれのアイテムをとってキーとバリューにセットしていく
        for attr, value in request.data["address"].items():
            setattr(address, attr, value)

        land_data = model_to_dict(land_data)
        address = model_to_dict(address)
        input_data = {"land_data": land_data, "address": address}
        land_data.pop("land")

        serializer = self.get_serializer(data=input_data)
        serializer.is_valid(raise_exception=True)
        land_data = serializer.validated_data.get("land_data")
        address = serializer.validated_data.get("address")

        address["land_id"] = land.id
        land_data["land_id"] = land.id
        land_data["created_by"] = request.user

        if "id" in land_data:
            land_data.pop("id")
        if "id" in address:
            address.pop("id")

        data = {
            "land_data": LandDataSerializer(
                instance=LandData.objects.create(**land_data)
            ).data,
            "address": AddressSerializer(
                instance=Address.objects.create(**address)
            ).data,
        }
        return JsonResponse(data=data)
