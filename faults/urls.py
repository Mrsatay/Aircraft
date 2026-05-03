from django.urls import path
from . import views

app_name = "faults"

urlpatterns = [
    path("", views.fault_list_view, name="list"),
    path("create/", views.create_fault_view, name="create"),
    path("<int:fault_id>/", views.fault_detail_view, name="detail"),
    path("<int:fault_id>/status/", views.fault_status_update_view, name="status_update"),
    path("<int:fault_id>/edit/", views.fault_edit_view, name="edit"),
    path("<int:fault_id>/delete/", views.fault_delete_view, name="delete"),
]
