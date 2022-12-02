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
