from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class UserManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="pass123", first_name="System", last_name="Admin")
        UserProfile.objects.create(user=self.admin, role="Admin")
        self.engineer = User.objects.create_user(username="engineer", password="pass123", first_name="Test", last_name="Engineer")
        UserProfile.objects.create(user=self.engineer, role="Test Engineer")

    def test_admin_can_view_user_management(self):
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("accounts:users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Management")
        self.assertContains(response, "engineer")

    def test_non_admin_cannot_view_user_management(self):
        self.client.login(username="engineer", password="pass123")
        response = self.client.get(reverse("accounts:users"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Akses ditolak")

    def test_admin_can_create_update_and_delete_user(self):
        self.client.login(username="admin", password="pass123")

        create_response = self.client.post(
            reverse("accounts:user_create"),
            {
                "username": "manager",
                "full_name": "Flight Manager",
                "password": "pass123",
                "role": "Test Manager",
            },
            follow=True,
        )
        self.assertEqual(create_response.status_code, 200)
        manager = User.objects.get(username="manager")
        self.assertEqual(manager.profile.role, "Test Manager")

        update_response = self.client.post(
            reverse("accounts:user_update", args=[manager.pk]),
            {
                "full_name": "Updated Manager",
                "password": "",
                "role": "Maintenance Engineer",
            },
            follow=True,
        )
        self.assertEqual(update_response.status_code, 200)
        manager.refresh_from_db()
        self.assertEqual(manager.profile.role, "Maintenance Engineer")
        self.assertEqual(manager.get_full_name(), "Updated Manager")

        delete_response = self.client.post(reverse("accounts:user_delete", args=[manager.pk]), follow=True)
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(User.objects.filter(username="manager").exists())

    def test_public_registration_cannot_choose_admin_role(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "full_name": "New User",
                "role": "Admin",
                "password": "pass123",
                "confirm_password": "pass123",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())
