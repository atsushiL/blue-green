from crm.permission import IsGeneralUser, IsSuperUser
from crm.utils.base_view_set import BaseViewSet
from crm.models import PurchaseSurvey
from crm.serializers.purchase_survey import (
    PurchaseSurveySerializer,
)


class PurchaseSurveyViewSet(BaseViewSet):
    serializer_class = PurchaseSurveySerializer

    def get_queryset(self):
        return PurchaseSurvey.objects.filter(estate_id=self.kwargs["estate_pk"])

    def perform_create(self, serializer):
        serializer.save(estate_id=self.kwargs["estate_pk"])

    def get_permissions(self):
        if self.action in ["destroy", "create"]:
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
