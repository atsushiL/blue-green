from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from crm.permission import IsSuperUser, IsGeneralUser
from crm.serializers.building_info import BuildingInfoSerializer
from crm.serializers.address import AddressSerializer
from crm.serializers.purchase_survey import PurchaseSurveySerializer
from crm.serializers.estate import EstateSerializer
from crm.serializers.building import BuildingSerializer
from crm.serializers.customer import GetEstateCustomerSerializer
from crm.serializers.customer import EstateCustomerDataSerializer
from crm.models import (
    PurchaseSurvey,
    EvaluationStandard,
    EvaluationResult,
    Estate,
    BuildingInfo,
    Address,
    EvaluateCompany,
    EvaluateCompanyEvaluations,
    Customer,
    ProvisionalCustomerData,
)
from crm.filters import EstateFilter, get_newest_customer_data


class EstateViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EstateFilter

    def get_queryset(self):
        if self.action == 'get_customers':
            return Customer.objects.filter(customer_status=Customer.CustomerStatus.PROVISIONAL)
        else:
            return Estate.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return EstateSerializer
        if self.action == 'get_customers':
            return GetEstateCustomerSerializer
        else:
            return BuildingSerializer

    def list(self, request, *args, **kwargs):
        return super(EstateViewSet, self).list(self, request)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        building_info_data = serializer.validated_data.get("building_info")
        address_data = serializer.validated_data.get("address")
        estate_data = serializer.validated_data.get("estate")
        customer = estate_data["customer"]
        # これは2次開発でやります
        # guarantee_company = get_object_or_404(
        #     GuaranteeCompany, id=estate_data["guarantee_company"].id
        # )

        estate = Estate.objects.create(
            customer=customer,
            introduction_company=customer.provisional_customer.introduction_company,
            created_by=request.user,
            updated_by=request.user,
        )

        building_info = BuildingInfo.objects.create(
            estate_id=estate.id, created_by=request.user, **building_info_data
        )

        purchase_survey = PurchaseSurvey.objects.create(
            estate_id=estate.id, created_by=request.user
        )

        evaluation_standards = EvaluationStandard.objects.all()
        for item in evaluation_standards:
            EvaluationResult.objects.create(
                estate_id=estate.id,
                created_by=request.user,
                updated_by=request.user,
                evaluation_standard_id=item.id
            )

        if "land" in address_data:
            address_data.pop("land")
        if "customer" in address_data:
            address_data.pop("customer")

        address_data["estate"] = estate
        address = Address.objects.create(**address_data)

        evaluation_companies = EvaluateCompany.objects.all()
        for ec in evaluation_companies:
            EvaluateCompanyEvaluations.objects.create(
                estate=estate,
                evaluate_company=ec,
                created_by=request.user,
                updated_by=request.user,
            )

        data = {
            "building_info": BuildingInfoSerializer(instance=building_info).data,
            "address": AddressSerializer(instance=address).data,
            "estate": EstateSerializer(instance=estate).data,
            "purchase_survey": PurchaseSurveySerializer(instance=purchase_survey).data,
        }
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def get_customers(self, request):
        serializer = GetEstateCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        queryset = get_newest_customer_data(
            self.get_queryset(),
            Customer.CustomerStatus.PROVISIONAL,
            Q(name__contains=serializer.validated_data.get("name")))
        data = {
            "customers": EstateCustomerDataSerializer(queryset, many=True).data
        }
        return JsonResponse(data=data)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["POST"])
    def get_provisional_customer(self, request, pk):
        estate = self.get_object()
        data = {
            "provisional_customer":
                estate.customer.provisional_customer.id,
            "customer_name":
                estate.customer.customer_data.first().name,
            "customer_status": ProvisionalCustomerData.Status(
                estate.customer.provisional_customer.provisional_customer_data.first().status
            ).name
        }
        return JsonResponse(data=data)
