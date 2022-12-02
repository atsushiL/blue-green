import csv, io, datetime
from django.shortcuts import get_object_or_404
from django.forms import model_to_dict
from django.db import transaction
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from crm.filters import ProspectCustomerFilter
from crm.models import (
    Customer,
    ProspectCustomer,
    ProspectCustomerData,
)
from crm.permission import IsGeneralUser, IsSuperUser
from crm.serializers.prospect_customer import (
    ListProspectCustomerSerializer,
    ProspectCustomerSerializer,
    CreateProspectCustomerSerilaizer,
)
from crm.serializers.customer import (
    CreateAndUpdateCustomerDataSerializer,
)


# Create your views here.
class ProspectCustomerViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProspectCustomerFilter
    queryset = ProspectCustomer.objects.filter(customer__customer_status=Customer.CustomerStatus.PROSPECT)


    def get_serializer_class(self):
        if self.action == "list":
            return ListProspectCustomerSerializer
        elif self.action == "create":
            return CreateProspectCustomerSerilaizer
        elif self.action in ["update","partial_update"]:
            return CreateAndUpdateCustomerDataSerializer
        else:
            return ProspectCustomerSerializer


    def create(self, request, *args, **kwargs):
        # 漢字氏名、カナ氏名、メールアドレス、生年月日、携帯電話番号、都道府県(ProspectCustomerData)、担当者を登録
        count = 0
        error_rows = []
        element = [
            "漢字氏名",
            "カナ氏名",
            "携帯電話番号",
            "メールアドレス",
            "生年月日",
            "都道府県",
        ]
        csv_file = request.FILES["file"]
        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        # header(1行目)を無視
        header = next(csv.reader(io_string))
        if len(header) < len(element):
            return Response({"msg":f"CSVファイルのヘッダー数が足りません.{header}"},status=status.HTTP_400_BAD_REQUEST)
        for i in range(len(element)):
            if not element[i] == header[i]:
                return Response({"msg":f"CSVファイルのヘッダーの内容が間違っています.{header}"},status=status.HTTP_400_BAD_REQUEST)
        for row in csv.reader(io_string, delimiter=","):
            year = int(row[4].split("/")[0])
            month = int(row[4].split("/")[1])
            day = int(row[4].split("/")[2])
            birthday = datetime.date(year, month, day)
            count += 1
            # CustomerDataに必要なデータ
            csv_data = {
                "name": row[0],
                "kana": row[1],
                "cellphone_no": "0" + row[2],
                "email": row[3],
                "birthday": birthday,
                "prefecture": row[5],
            }
            with transaction.atomic():
                serializer = CreateAndUpdateCustomerDataSerializer(data=csv_data)
                if serializer.is_valid():
                    # まだデータが存在しないなら保存し、すでに存在するなら保存しない
                    if not serializer.check_data_exists(csv_data):
                        customer = Customer.objects.create(
                            entrance=Customer.Entrance.PROSPECT,
                            customer_status=Customer.CustomerStatus.PROSPECT,
                            available=True,
                            created_by=request.user,
                            updated_by=request.user,
                        )
                        prefecture = serializer.validated_data.pop("prefecture")
                        serializer.save(customer=customer,created_by=request.user)
                        prospect_customer = ProspectCustomer.objects.create(
                        customer=customer,
                        created_by=request.user,
                        )
                        ProspectCustomerData.objects.create(
                            prospect_customer=prospect_customer,
                            prefecture=prefecture,
                            created_by=request.user,
                        )
                else:
                    error_rows.append(str(count) + ":" + str(serializer.error_messages))
        if len(error_rows) == 0:
            return JsonResponse({"msg":"CSVファイルのアップロードに成功しました"},status=status.HTTP_201_CREATED)
        else:
            msg = ""
            for row in error_rows:
                msg += str(row) + ","
            msg = msg[:-1]
            return JsonResponse({"msg":f"CSVファイルの{msg}行目のアップロードに失敗しました"},status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        prospect_customer = get_object_or_404(ProspectCustomer,pk=kwargs["pk"])
        partial = kwargs.pop('partial', False)
        if partial:
            data = prospect_customer.customer.customer_data.latest("created_at")
            input_data = model_to_dict(data)
            input_data['prefecture'] = prospect_customer.prospect_customer_data.latest("created_at").prefecture
            input_data.update(request.data)
        else:
            input_data = request.data
        serializer = self.get_serializer(data=input_data)
        serializer.is_valid(raise_exception=True)
        prefecture = serializer.validated_data.pop("prefecture")
        serializer.save(customer=prospect_customer.customer,created_by=request.user)
        ProspectCustomerData.objects.create(
            prospect_customer=prospect_customer,
            prefecture=prefecture,
            is_available=True,
            created_by=request.user,
        )
        serializer.validated_data["prefecture"] = prefecture
        customer = prospect_customer.customer
        customer.updated_by = self.request.user
        customer.save()
        return JsonResponse(data=serializer.validated_data,status=status.HTTP_201_CREATED)


    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsGeneralUser]
        elif self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
