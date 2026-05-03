from django.urls import path

from . import views

app_name = "ai_tools"

urlpatterns = [
    path("generate-description/", views.generate_description_view, name="generate_description"),
    path("faults/<int:fault_id>/explain/", views.explain_fault_view, name="explain_fault"),
]
