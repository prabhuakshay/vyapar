from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User


class UserManagerTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            "akshay", "Akshay@Example.COM", "s3cret-pass", full_name="Akshay Prabhu"
        )
        assert user.email == "akshay@example.com"
        assert user.check_password("s3cret-pass")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        user = User.objects.create_superuser("root", "root@example.com", "pw")
        assert user.is_staff
        assert user.is_superuser

    def test_superuser_must_be_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser("root", "r@example.com", "pw", is_staff=False)

    def test_requires_username_and_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user("", "a@example.com")
        with self.assertRaises(ValueError):
            User.objects.create_user("a", "")

    def test_natural_key_ignores_case(self):
        user = User.objects.create_user("Akshay", "a@example.com")
        assert User.objects.get_by_natural_key("akshay") == user


class UserModelTests(TestCase):
    def test_username_unique_ignoring_case(self):
        User.objects.create_user("akshay", "a@example.com")
        with self.assertRaises(IntegrityError):
            User.objects.create_user("AKSHAY", "b@example.com")

    def test_email_unique_ignoring_case(self):
        User.objects.create_user("a", "same@example.com")
        with self.assertRaises(IntegrityError):
            User.objects.create(username="b", email="SAME@example.com")

    def test_full_clean_reports_case_insensitive_duplicate(self):
        User.objects.create_user("akshay", "a@example.com")
        user = User(username="Akshay", email="b@example.com", full_name="X")
        user.set_unusable_password()
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_names(self):
        user = User(username="ap", full_name="  Akshay Prabhu ")
        assert str(user) == "ap"
        assert user.get_full_name() == "Akshay Prabhu"
        assert user.get_short_name() == "Akshay"
        assert User(username="ap").get_short_name() == "ap"

    def test_history_excludes_password(self):
        user = User.objects.create_user("akshay", "a@example.com", "pw")
        user.full_name = "Akshay Prabhu"
        user.save()
        assert user.history.count() == 2
        assert not hasattr(user.history.first(), "password")
