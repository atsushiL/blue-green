from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from crm.models import Family, ProvisionalCustomer
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.family import FamilySerializer


class FamilyViewSet(ModelViewSet):
    serializer_class = FamilySerializer

    def get_queryset(self):
        return Family.objects.filter(
            provisional_customer_id=self.kwargs['provisional_customer_pk'])

    def perform_create(self, serializer):
        serializer.save(
            provisional_customer_id=self.kwargs['provisional_customer_pk'],
            created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(
            provisional_customer_id=self.kwargs['provisional_customer_pk'],
            updated_by=self.request.user)
        customer = ProvisionalCustomer.objects.get(
            id=self.kwargs['provisional_customer_pk']).customer
        customer.updated_by = self.request.user
        customer.save()

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
