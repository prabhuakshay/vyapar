from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

if TYPE_CHECKING:
    from django.http import HttpRequest

    from accounts.models import User


class UsernameOrEmailBackend(ModelBackend):
    """Authenticate with either username or email, case-insensitively."""

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: str,
    ) -> User | None:
        """Return the user matching the identifier and password, if any.

        Returns:
            The authenticated user, or None.
        """
        user_model = get_user_model()
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)
        if username is None or password is None:
            return None
        user = user_model.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        ).first()
        if user is None:
            # Hash anyway so response time doesn't reveal whether the user exists.
            user_model().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
