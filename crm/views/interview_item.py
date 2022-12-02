from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse

from crm.serializers.interview_item import InterviewItemSerializer
from crm.models import InterviewItem
from crm.permission import IsGeneralUser, IsSuperUser


class InterviewItemViewSet(ModelViewSet):
    queryset = InterviewItem.objects.all()
    serializer_class = InterviewItemSerializer

    def list(self, request, *args, **kwargs):
        """
        ヒアリング項目一覧
        - "id" : ID
        - "item" : ヒアリング項目
        - "memo" : 特記項目
        - "created_at" : 作成日
        - "created_by" : 担当者
        """
        return super(InterviewItemViewSet, self).list(self, request, *args, **kwargs)

    def create(self, request):
        serializer = InterviewItemSerializer(data=request.data)
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
