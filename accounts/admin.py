from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from simple_history.admin import SimpleHistoryAdmin

from accounts.forms import UserChangeForm, UserCreationForm
from accounts.models import User


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, BaseUserAdmin):
    """Admin for users, with change history."""

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("username", "full_name", "email", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "full_name", "email")
    ordering = ("username",)
    readonly_fields = ("last_login", "date_joined", "updated_at")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("full_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "full_name",
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
