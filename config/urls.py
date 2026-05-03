from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="dashboard:index", permanent=False)),
    path("accounts/", include("accounts.urls")),
    path("ai/", include("ai_tools.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("faults/", include("faults.urls")),
    path("aircraft/", include("aircraft.urls")),
    path("reports/", include("reports.urls")),
]
