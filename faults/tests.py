from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserProfile
from aircraft.models import Aircraft

from .models import Fault, StatusHistory


class FaultWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="engineer", password="pass123")
        UserProfile.objects.create(user=self.user, role="Maintenance Engineer")
        self.client.login(username="engineer", password="pass123")
        self.aircraft = Aircraft.objects.create(
            tail_number="PK-TST01",
            model="B737-800",
            manufacturer="Boeing",
            current_status="Testing",
        )
        self.fault = Fault.objects.create(
            title="Hydraulic leak indication",
            description="Leak warning observed during ground check.",
            aircraft=self.aircraft,
            reported_by=self.user,
            assigned_to=self.user,
            subsystem="Hydraulics",
            severity="Critical",
            current_status="Assigned",
        )

    def test_status_update_creates_history(self):
        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Under Analysis",
                "assigned_to": str(self.user.pk),
                "analysis_findings": "Pressure drop confirmed at pump outlet.",
                "status_notes": "Started troubleshooting.",
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Under Analysis")
        history = StatusHistory.objects.get(fault=self.fault)
        self.assertEqual(history.old_status, "Assigned")
        self.assertEqual(history.new_status, "Under Analysis")

    def test_invalid_transition_is_rejected(self):
        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {"new_status": "Verified Closed"},
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Assigned")
        self.assertFalse(StatusHistory.objects.filter(fault=self.fault).exists())

    def test_under_analysis_requires_findings(self):
        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Under Analysis",
                "assigned_to": str(self.user.pk),
                "analysis_findings": "",
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Assigned")
        self.assertFalse(StatusHistory.objects.filter(fault=self.fault).exists())

    def test_root_cause_identified_requires_root_cause(self):
        self.fault.current_status = "Under Analysis"
        self.fault.analysis_findings = "Pressure drop confirmed."
        self.fault.save(update_fields=["current_status", "analysis_findings"])

        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Root Cause Identified",
                "assigned_to": str(self.user.pk),
                "root_cause": "",
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Under Analysis")

    def test_non_manager_cannot_verified_close_resolved_fault(self):
        self.fault.current_status = "Resolved"
        self.fault.save(update_fields=["current_status"])

        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Verified Closed",
                "assigned_to": str(self.user.pk),
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Resolved")

    def test_resolved_status_sets_resolution_time_automatically(self):
        self.fault.current_status = "Fix In Progress"
        self.fault.reported_date = timezone.now() - timezone.timedelta(hours=5, minutes=30)
        self.fault.save(update_fields=["current_status", "reported_date"])

        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Resolved",
                "resolution_action": "Replaced leaking hydraulic line and passed pressure test.",
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Resolved")
        self.assertIsNotNone(self.fault.closed_date)
        self.assertAlmostEqual(self.fault.resolution_time_hours, 5.5, delta=0.2)

    def test_test_manager_can_verified_close_resolved_fault(self):
        manager = User.objects.create_user(username="manager", password="pass123")
        UserProfile.objects.create(user=manager, role="Test Manager")
        self.client.login(username="manager", password="pass123")
        self.fault.current_status = "Resolved"
        self.fault.assigned_to = self.user
        self.fault.save(update_fields=["current_status", "assigned_to"])

        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Verified Closed",
                "assigned_to": str(self.user.pk),
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.current_status, "Verified Closed")

    def test_fault_cannot_be_assigned_to_test_manager(self):
        manager = User.objects.create_user(username="manager2", password="pass123")
        UserProfile.objects.create(user=manager, role="Test Manager")

        response = self.client.post(
            reverse("faults:status_update", args=[self.fault.pk]),
            {
                "new_status": "Assigned",
                "assigned_to": str(manager.pk),
            },
        )

        self.assertRedirects(response, reverse("faults:detail", args=[self.fault.pk]))
        self.fault.refresh_from_db()
        self.assertEqual(self.fault.assigned_to, self.user)
