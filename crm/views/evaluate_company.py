from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse


from crm.serializers.evaluate_company import EvaluateCompanySerializer
from crm.models import Estate, EvaluateCompany, EvaluateCompanyEvaluations
from crm.permission import IsGeneralUser, IsSuperUser


class EvaluateCompanyViewSet(ModelViewSet):
    queryset = EvaluateCompany.objects.all()
    serializer_class = EvaluateCompanySerializer

    def list(self, request, *args, **kwargs):
        """
        評価会社
        - "id" : ID
        - "name" : 評価会社名
        - "phone_no" : 電話番号
        - "created_by" : 担当者
        - "created_at" : 作成日
        """
        return super(EvaluateCompanyViewSet, self).list(self, request, *args, **kwargs)

    def create(self, request):
        serializer = EvaluateCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by_id=request.user.id)
            estates = Estate.objects.filter(purchase_survey__result=None)
            for e in estates:
                EvaluateCompanyEvaluations.objects.create(
                    estate=e,
                    evaluate_company_id=serializer.data["id"],
                    created_by=request.user,
                    updated_by=request.user,
                )
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsSuperUser]
        else:
            permission_classes = [IsGeneralUser]
        return [permission() for permission in permission_classes]
