from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Test Engineer", "Test Engineer"),
        ("Maintenance Engineer", "Maintenance Engineer"),
        ("Test Manager", "Test Manager"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default="Test Engineer")

    def __str__(self):
        return f"{self.user.username} ({self.role})"
