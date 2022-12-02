from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from crm.serializers.user import LoginSerializer


class LoginViewSet(ViewSet):
    serializer_class = LoginSerializer

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        logout(request)
        return HttpResponse()

    @action(methods=["POST"], detail=False, permission_classes=[])
    def login(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")
        password = serializer.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse(data={"msg": "ユーザーまたパスワードが間違っています。"}, status=400)
        else:
            login(request, user)
            return JsonResponse(data={'role': user.Role(user.role).name})
