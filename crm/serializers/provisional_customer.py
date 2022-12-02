from rest_framework import serializers
from crm.models import ProvisionalCustomer, Customer, AntiSocialCheckResult, \
    ProvisionalCustomerData
from crm.serializers.address import AddressSerializer
from crm.serializers.customer import CustomerDataSerializer


class ProvisionalCustomerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalCustomerData
        fields = "__all__"
        read_only_fields = ["id", "provisional_customer", "created_at", "created_by"]


# 仮申し込み客基本情報
class ProvisionalCustomerSerializer(serializers.Serializer):
    address = AddressSerializer()
    customer_data = CustomerDataSerializer()
    provisional_customer_data = ProvisionalCustomerDataSerializer()

    def to_representation(self, instance):
        rep = {
            "customer_data": CustomerDataSerializer(
                instance=instance.customer.customer_data.first()).data,
            "address": AddressSerializer(
                instance=instance.customer.address.first()).data,
            "provisional_customer_data": ProvisionalCustomerDataSerializer(
                instance=instance.provisional_customer_data.first()).data
        }
        rep["provisional_customer_data"]["status"] = ProvisionalCustomerData.Status(
            rep["provisional_customer_data"]["status"]).name
        rep["provisional_customer_data"]["property"] = ProvisionalCustomerData.Property(
            rep["provisional_customer_data"]["property"]).name
        return rep


# 仮申し込み客一覧を表示
class ListProvisionalCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalCustomer
        fields = ["id", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        rep = super(ListProvisionalCustomerSerializer, self).to_representation(instance)
        anti_social_check_result = instance.anti_social_check_result.first()
        customer = instance.customer
        customer_data = customer.customer_data.first()
        provisional_customer_data = customer.provisional_customer.provisional_customer_data.first()
        negotiation_history = customer.negotiation_history.first()

        if anti_social_check_result is None:
            anti_social_check_status = anti_social_result = ""
        else:
            anti_social_check_status = AntiSocialCheckResult.ANTI_SOCIAL_CHECK(
                anti_social_check_result.anti_social_check_status).name
            anti_social_result = anti_social_check_result.anti_social_result

        if negotiation_history is None:
            last_conversation_date = ""
        else:
            last_conversation_date = negotiation_history.negotiation_datetime

        rep["customer"] = customer.id
        rep["application_date"] = provisional_customer_data.application_date
        rep["provision_status"] = ProvisionalCustomerData.Status(
            provisional_customer_data.status).name
        rep["approval"] = provisional_customer_data.approval
        rep["name"] = customer_data.name
        rep["kana"] = customer_data.kana
        rep["created_by"] = customer.created_by.name
        rep["anti_social_check"] = anti_social_check_status
        rep["anti_social_result"] = anti_social_result
        rep["last_conversation_date"] = last_conversation_date
        return rep
