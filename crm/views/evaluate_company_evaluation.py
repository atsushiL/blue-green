from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest

from crm.serializers.evaluate_company_evaluation import (
    EvaluateCompanyEvaluationsSerializer,
)
from crm.models import (
    Estate,
    EvaluateCompanyEvaluations,
)
from crm.permission import (
    IsGeneralUser,
    IsSuperUser,
)


class EvaluateCompanyEvaluationsViewSet(ModelViewSet):
    serializer_class = EvaluateCompanyEvaluationsSerializer

    def get_queryset(self):
        return EvaluateCompanyEvaluations.objects.filter(
            estate_id=self.kwargs["estate_pk"]
        )

    def get_permissions(self):
        if self.action in ["destroy", "create"]:
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user, status=EvaluateCompanyEvaluations.Status.COMPLETE)

    @action(methods=["POST"], detail=True, permission_classes=[])
    def status_requested_data(self, request, pk, estate_pk):
        estate = get_object_or_404(Estate, pk=estate_pk)
        evaluation = get_object_or_404(estate.evaluate_company_evaluations, pk=pk)
        if evaluation.status != EvaluateCompanyEvaluations.Status.UNTOUCHED:
            return HttpResponseBadRequest()
        evaluation.status = EvaluateCompanyEvaluations.Status.IN_PROGRESS
        evaluation.save()
        return HttpResponse()

