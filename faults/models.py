from django.contrib.auth.models import User
from django.db import models

from aircraft.models import Aircraft


class Fault(models.Model):
    STATUS_CHOICES = [
        ("New", "New"),
        ("Assigned", "Assigned"),
        ("Under Analysis", "Under Analysis"),
        ("Root Cause Identified", "Root Cause Identified"),
        ("Fix In Progress", "Fix In Progress"),
        ("Resolved", "Resolved"),
        ("Verified Closed", "Verified Closed"),
    ]
    SEVERITY_CHOICES = [
        ("Critical", "Critical"),
        ("Major", "Major"),
        ("Minor", "Minor"),
    ]
    FLIGHT_PHASE_CHOICES = [
        ("Pre-Flight", "Pre-Flight"),
        ("Taxi", "Taxi"),
        ("Takeoff", "Takeoff"),
        ("Climb", "Climb"),
        ("Cruise", "Cruise"),
        ("Descent", "Descent"),
        ("Landing", "Landing"),
        ("Post-Flight", "Post-Flight"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="faults")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reported_faults")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_faults")
    subsystem = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    current_status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="New")
    reported_date = models.DateTimeField(auto_now_add=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="closed_faults")
    analysis_findings = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    resolution_action = models.TextField(blank=True)
    severity_score = models.IntegerField(null=True, blank=True)
    resolution_time_hours = models.FloatField(null=True, blank=True)
    component_affected = models.CharField(max_length=120, blank=True)
    environmental_conditions = models.CharField(max_length=160, blank=True)
    flight_phase = models.CharField(max_length=40, choices=FLIGHT_PHASE_CHOICES, blank=True)
    ai_explanation = models.TextField(blank=True)

    class Meta:
        ordering = ["-reported_date"]

    def __str__(self):
        return f"#{self.pk} {self.title}"


class StatusHistory(models.Model):
    fault = models.ForeignKey(Fault, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=40, blank=True)
    new_status = models.CharField(max_length=40)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="status_changes")
    change_notes = models.TextField(blank=True)
    change_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-change_timestamp", "-id"]

    def __str__(self):
        return f"Fault #{self.fault_id}: {self.old_status or 'None'} -> {self.new_status}"
