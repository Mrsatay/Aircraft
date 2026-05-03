from django.db import models


class Aircraft(models.Model):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Testing", "Testing"),
        ("Maintenance Review", "Maintenance Review"),
        ("Operational", "Operational"),
    ]

    tail_number = models.CharField(max_length=32, unique=True)
    model = models.CharField(max_length=120)
    manufacturer = models.CharField(max_length=120, blank=True)
    current_status = models.CharField(max_length=80, choices=STATUS_CHOICES, default="Available")

    class Meta:
        ordering = ["tail_number"]

    def __str__(self):
        return f"{self.tail_number} - {self.model}"
