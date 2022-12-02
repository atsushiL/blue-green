from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse

from crm.serializers.promotion_result import PromotionResultSerializer
from crm.models import PromotionResult
from crm.permission import IsGeneralUser, IsSuperUser


class PromotionResultViewSet(ModelViewSet):
    queryset = PromotionResult.objects.all()
    serializer_class = PromotionResultSerializer

    def list(self, request, *args, **kwargs):
        """
        販促結果
        - "id" : ID
        - "result" : 販促結果
        - "created_at" : 作成日
        - "created_by" : 担当者
        """
        return super(PromotionResultViewSet, self).list(self, request, *args, **kwargs)

    def create(self, request):
        serializer = PromotionResultSerializer(data=request.data)
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
