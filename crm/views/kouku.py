from rest_framework.viewsets import ModelViewSet
from crm.permission import IsGeneralUser, IsSuperUser

from crm.serializers.kouku import KoukuSerializer
from crm.models import Kouku, Estate, Land
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse


class KoukuViewSet(ModelViewSet):
    serializer_class = KoukuSerializer

    def get_queryset(self):
        route = self.request.path.split("/")[-2]
        estate = get_object_or_404(Estate, id=self.kwargs["estate_pk"])
        if route != "estate_kouku":
            return Kouku.objects.filter(
                land_id=get_object_or_404(Land, id=estate.customer.land.id)
            )
        else:
            return Kouku.objects.filter(estate_id=estate.id)

    def create(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        # 取得したURLから土地と物件を判別
        route = request.path.split("/")[-2]

        # estateでなければlandを取得
        if route != "estate_kouku":
            land = get_object_or_404(Land, id=estate.customer.land.id)
            estate = None
        else:
            land = None

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            estate=estate, land=land, created_by=request.user, updated_by=request.user
        )

        return JsonResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        kouku = get_object_or_404(Kouku, id=kwargs["pk"])
        route = request.path.split("/")[-3]

        if (route == "land_kouku" and kouku not in estate.customer.land.kouku.all()) or (
                route == "estate_kouku" and kouku not in estate.kouku.all()):
            return HttpResponseBadRequest()

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(kouku, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_by=request.user,
        )
        return JsonResponse(data=serializer.data)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
