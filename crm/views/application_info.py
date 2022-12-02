from django.db import transaction
from crm.models import ApplicationInfo, ProvisionalCustomer
from crm.serializers.application_info import ApplicationInfoSerializer, \
    IntroductionCompanyIDSerializer
from crm.utils.base_view_set import BaseViewSet


class ApplicationInfoViewSet(BaseViewSet):
    serializer_class = ApplicationInfoSerializer

    def get_queryset(self):
        return ApplicationInfo.objects.filter(provisional_customer_id=self.kwargs['provisional_customer_pk'])

    @transaction.atomic
    def perform_create(self, serializer):
        if 'introduction_company' in self.request.data:
            intro_comp_id_serializer = IntroductionCompanyIDSerializer(data=self.request.data)
            intro_comp_id_serializer.is_valid(raise_exception=True)
            provisional_customer = ProvisionalCustomer.objects.get(
                id=self.kwargs['provisional_customer_pk'])
            provisional_customer.introduction_company_id = \
                intro_comp_id_serializer.validated_data.get('introduction_company')
            provisional_customer.updated_by = self.request.user
            provisional_customer.save()
        serializer.save(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])
        customer = ProvisionalCustomer.objects.get(
                id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()