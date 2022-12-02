from rest_framework.permissions import BasePermission
from crm.models import User

# 一般ユーザー
class IsGeneralUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.user and request.user.is_authenticated:
            # 一般ユーザーにできて管理ユーザーにできないことはないので管理ユーザーもTrue
            if (
                request.user.role == User.Role.GENERAL
                or request.user.role == User.Role.MANAGEMENT
            ):
                return True
        return False


# 管理ユーザー
class IsManagementUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.user and request.user.is_authenticated:
            if request.user.role == User.Role.MANAGEMENT:
                return True
        return False

# スーパーユーザー
class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
