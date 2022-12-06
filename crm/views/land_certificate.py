from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from crm.models import Estate, LandCertificate, Land
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.land_certificate import LandCertificateSerializer


class LandCertificateViewSet(ModelViewSet):
    serializer_class = LandCertificateSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return LandCertificate.objects.filter(
            land_id=self.get_land_id(self.kwargs['estate_pk']))

    def perform_create(self, serializer):
        serializer.save(land_id=self.get_land_id(self.kwargs['estate_pk']),
                        created_by=self.request.user)

    def get_land_id(self, estate_id):
        estate = get_object_or_404(Estate, id=estate_id)
        land = Land.objects.filter(customer_id=estate.customer_id).first()
        return land.id