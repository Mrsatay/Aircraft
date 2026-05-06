from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from aircraft.models import Aircraft
from faults.models import Fault


class ReportsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reporter", password="pass123")
        UserProfile.objects.create(user=self.user, role="Admin")
        self.client.login(username="reporter", password="pass123")
        aircraft_one = Aircraft.objects.create(
            tail_number="PK-RPT01",
            model="B737-800",
            manufacturer="Boeing",
            current_status="Testing",
        )
        aircraft_two = Aircraft.objects.create(
            tail_number="PK-RPT02",
            model="A320neo",
            manufacturer="Airbus",
            current_status="Operational",
        )
        Fault.objects.create(
            title="Hydraulic pressure issue",
            description="Pressure drop detected.",
            aircraft=aircraft_one,
            reported_by=self.user,
            assigned_to=self.user,
            subsystem="Hydraulics",
            severity="Critical",
            current_status="Under Analysis",
            resolution_time_hours=4,
        )
        Fault.objects.create(
            title="Display lag",
            description="Display update delayed.",
            aircraft=aircraft_two,
            reported_by=self.user,
            subsystem="Avionics",
            severity="Major",
            current_status="Resolved",
            resolution_time_hours=2,
        )

    def test_reports_page_renders_metrics_and_tables(self):
        response = self.client.get(reverse("reports:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Faults by Aircraft")
        self.assertContains(response, "Faults by Subsystem")
        self.assertContains(response, "Recent Fault Activity")
        self.assertEqual(response.context["total_faults"], 2)

    def test_reports_filters_by_severity(self):
        response = self.client.get(reverse("reports:index"), {"severity": "Critical"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_faults"], 1)
        self.assertContains(response, "Hydraulic pressure issue")
        self.assertNotContains(response, "Display lag")

    def test_test_engineer_cannot_access_reports(self):
        engineer = User.objects.create_user(username="engineer", password="pass123")
        UserProfile.objects.create(user=engineer, role="Test Engineer")
        self.client.login(username="engineer", password="pass123")

        response = self.client.get(reverse("reports:index"))

        self.assertRedirects(response, reverse("dashboard:index"))
