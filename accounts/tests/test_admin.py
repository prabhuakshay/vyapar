from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User


# The manifest only exists after collectstatic, which tests don't run.
@override_settings(
    STORAGES={
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class UserAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser("root", "root@example.com", "pw")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_changelist_and_search(self):
        response = self.client.get(
            reverse("admin:accounts_user_changelist"), {"q": "ro"}
        )
        assert response.status_code == 200

    def test_add_user(self):
        response = self.client.post(
            reverse("admin:accounts_user_add"),
            {
                "username": "akshay",
                "full_name": "Akshay Prabhu",
                "email": "a@example.com",
                "usable_password": "true",
                "password1": "a-Long-pass-123",
                "password2": "a-Long-pass-123",
            },
        )
        assert response.status_code == 302
        assert User.objects.filter(username="akshay").exists()

    def test_history_page(self):
        url = reverse("admin:accounts_user_history", args=[self.admin.pk])
        assert self.client.get(url).status_code == 200
