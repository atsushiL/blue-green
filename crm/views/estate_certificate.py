from rest_framework.mixins import DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from crm.models import EstateCertificate
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.estate_certificate import EstateCertificateSerializer


class EstateCertificateViewSet(DestroyModelMixin, GenericViewSet):
    serializer_class = EstateCertificateSerializer

    def get_queryset(self):
        return EstateCertificate.objects.filter(estate_id=self.kwargs["estate_pk"])

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsGeneralUser]
        else:
            permission_classes = [IsSuperUser]
        return [permission() for permission in permission_classes]
