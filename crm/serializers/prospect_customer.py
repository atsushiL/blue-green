from rest_framework import serializers
from crm.models import (
    ProspectCustomer,
    ALBAntiSocialCheck,
)
from crm.serializers.customer_negotiation_history import ListCustomerNegotiationHistorySerializer
from crm.serializers.alb_anti_social_check import ALBAntiSocialCheckSerializer

class ProspectCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProspectCustomer
        fields = "__all__"
        read_only_fields = ["customer","created_at","created_by"]


    def to_representation(self,instance):
        customer_data = instance.customer.customer_data.latest("created_at")
        rep = {
            "prospect_customer" :DetailProspectCustomerSerializer(
                instance=instance
            ).data,
            "alb_anti_social_check" :ALBAntiSocialCheckSerializer(
                instance=ALBAntiSocialCheck.objects.filter(name=customer_data.name, birthday=customer_data.birthday), many=True
            ).data,
            "customer_negotiation_history" :ListCustomerNegotiationHistorySerializer(
                instance=instance.customer.negotiation_history, many=True
            ).data,
        }
        return rep


# 見込客一覧を表示
class ListProspectCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProspectCustomer
        fields = ["id"]

    def to_representation(self, instance):
        rep = super(ListProspectCustomerSerializer, self).to_representation(instance)
        customer = instance.customer
        latest_customer_data = instance.customer.customer_data.latest("created_at")
        prospect_customer_data = instance.prospect_customer_data.latest("created_at")
        rep["cellphone_no"] = latest_customer_data.cellphone_no
        rep["name"] = latest_customer_data.name
        rep["prefecture"] = prospect_customer_data.prefecture
        rep["created_by"] = customer.created_by.name
        rep["created_at"] = customer.created_at

        if customer.negotiation_history.exists():
            rep["last_conversation_date"] = customer.negotiation_history.latest("negotiation_datetime").negotiation_datetime
        else:
            rep["last_conversation_date"] = ""

        return rep


# 見込客情報詳細を表示
class DetailProspectCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProspectCustomer
        fields = ["id"]

    def to_representation(self, instance):
        rep = super(DetailProspectCustomerSerializer, self).to_representation(instance)
        customer_data = instance.customer.customer_data.latest("created_at")
        prospect_customer_data = instance.prospect_customer_data.latest("created_at")
        # 漢字氏名、カナ氏名、携帯電話番号、メールアドレス、都道府県、特記事項、生年月日
        rep["customer_kana"] = customer_data.kana
        rep["customer_name"] = customer_data.name
        rep["cellphone_no"] = customer_data.cellphone_no
        rep["email"] = customer_data.email
        rep["prefecture"] = prospect_customer_data.prefecture
        rep["memo"] = customer_data.memo
        rep["birthday"] = customer_data.birthday
        rep["created_by"] = instance.created_by.name
        return rep


# ファイルアップロード用Serializer
class CreateProspectCustomerSerilaizer(serializers.Serializer):
    file = serializers.FileField()


