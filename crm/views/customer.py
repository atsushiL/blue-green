from rest_framework.permissions import IsAuthenticated
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.customer import CustomerSerializer
from rest_framework.viewsets import ModelViewSet
from crm.models import Customer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsGeneralUser]
        elif self.action == 'destroy':
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
