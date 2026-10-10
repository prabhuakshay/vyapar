from django.contrib.auth import forms as auth_forms

from accounts.models import User


class UserCreationForm(auth_forms.AdminUserCreationForm):
    """Admin form for adding a user."""

    class Meta:
        model = User
        fields = ("username", "full_name", "email")


class UserChangeForm(auth_forms.UserChangeForm):
    """Admin form for editing a user."""

    class Meta:
        model = User
        fields = "__all__"
