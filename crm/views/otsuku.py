from rest_framework.viewsets import ModelViewSet
from crm.permission import IsGeneralUser, IsSuperUser

from crm.serializers.otsuku import OtsukuSerializer
from crm.models import Otsuku, Estate, Land
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse


class OtsukuViewSet(ModelViewSet):
    serializer_class = OtsukuSerializer

    def get_queryset(self):
        route = self.request.path.split("/")[-2]
        estate = get_object_or_404(Estate, id=self.kwargs["estate_pk"])
        if route != "estate_otsuku":
            return Otsuku.objects.filter(
                land_id=get_object_or_404(Land, id=estate.customer.land.id)
            )
        else:
            return Otsuku.objects.filter(estate_id=estate.id)

    def create(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        # 取得したURLから土地と物件を判別
        route = request.path.split("/")[-2]
        # 乙区は二つのテーブルに紐づくことはできないのでデータを整形する。
        if route != "estate_otsuku":
            land = get_object_or_404(Land, id=estate.customer.land.id)
            estate = None
        else:
            land = None

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # saveはオブジェクトがなければ作成して、あれば更新する。
        serializer.save(
            estate=estate, land=land, created_by=request.user, updated_by=request.user
        )

        return JsonResponse(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        estate = get_object_or_404(Estate, id=kwargs["estate_pk"])
        otsuku = get_object_or_404(Otsuku, id=kwargs["pk"])
        route = request.path.split("/")[-3]
        if (route == "land_otsuku" and otsuku not in estate.customer.land.otsuku.all()) or (
                route == "estate_otsuku" and otsuku not in estate.otsuku.all()):
            return HttpResponseBadRequest()
        partial = kwargs.pop("partial", False)
        # get_serializerでotsukuにrequest.dataを入れる
        serializer = self.get_serializer(otsuku, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # オブジェクトを更新する
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
