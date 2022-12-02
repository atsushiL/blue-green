from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from crm.filters import IntroductionCompanyFilter
from django.http import JsonResponse
from rest_framework.response import Response
from crm.serializers.introduction_company import IntroductionCompanySerializer
from crm.models import IntroductionCompany
from crm.permission import IsGeneralUser, IsSuperUser


class IntroductionCompanyViewSet(ModelViewSet):
    queryset = IntroductionCompany.objects.all()
    serializer_class = IntroductionCompanySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IntroductionCompanyFilter

    def list(self, request, *args, **kwargs):
        """
        紹介会社
        - "id" : ID
        - "name" : 紹介会社名
        - "phone_no" : 電話番号
        - "created_at" : 作成日
        - "created_by" : 担当者
        """
        return super(IntroductionCompanyViewSet, self).list(
            self, request, *args, **kwargs
        )

    def create(self, request):
        serializer = IntroductionCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by_id=request.user.id,updated_by_id=request.user.id)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by_id=request.user.id)
        return JsonResponse(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
