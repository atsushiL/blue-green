from rest_framework.viewsets import ModelViewSet
from crm.serializers.evaluation_standard import EvaluationStandardSerializer
from crm.models import EvaluationStandard, EvaluationResult, Estate, PurchaseSurvey
from crm.permission import IsGeneralUser, IsSuperUser


class EvaluationStandardViewSet(ModelViewSet):
    queryset = EvaluationStandard.objects.all()
    serializer_class = EvaluationStandardSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

        estates = Estate.objects.all()
        for estate in estates:
            purchase_survey = PurchaseSurvey.objects.get(estate_id=estate.id)
            # 結果承認の場合、追加しない
            if purchase_survey.result is None:
                EvaluationResult.objects.create(
                    estate_id=estate.id,
                    created_by=self.request.user,
                    updated_by=self.request.user,
                    evaluation_standard_id=serializer.data["id"]
                )

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
