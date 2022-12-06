from rest_framework.viewsets import ModelViewSet
from crm.models import EstateCertificate
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.estate_certificate import EstateCertificateSerializer


class EstateCertificateViewSet(ModelViewSet):
    serializer_class = EstateCertificateSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return EstateCertificate.objects.filter(estate_id=self.kwargs["estate_pk"])

    def perform_create(self, serializer):
        serializer.save(estate_id=self.kwargs['estate_pk'],
                        created_by=self.request.user)

