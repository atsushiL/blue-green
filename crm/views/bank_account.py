from crm.models import BankAccount, ProvisionalCustomer
from crm.serializers.bank_account import BankAccountSerializer
from crm.utils.base_view_set import BaseViewSet


class BankAccountViewSet(BaseViewSet):
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        return BankAccount.objects.filter(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])

    def perform_create(self, serializer):
        serializer.save(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])
        customer = ProvisionalCustomer.objects.get(
            id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()