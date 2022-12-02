from crm.models import Loan, ProvisionalCustomer
from crm.serializers.loan import LoanSerializer
from crm.utils.base_view_set import BaseViewSet


class LoanViewSet(BaseViewSet):
    serializer_class = LoanSerializer

    def get_queryset(self):
        return Loan.objects.filter(provisional_customer_id=self.kwargs['provisional_customer_pk'])

    def perform_create(self, serializer):
        serializer.save(provisional_customer_id=self.kwargs['provisional_customer_pk'])
        customer = ProvisionalCustomer.objects.get(
            id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()