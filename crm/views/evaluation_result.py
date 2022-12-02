from rest_framework.permissions import IsAuthenticated
from crm.permission import IsGeneralUser, IsSuperUser
from rest_framework.viewsets import ModelViewSet
from crm.serializers.evaluation_result import EvaluationResultSerializer
from crm.models import EvaluationResult


class EvaluationResultViewSet(ModelViewSet):
    serializer_class = EvaluationResultSerializer

    def get_queryset(self):
        return EvaluationResult.objects.filter(
            estate_id=self.kwargs["estate_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            estate_id=self.kwargs['estate_pk'],
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            estate_id=self.kwargs['estate_pk'],
            updated_by=self.request.user
        )

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
