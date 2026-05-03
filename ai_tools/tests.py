from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from accounts.models import UserProfile
from aircraft.models import Aircraft
from faults.models import Fault


class AiToolsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="pass123")
        UserProfile.objects.create(user=self.user, role="Admin")
        self.client.login(username="admin", password="pass123")
        self.aircraft = Aircraft.objects.create(
            tail_number="PK-AI01",
            model="A320neo",
            manufacturer="Airbus",
            current_status="Testing",
        )
        self.fault = Fault.objects.create(
            title="Display flicker",
            description="Intermittent flicker observed on left MFD.",
            aircraft=self.aircraft,
            reported_by=self.user,
            subsystem="Avionics",
            severity="Major",
            current_status="Assigned",
            flight_phase="Cruise",
        )

    def test_generate_description_fallback(self):
        with patch("ai_tools.views._call_openrouter", return_value=(None, "fallback")):
            response = self.client.post(
                reverse("ai_tools:generate_description"),
                data={
                    "aircraft": f"{self.aircraft.tail_number} - {self.aircraft.model}",
                    "subsystem": "Avionics",
                    "severity": "Major",
                    "flightPhase": "Cruise",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("Avionics", body["description"])

    def test_explain_fault_persists_explanation(self):
        with patch("ai_tools.views._call_openrouter", return_value=(None, "fallback")):
            response = self.client.post(reverse("ai_tools:explain_fault", args=[self.fault.pk]))

        self.assertEqual(response.status_code, 200)
        self.fault.refresh_from_db()
        self.assertTrue(self.fault.ai_explanation)
        self.assertIn("Summary:", self.fault.ai_explanation)
