from crm.models import AntiSocialCheckResult, ProvisionalCustomer
from crm.serializers.anti_social_check_result import AntiSocialCheckResultSerializer
from crm.utils.base_view_set import BaseViewSet


class AntiSocialCheckResultViewSet(BaseViewSet):
    serializer_class = AntiSocialCheckResultSerializer

    def get_queryset(self):
        return AntiSocialCheckResult.objects.filter(provisional_customer_id=self.kwargs['provisional_customer_pk'])

    def perform_create(self, serializer):
        serializer.save(provisional_customer_id=self.kwargs['provisional_customer_pk'])
        customer = ProvisionalCustomer.objects.get(
            id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()