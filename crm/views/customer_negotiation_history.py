from django.http import HttpResponseNotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from crm.serializers.customer_negotiation_history import (
    ListCustomerNegotiationHistorySerializer,
    CreateCustomerNegotiationHistorySerializer,
    CustomerNegotiationHistorySerializer,
)
from rest_framework.permissions import IsAuthenticated

from crm.models import (
    CustomerNegotiationHistory,
    ProvisionalCustomer,
    ProspectCustomer,
)

from crm.permission import (
    IsGeneralUser,
    IsSuperUser,
)


class CustomerNegotiationHistoryViewSet(ModelViewSet):
    def get_queryset(self):
        # 仮申込客
        if "provisional_customer_pk" in self.kwargs:
            customer_id = get_object_or_404(
                ProvisionalCustomer, id=self.kwargs["provisional_customer_pk"]).customer_id
        # 見込客
        elif "prospect_customer_pk" in self.kwargs:
            customer_id = get_object_or_404(
                ProspectCustomer, id=self.kwargs["prospect_customer_pk"]).customer_id
        else:
            return HttpResponseNotFound()
        return CustomerNegotiationHistory.objects.filter(customer_id=customer_id)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateCustomerNegotiationHistorySerializer
        elif self.action == "list":
            return ListCustomerNegotiationHistorySerializer
        else:
            return CustomerNegotiationHistorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["created_by_id"] = request.user.id
        serializer.validated_data["updated_by_id"] = request.user.id
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # 仮申込客
        if "provisional_customer_pk" in self.kwargs:
            customer_id = get_object_or_404(
                ProvisionalCustomer, id=self.kwargs["provisional_customer_pk"]).customer_id
        # 見込客
        else:
            customer_id = get_object_or_404(
                ProspectCustomer, id=self.kwargs["prospect_customer_pk"]).customer_id
        serializer.save(customer_id=customer_id)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsSuperUser]
        else:
            # 仮申込客の交渉履歴を閲覧・登録できるのは管理者・一般ユーザ
            if "provisional_customer_pk" in self.kwargs:
                permission_classes = [IsGeneralUser]
            else:
                # 全てのログインユーザは見込客のの交渉履歴を閲覧・登録できる
                permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
