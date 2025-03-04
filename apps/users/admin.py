from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    
    list_display = ["pkid", "id", "email", "first_name",
                    "last_name","is_superuser",]
    list_display_links = ["pkid", "id", "email"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["pkid"]
    fieldsets = (
        (_("Login Credentials"), {"fields": ("email", "password")}),
        (_("Personal Info"), {
         "fields": ("first_name", "last_name")}),
        (_("Permissions and Groups"), {"fields": (
            "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Impotant Dated"), {"fields": ("last_login",)}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": (
        "email", "first_name", "last_name", "password1", "password2")}),)
