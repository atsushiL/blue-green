from rest_framework import serializers
from crm.models import Land
from crm.serializers.address import AddressSerializer
from crm.serializers.land_data import LandDataSerializer


class LandSerializer(serializers.Serializer):
    address = AddressSerializer()
    land_data = LandDataSerializer()

    def to_representation(self, instance: Land):
        rep = {
            "land_data": LandDataSerializer(
                instance=instance.land_data.latest("created_at")
            ).data,
            "address": AddressSerializer(
                instance=instance.address.latest("created_at")
            ).data,
        }
        return rep


class ListLandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Land
        fields = "__all__"

    def to_representation(self, instance):
        # オブジェクトを全て取得する。
        rep = super(ListLandSerializer, self).to_representation(instance)

        land_data = instance.land_data.latest("created_at")
        land_certificate = instance.land_certificate.latest("created_at")
        address = instance.customer.address.latest("created_at")

        # 郵便番号を取得
        rep["post_no"] = address.post_no
        # 都道府県を取得
        rep["prefecture"] = address.prefecture
        # 市区町村を取得
        rep["municipalities"] = address.municipalities
        # 丁・番地を取得
        rep["house_no"] = address.house_no
        # 建物名・部屋番号を取得
        rep["other"] = address.other
        # 地番を取得
        rep["lot_no"] = land_data.lot_no
        # 地目を取得
        rep["landmark"] = land_data.landmark
        # 平方メートル
        rep["registered_size_square"] = land_data.registered_size_square
        # 登記簿謄本画像を取得
        rep["photo"] = land_certificate.photo
        # 名義種別を取得
        rep["holder_type"] = land_data.holder_type
        # 名義人名を取得
        rep["holder"] = land_data.holder

        return rep
