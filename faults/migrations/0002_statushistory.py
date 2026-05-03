from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("faults", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("old_status", models.CharField(blank=True, max_length=40)),
                ("new_status", models.CharField(max_length=40)),
                ("change_notes", models.TextField(blank=True)),
                ("change_timestamp", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="status_changes", to=settings.AUTH_USER_MODEL)),
                ("fault", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="status_history", to="faults.fault")),
            ],
            options={"ordering": ["-change_timestamp", "-id"]},
        ),
    ]
