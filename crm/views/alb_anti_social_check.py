import io, csv, re
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from crm.models import ALBAntiSocialCheck
from crm.permission import (
    IsGeneralUser,
)
from crm.serializers.alb_anti_social_check import (
    ALBAntiSocialCheckSerializer,
    FileUploadSerializer,
)


class ALB_Anti_Social_CheckViewSet(ModelViewSet):
    queryset = ALBAntiSocialCheck.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FileUploadSerializer
        else:
            return ALBAntiSocialCheckSerializer


    def create(self, request, *args, **kwargs):
        count = 0
        error_rows = []
        element = [
            "漢字氏名",
            "カナ氏名",
            "生年月日",
            "登録内容",
            "取引状況",
            "契約書に反社会的勢力の排除条項の有無",
            "反社会的勢力と判明した日",
            "反社会的勢力であることが判明した経緯",
            "対応方針",
            "入庫日",
        ]
        csv_file = request.FILES["file"]
        decoded_file = csv_file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        # 1行目を無視
        header = next(csv.reader(io_string))
        if len(header) < len(element):
            return Response({"msg":f"CSVファイルのヘッダー数が足りません.{header}"},status=status.HTTP_400_BAD_REQUEST)
        for i in range(len(element)):
            if not element[i] == header[i]:
                return Response({"msg":f"CSVファイルのヘッダーの内容が間違っています.{header}"},status=status.HTTP_400_BAD_REQUEST)
        for row in csv.reader(io_string, delimiter=","):
            count += 1

            registered_info = row[3].split("\n")
            address = phone_no = cellphone_no = workplace = workplace_phone_no = ""
            for info in registered_info:
                if re.search("住所：", info):
                    address = info.strip().lstrip("住所：")
                elif re.search("自宅電話：", info):
                    phone_no = info.strip().lstrip("自宅電話：")
                elif re.search("携帯電話：", info):
                    cellphone_no = info.strip().lstrip("携帯電話：")
                elif re.search("勤務先：", info):
                    workplace = info.strip().lstrip("勤務先：")
                elif re.search("勤務先電話：", info):
                    workplace_phone_no =  info.strip().lstrip("勤務先電話：") 
            
            business_details = row[4].split("\n")
            account_overview = balance = new_appraisal_loan_date = ""
            for detail in business_details:
                if re.search("口座概要：", detail):
                    account_overview = detail.strip().lstrip("口座概要：")
                elif re.search("残高：", detail):
                    balance = detail.strip().lstrip("残高：")
                elif re.search("新規査定貸付日：", detail):
                    new_appraisal_loan_date = detail.strip().lstrip("新規査定貸付日：")

            csv_data = {
                "name": row[0],
                "kana": row[1],
                "birthday": row[2],
                "address": address,
                "phone_no": phone_no,
                "cellphone_no": cellphone_no,
                "workplace": workplace,
                "workplace_phone_no": workplace_phone_no,  
                "account_overview": account_overview,
                "balance": balance,
                "new_appraisal_loan_date": new_appraisal_loan_date,
                "anti_social_confirmation_date": row[5],
                "anti_social_confirmation_reason": row[6],
                "response_policy": row[7],
                "receipt_date": row[8],
                "created_by":request.user.id
            }
            serializer = ALBAntiSocialCheckSerializer(data=csv_data)
            if serializer.is_valid():
                # まだデータが存在しないなら保存し、すでに存在するなら保存しない
                if not serializer.check_data_exists(csv_data):
                    serializer.save()
            else:
                error_rows.append(str(count) + ":" + serializer.error_messages)
        if len(error_rows) == 0:
            return Response({"msg":"CSVファイルのアップロードに成功しました"},status=status.HTTP_201_CREATED)
        else:
            msg = ""
            for row in error_rows:
                msg += str(row) + ","
            msg = msg[:-1]
            return Response({"msg":f"CSVファイルの{msg}行目のアップロードに失敗しました"},status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsGeneralUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
