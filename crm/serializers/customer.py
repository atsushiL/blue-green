from rest_framework import serializers
from crm.models import CustomerData, Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CustomerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerData
        fields = "__all__"
        read_only_fields = ["id", "created_at", "customer","created_by"]


class CreateAndUpdateCustomerDataSerializer(serializers.ModelSerializer):
    prefecture = serializers.CharField()

    class Meta:
        model = CustomerData
        fields = ["id", "name", "kana", "birthday", "email", "memo", "cellphone_no", "prefecture"]
        read_only_fields = ["created_at","created_by"]

    def check_data_exists(self, data):
        name = data.get("name")
        kana = data.get("kana")
        cellphone_no = data.get("cellphone_no")
        email = data.get("email")
        birthday = data.get("birthday")

        record = CustomerData.objects.filter(name=name,kana=kana,cellphone_no=cellphone_no,email=email,birthday=birthday).first()

        if record:
            return True
        else:
            return False

class GetEstateCustomerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

class EstateCustomerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id"]

    def to_representation(self, instance):
        rep = super(EstateCustomerDataSerializer, self).to_representation(instance)

        customer_data = instance.customer_data.latest('created_at')

        rep["name"] = customer_data.name
        rep["kana"] = customer_data.kana
        rep["birthday"] = customer_data.birthday
        rep['application_date'] = instance.provisional_customer.provisional_customer_data.latest("created_at").application_date
        rep['postcode'] = instance.address.latest("created_at").post_no
        return rep
