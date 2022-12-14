from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.forms import model_to_dict
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from crm.filters import ProvisionalCustomerFilter
from crm.permission import IsGeneralUser, IsSuperUser
from rest_framework.viewsets import ModelViewSet
from crm.serializers.provisional_customer import ListProvisionalCustomerSerializer, \
    ProvisionalCustomerSerializer, ProvisionalCustomerDataSerializer
from crm.serializers.address import AddressSerializer
from crm.serializers.customer import CustomerDataSerializer
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from rest_framework import status
from crm.models import ProvisionalCustomer, Customer, \
    CustomerData, Address, ProvisionalCustomerData, Estate, AntiSocialCheckResult
from crm.utils.mail import send_refuse_email
from crm.utils.provisional_filter_backend import ProvisionalFilterBackend


class ProvisionalCustomerViewSet(ModelViewSet):
    filter_backends = (ProvisionalFilterBackend,)
    filterset_class = ProvisionalCustomerFilter
    queryset = ProvisionalCustomer.objects.filter(
        customer__customer_status=Customer.CustomerStatus.PROVISIONAL)

    def get_serializer_class(self):
        if self.action == "list":
            return ListProvisionalCustomerSerializer
        else:
            return ProvisionalCustomerSerializer

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer_data = serializer.validated_data.get('customer_data')
        address = serializer.validated_data.get('address')
        provisional_customer_data = serializer.validated_data.get('provisional_customer_data')

        customer = Customer.objects.create(
            entrance=Customer.Entrance.PROVISIONAL,
            customer_status=Customer.CustomerStatus.PROVISIONAL,
            available=True,
            created_by=request.user,
            updated_by=request.user
        )
        provisional_customer = ProvisionalCustomer.objects.create(
            customer=customer,
            updated_by=request.user
        )
        AntiSocialCheckResult.objects.create(
            provisional_customer=provisional_customer,
            created_by=request.user
        )

        data = self.__create_data(customer_data, address, provisional_customer_data,
                                  customer.id, provisional_customer.id)
        return JsonResponse(data=data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer_data = serializer.validated_data.get('customer_data')
        address = serializer.validated_data.get('address')
        provisional_customer_data = serializer.validated_data.get('provisional_customer_data')
        customer_id = ProvisionalCustomer.objects.get(id=kwargs["pk"]).customer_id

        data = self.__create_data(customer_data, address, provisional_customer_data,
                                  customer_id, kwargs["pk"])
        return JsonResponse(data=data)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        provisional_customer_id = kwargs["pk"]
        customer_id = ProvisionalCustomer.objects.get(id=provisional_customer_id).customer_id
        customer_data = CustomerData.objects.filter(customer_id=customer_id).first()
        address = Address.objects.filter(customer_id=customer_id).first()
        provisional_customer_data = ProvisionalCustomerData.objects.filter(
            provisional_customer_id=provisional_customer_id).first()
        for attr, value in request.data["customer_data"].items():
            setattr(customer_data, attr, value)
        for attr, value in request.data["address"].items():
            setattr(address, attr, value)
        for attr, value in request.data["provisional_customer_data"].items():
            setattr(provisional_customer_data, attr, value)
        input_data = {
            "customer_data": model_to_dict(customer_data),
            "address": model_to_dict(address),
            "provisional_customer_data": model_to_dict(provisional_customer_data)
        }
        serializer = self.get_serializer(data=input_data)
        serializer.is_valid(raise_exception=True)
        customer_data = CustomerDataSerializer(instance=customer_data).data
        address = AddressSerializer(instance=address).data
        provisional_customer_data = ProvisionalCustomerDataSerializer(
            instance=provisional_customer_data).data
        customer_data.pop("customer")
        address.pop("customer")
        provisional_customer_data.pop("provisional_customer")

        data = self.__create_data(customer_data, address, provisional_customer_data,
                                  customer_id, provisional_customer_id)
        return JsonResponse(data=data)

    def __create_data(self, customer_data, address, provisional_customer_data,
                      customer_id, provisional_customer_id):

        customer_data["customer_id"] = customer_id
        customer_data["created_by"] = self.request.user
        address["customer_id"] = customer_id
        provisional_customer_data["provisional_customer_id"] = provisional_customer_id
        provisional_customer_data["created_by"] = self.request.user

        if "id" in provisional_customer_data:
            customer_data.pop("id")
            address.pop("id")
            provisional_customer_data.pop("id")

        data = {
            "customer_data": CustomerDataSerializer(
                instance=CustomerData.objects.create(**customer_data)).data,
            "address": AddressSerializer(
                instance=Address.objects.create(**address)).data,
            "provisional_customer_data": ProvisionalCustomerDataSerializer(
                instance=ProvisionalCustomerData.objects.create(
                    **provisional_customer_data)).data
        }
        data["provisional_customer_data"]["status"] = ProvisionalCustomerData.Status(
            data["provisional_customer_data"]["status"]).name
        data["provisional_customer_data"]["property"] = ProvisionalCustomerData.Property(
            data["provisional_customer_data"]["property"]).name
        self.__update_customer(provisional_customer_id)
        return data

    # ???????????????????????? ?????????????????????
    @action(detail=True, methods=["POST"])
    def approval_false(self, request, pk):
        provisional_customer = get_object_or_404(ProvisionalCustomer, pk=pk)
        customer_data = provisional_customer.customer.customer_data.first()
        provisional_customer_data = provisional_customer.provisional_customer_data.first()
        # ?????????????????????????????????????????????????????????????????????
        # ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        if (provisional_customer_data.approval is not None) or \
                provisional_customer_data.status not in [
            provisional_customer_data.Status.INTERNAL_APPROVAL,
            provisional_customer_data.Status.CUSTOMER_APPROVAL,
            provisional_customer_data.Status.RENEGOTIATION,
            provisional_customer_data.Status.IN_PROGRESS
        ]:
            return HttpResponseBadRequest()
        # ?????????????????????????????????None?????????????????????
        estate_id = get_object_or_404(Estate, customer_id=provisional_customer.customer_id).id
        address = Address.objects.filter(estate_id=estate_id).first()
        address_str = \
            address.prefecture + address.municipalities + address.house_no + "  " + address.other
        send_refuse_email(
            user_email=customer_data.email,
            customer_name=customer_data.name,
            user_name=request.user.name,
            address=address_str)

        # ????????????????????????????????? & ?????????????????????
        data = model_to_dict(provisional_customer_data)
        data["provisional_customer_id"] = data.pop("provisional_customer")
        data["created_by"] = request.user
        data["status"] = ProvisionalCustomerData.Status.PROCESSED
        data["approval"] = False
        ProvisionalCustomerData.objects.create(**data)
        self.__update_customer(pk)
        return HttpResponse()

    def __change_status(self, provisional_customer_data: ProvisionalCustomerData, status,
                        approval=None):
        data = model_to_dict(provisional_customer_data)
        data["provisional_customer_id"] = data.pop("provisional_customer")
        data["created_by"] = self.request.user
        data["status"] = status
        if approval is not None:
            data["approval"] = approval
        self.__update_customer(data["provisional_customer_id"])
        return ProvisionalCustomerData.objects.create(**data)

    # ????????????status?????????
    @action(detail=True, methods=["POST"])
    def status_in_progress(self, request, pk):
        asc_result = AntiSocialCheckResult.objects.filter(provisional_customer_id=pk)
        if not asc_result.exists():
            return HttpResponseNotFound("??????????????????????????????????????????")
        if asc_result.first().anti_social_result is None:
            return HttpResponseBadRequest("??????????????????????????????????????????")
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")
        if provisional_customer_data.status != ProvisionalCustomerData.Status.UNTOUCHED:
            return HttpResponseBadRequest("?????????????????????????????????????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.IN_PROGRESS)

        return HttpResponse()

    # ????????????status????????????
    @action(detail=True, methods=["POST"])
    def status_internal_approval(self, request, pk):
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")
        if provisional_customer_data.status != ProvisionalCustomerData.Status.IN_PROGRESS:
            return HttpResponseBadRequest("?????????????????????????????????????????????????????????????????????")
        if provisional_customer_data.approval == False:
            return HttpResponseBadRequest("????????????????????????????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.INTERNAL_APPROVAL)

        return HttpResponse()

    # ????????????status???????????????
    @action(detail=True, methods=["POST"])
    def status_customer_approval(self, request, pk):
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")
        if provisional_customer_data.status != ProvisionalCustomerData.Status.INTERNAL_APPROVAL:
            return HttpResponseBadRequest("????????????????????????????????????????????????????????????????????????")
        if provisional_customer_data.approval == False:
            return HttpResponseBadRequest("????????????????????????????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.CUSTOMER_APPROVAL)

        return HttpResponse()

    # ????????????status?????????
    @action(detail=True, methods=["POST"])
    def status_renegotiation(self, request, pk):
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")
        if provisional_customer_data.status != ProvisionalCustomerData.Status.INTERNAL_APPROVAL:
            return HttpResponseBadRequest("????????????????????????????????????????????????????????????????????????")
        if provisional_customer_data.approval == False:
            return HttpResponseBadRequest("????????????????????????????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.RENEGOTIATION)

        return HttpResponse()

    # ????????????status????????????
    @action(detail=True, methods=["POST"])
    def status_withdrawal(self, request, pk):
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.WITHDRAWAL)

        return HttpResponse()

    # ????????????status??????
    @action(detail=True, methods=["POST"])
    def status_processed(self, request, pk):
        try:
            provisional_customer_data = self.__get_provisional_customer_data(pk)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("???????????????????????????????????????")
        if provisional_customer_data.status == ProvisionalCustomerData.Status.UNTOUCHED:
            return HttpResponseBadRequest("?????????????????????????????????????????????????????????")
        if provisional_customer_data.approval is None:
            return HttpResponseBadRequest("?????????????????????????????????????????????????????????????????????")

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.PROCESSED)

        return HttpResponse()

    def __get_provisional_customer_data(self, pk):
        provisional_customer_data = ProvisionalCustomerData.objects.filter(
            provisional_customer_id=pk)
        if provisional_customer_data.exists():
            provisional_customer_data = provisional_customer_data.first()
            return provisional_customer_data
        else:
            raise ObjectDoesNotExist()

    # ????????????????????????
    @action(detail=True, methods=["POST"])
    def approval_true(self, request, pk):
        asc_result = AntiSocialCheckResult.objects.filter(provisional_customer_id=pk)
        if not asc_result.exists():
            return HttpResponseNotFound("??????????????????????????????????????????")
        if not asc_result.first().anti_social_result:
            return HttpResponseBadRequest("??????????????????OK?????????????????????")

        provisional_customer_data = ProvisionalCustomerData.objects.filter(
            provisional_customer_id=pk).first()
        # ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        if (provisional_customer_data.approval is not None) or \
                provisional_customer_data.status not in [
            provisional_customer_data.Status.INTERNAL_APPROVAL,
            provisional_customer_data.Status.CUSTOMER_APPROVAL,
            provisional_customer_data.Status.RENEGOTIATION
        ]:
            return HttpResponseBadRequest()

        self.__change_status(
            provisional_customer_data, ProvisionalCustomerData.Status.PROCESSED, True)

        return HttpResponse()

    def __change_asc_status_or_result(self, pk, status=None, result=None):
        if not ProvisionalCustomer.objects.filter(id=pk).exists():
            return HttpResponseNotFound("??????????????????????????????????????????")
        asc_result = AntiSocialCheckResult.objects.filter(provisional_customer_id=pk)
        if asc_result.exists():
            asc_result = asc_result.first()
        else:
            return HttpResponseNotFound("??????????????????????????????????????????")
        data = model_to_dict(asc_result)
        data["provisional_customer_id"] = data.pop("provisional_customer")
        data["created_by"] = self.request.user
        if status is not None:
            data["anti_social_check_status"] = status
        if result is not None:
            data["anti_social_result"] = result
        AntiSocialCheckResult.objects.create(**data)
        self.__update_customer(pk)
        return HttpResponse()

    # ???????????????status?????????
    @action(detail=True, methods=["POST"])
    def asc_status_waiting(self, request, pk):
        return self.__change_asc_status_or_result(
            pk, AntiSocialCheckResult.ANTI_SOCIAL_CHECK.WAITING_FOR_RESULT)

    # ???????????????status????????????
    @action(detail=True, methods=["POST"])
    def asc_status_registered(self, request, pk):
        return self.__change_asc_status_or_result(
            pk, AntiSocialCheckResult.ANTI_SOCIAL_CHECK.RESULTS_REGISTERED)

    # ???????????????NG
    @action(detail=True, methods=["POST"])
    def asc_result_NG(self, request, pk):
        return self.__change_asc_status_or_result(
            pk, AntiSocialCheckResult.ANTI_SOCIAL_CHECK.RESULTS_REGISTERED, False)

    # ???????????????OK
    @action(detail=True, methods=["POST"])
    def asc_result_OK(self, request, pk):
        return self.__change_asc_status_or_result(
            pk, AntiSocialCheckResult.ANTI_SOCIAL_CHECK.RESULTS_REGISTERED, True)

    def __update_customer(self, provisional_customer_id):
        customer = ProvisionalCustomer.objects.get(
            id=provisional_customer_id).customer
        customer.updated_by = self.request.user
        customer.save()
