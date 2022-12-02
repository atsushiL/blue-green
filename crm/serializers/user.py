import secrets
from rest_framework import serializers
from crm.models import (
    User,
    InterviewItem,
)
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "name", "email", "role", "is_active", "verified", "created_at", "updated_at"]
        read_only_fields = ["id", "updated_at", "created_at", "verified", "is_active"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            password=secrets.token_urlsafe(),
            name=validated_data.get("name"),
            email=validated_data.get("email"),
            role=validated_data.get("role"),
            is_active=False,
        )
        return user


class UserChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ["password", "new_password", "confirm_password"]

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("パスワードが異なっています。")
        validate_password(attrs["new_password"])

        return attrs


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=8)

    class Meta:
        model = User
        fields = ["username", "password"]


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class UserResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=254)
    new_password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("パスワードが異なっています。")
        validate_password(attrs["new_password"])
        return attrs


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=254)


class VerifyUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=8)
    new_password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("パスワードが異なっています。")
        validate_password(attrs["new_password"])
        return attrs
