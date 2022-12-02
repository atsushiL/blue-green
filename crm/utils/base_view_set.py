from django.forms import model_to_dict
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from crm.permission import IsGeneralUser, IsSuperUser
from rest_framework.viewsets import ModelViewSet


# ベイスviewクラス
class BaseViewSet(ModelViewSet):

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().first()
        if queryset is None:
            return Response(data={})
        serializer = self.get_serializer(queryset)
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["created_by"] = request.user
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if partial:
            data = self.get_queryset().first()
            input_data = model_to_dict(data)
            input_data.update(request.data)
        else:
            input_data = request.data
        serializer = self.get_serializer(data=input_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["created_by"] = request.user
        self.perform_create(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

