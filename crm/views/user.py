import os
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from ag_smile_leaseback_crm_back import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from crm.filters import UserFilter
from crm.models import User
from crm.serializers.user import (
    UserSerializer,
    UserChangePasswordSerializer,
    EmailSerializer,
    UserResetPasswordSerializer,
    TokenSerializer,
    VerifyUserSerializer,
)
from crm.permission import IsManagementUser
from crm.utils.token import generate_token, validate_token
from crm.utils.mail import send_welcome_email, send_password_reset
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter

    def list(self, request, *args, **kwargs):
        user = request.user
        if int(user.role) == User.Role.MANAGEMENT:
            return super(UserViewSet, self).list(self, request, *args, **kwargs)
        else:
            instance = get_object_or_404(User, pk=user.id)
            serializer = self.get_serializer(instance=instance)
            return Response(serializer.data)

    @action(methods=["POST"], detail=False)
    def change_password(self, request):
        serializer = UserChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.data.get("password")
        new_password = serializer.data.get("new_password")
        user = request.user
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return HttpResponse()
        else:
            return JsonResponse(data={"msg": "旧パスワードが間違っています。"}, status=400)

    @action(detail=False, methods=["POST"], permission_classes=[IsManagementUser])
    def send_invite_user_mail(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        name = serializer.validated_data.get("name")
        email = serializer.validated_data.get("email")
        data = {
            "username": username,
            "email": email,
        }
        token = generate_token(data, settings.VERIFY_USER_TOKEN_EXPIRE)
        base_url = settings.CRM_BASE_URL
        url = base_url + "/verify_user/" + token
        serializer.save()
        send_welcome_email(user_email=email, username=name, url=url)
        return HttpResponse()

    @action(detail=False, methods=["POST"], permission_classes=[IsManagementUser])
    def resend_invite_user_mail(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        user = User.objects.get(email=email)
        data = {
            "username": user.username,
            "email": user.email,
        }
        token = generate_token(data, settings.VERIFY_USER_TOKEN_EXPIRE)
        base_url = settings.CRM_BASE_URL
        url = base_url + "/verify_user/" + token
        if user.verified:
            JsonResponse(data={"msg": "user verified."}, status=400)
        else:
            mail_sent_at = int(user.mail_sent_at.timestamp())
            expire = settings.VERIFY_USER_TOKEN_EXPIRE
            now = int(timezone.now().timestamp())
            if mail_sent_at + expire > now:
                return JsonResponse(data={"msg": "user invited today."}, status=400)
            else:
                send_welcome_email(user_email=email, username=user.name, url=url)
                user.mail_sent_at = timezone.now()
                user.save()
                return HttpResponse()

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny])
    def send_reset_password_mail(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return HttpResponse()
        data = {"email": email}
        token = generate_token(data, settings.PASSWORD_RESET_TOKEN_EXPIRE)
        base_url = settings.CRM_BASE_URL
        url = base_url + "/reset_password/" + token
        send_password_reset(email, url)
        return HttpResponse()

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = UserResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data.get("new_password")
        token = serializer.data.get("token")
        data = validate_token(token)
        if not data:
            return HttpResponseBadRequest("token validation failed ")
        try:
            user = User.objects.get(email=data["email"])
        except ObjectDoesNotExist:
            return HttpResponse()
        user.set_password(new_password)
        user.save()
        return HttpResponse()

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def verify_user_token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.data.get("token")
        data = validate_token(token)
        try:
            user = User.objects.get(username=data["username"])
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
        if not data or user.verified:
            return HttpResponseBadRequest("token validation failed ")
        return HttpResponse()

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def verify_mail_token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.data.get("token")
        data = validate_token(token)
        if not data:
            return HttpResponseBadRequest("token validation failed ")
        return HttpResponse()

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def verify_user(self, request):
        serializer = VerifyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data.get("new_password")
        username = serializer.validated_data.get("username")
        email = serializer.validated_data.get("email")
        token = serializer.data.get("token")
        data = validate_token(token)
        if not data:
            return HttpResponseBadRequest("token validation failed ")
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
        if (
            not user.verified
            and data["email"] == email
            and data["username"] == username
        ):
            user.set_password(new_password)
            user.is_active = True
            user.verified = True
            user.save()
            return HttpResponse()
        else:
            return HttpResponseBadRequest()

    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def user_info(self, request):
        data = {"name": "", "role": ""}
        if request.user.is_authenticated:
            data = {
                "name": request.user.name,
                "role": request.user.Role(request.user.role).name,
            }
        return JsonResponse(data=data)

    @action(methods=["POST"], detail=True, permission_classes=[IsManagementUser])
    def disable_user(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user == user:
            return HttpResponseBadRequest()
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()

        return HttpResponse()
