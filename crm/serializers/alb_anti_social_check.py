from rest_framework import serializers
from crm.models import ALBAntiSocialCheck


class ALBAntiSocialCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ALBAntiSocialCheck
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


    def check_data_exists(self, data):
        name = data.get("name")
        kana = data.get("kana")
        birthday = data.get("birthday")
        address = data.get("address")

        record = ALBAntiSocialCheck.objects.filter(name=name,kana=kana,birthday=birthday,address=address).first()

        if record:
            return True
        else:
            return False


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
