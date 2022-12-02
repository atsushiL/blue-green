from crm.models import WorkplaceInfo, ProvisionalCustomer
from crm.serializers.workplace_info import WorkplaceInfoSerializer
from crm.utils.base_view_set import BaseViewSet


class WorkplaceInfoViewSet(BaseViewSet):
    serializer_class = WorkplaceInfoSerializer

    def get_queryset(self):
        return WorkplaceInfo.objects.filter(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])

    def perform_create(self, serializer):
        serializer.save(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])
        customer = ProvisionalCustomer.objects.get(
            id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()