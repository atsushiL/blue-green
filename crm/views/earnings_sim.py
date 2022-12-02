from rest_framework.viewsets import ModelViewSet
from crm.models import EarningsSim
from rest_framework.permissions import IsAuthenticated
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.earnings_sim import EarningsSimSerializer


class EarningsSimViewSet(ModelViewSet):
    serializer_class = EarningsSimSerializer

    def get_queryset(self):
        return EarningsSim.objects.filter(estate_id=self.kwargs['estate_pk'])

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(estate_id=self.kwargs['estate_pk'],
                        created_by=self.request.user)
