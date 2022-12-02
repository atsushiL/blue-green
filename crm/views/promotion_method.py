from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse

from crm.serializers.promotion_method import PromotionMethodSerializer
from crm.models import PromotionMethod
from crm.permission import IsGeneralUser, IsSuperUser


class PromotionMethodViewSet(ModelViewSet):
    queryset = PromotionMethod.objects.all()
    serializer_class = PromotionMethodSerializer

    def list(self, request, *args, **kwargs):
        """
        販促内容
        - "id" : ID
        - "method" : 販促方法
        - "created_at" : 作成日
        - "created_by" : 担当者
        """
        return super(PromotionMethodViewSet, self).list(self, request, *args, **kwargs)

    def create(self, request):
        serializer = PromotionMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by_id=request.user.id)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
