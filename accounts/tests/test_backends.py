from django.contrib.auth import authenticate
from django.test import TestCase

from accounts.models import User


class UsernameOrEmailBackendTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user("akshay", "a@example.com", "s3cret-pass")

    def test_login_with_username(self):
        assert authenticate(username="Akshay", password="s3cret-pass") == self.user

    def test_login_with_email(self):
        assert authenticate(username="A@Example.com", password="s3cret-pass") == (
            self.user
        )

    def test_wrong_password(self):
        assert authenticate(username="akshay", password="nope") is None

    def test_unknown_user(self):
        assert authenticate(username="ghost", password="s3cret-pass") is None

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        assert authenticate(username="akshay", password="s3cret-pass") is None
