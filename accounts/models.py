from typing import ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager["User"]):
    """Creates users and superusers keyed on username."""

    use_in_migrations = True

    def get_by_natural_key(self, username: str | None) -> User:
        """Look up a user by username, ignoring case.

        Returns:
            The matching user.
        """
        return self.get(username__iexact=username)

    def _create_user(
        self, username: str, email: str, password: str | None, **extra_fields: object
    ) -> User:
        if not username:
            msg = "Users must have a username."
            raise ValueError(msg)
        if not email:
            msg = "Users must have an email address."
            raise ValueError(msg)
        user = self.model(
            username=self.model.normalize_username(username),
            email=self.normalize_email(email).lower(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        """Create a regular user.

        Returns:
            The saved user.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> User:
        """Create a user with full admin access.

        Returns:
            The saved superuser.

        Raises:
            ValueError: If `is_staff` or `is_superuser` is explicitly False.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields["is_staff"] is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields["is_superuser"] is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """A person who can sign in, identified by a unique username."""

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        help_text=_("150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={"unique": _("A user with that username already exists.")},
    )
    full_name = models.CharField(_("full name"), max_length=255)
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={"unique": _("A user with that email already exists.")},
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    # Password hashes and login timestamps would bloat history with noise.
    history = HistoricalRecords(excluded_fields=["password", "last_login"])

    objects: ClassVar[UserManager] = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["username"]
        constraints = [
            models.UniqueConstraint(
                Lower("username"),
                name="accounts_user_username_ci_unique",
                violation_error_message=_("A user with that username already exists."),
            ),
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
                violation_error_message=_("A user with that email already exists."),
            ),
        ]

    def __str__(self) -> str:
        return self.username

    def clean(self) -> None:
        """Normalize username and email before validation."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email).lower()

    def get_full_name(self) -> str:
        """Return the user's full name.

        Returns:
            The full name, stripped of surrounding whitespace.
        """
        return self.full_name.strip()

    def get_short_name(self) -> str:
        """Return the first word of the full name, or the username.

        Returns:
            A short, friendly name for greetings.
        """
        return self.get_full_name().split(" ", 1)[0] or self.username
