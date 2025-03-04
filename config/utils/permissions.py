from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


User = get_user_model()

class HasPermissions(permissions.BasePermission):
    message = "You do not have permission."

    def has_permission(self, request: Request, view: View) -> bool:
        user = request.user
        if  not user or not user.is_authenticated:
            self.message = "Authentication is required to access this resource."
            return False
        
        return True
        

        