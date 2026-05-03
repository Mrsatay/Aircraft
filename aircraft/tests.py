from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from faults.models import Fault

from .models import Aircraft


class AircraftManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="pass123")
        UserProfile.objects.create(user=self.admin, role="Admin")
        self.engineer = User.objects.create_user(username="engineer", password="pass123")
        UserProfile.objects.create(user=self.engineer, role="Test Engineer")
        self.aircraft = Aircraft.objects.create(
            tail_number="PK-AC01",
            model="B737-800",
            manufacturer="Boeing",
            current_status="Operational",
        )
        Fault.objects.create(
            title="Control surface advisory",
            description="Advisory during taxi.",
            aircraft=self.aircraft,
            reported_by=self.admin,
            subsystem="Flight Controls",
            severity="Major",
            current_status="Assigned",
        )

    def test_aircraft_page_renders_stats_and_fault_link(self):
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("aircraft:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aircraft Management")
        self.assertContains(response, "View Faults (1)")

    def test_admin_can_create_and_update_aircraft(self):
        self.client.login(username="admin", password="pass123")
        create_response = self.client.post(
            reverse("aircraft:create"),
            {
                "tail_number": "PK-AC02",
                "model": "A320neo",
                "manufacturer": "Airbus",
                "current_status": "Testing",
            },
            follow=True,
        )
        self.assertEqual(create_response.status_code, 200)
        created = Aircraft.objects.get(tail_number="PK-AC02")

        update_response = self.client.post(
            reverse("aircraft:update", args=[created.pk]),
            {
                "tail_number": "PK-AC02",
                "model": "A321neo",
                "manufacturer": "Airbus",
                "current_status": "Maintenance Review",
            },
            follow=True,
        )
        self.assertEqual(update_response.status_code, 200)
        created.refresh_from_db()
        self.assertEqual(created.model, "A321neo")
        self.assertEqual(created.current_status, "Maintenance Review")

    def test_non_admin_manager_cannot_create_aircraft(self):
        self.client.login(username="engineer", password="pass123")
        response = self.client.post(
            reverse("aircraft:create"),
            {
                "tail_number": "PK-NOPE",
                "model": "ATR 72-600",
                "manufacturer": "ATR",
                "current_status": "Testing",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Aircraft.objects.filter(tail_number="PK-NOPE").exists())
