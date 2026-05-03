from django.urls import path
from . import views

app_name = "aircraft"

urlpatterns = [
    path("", views.aircraft_list_view, name="list"),
    path("create/", views.aircraft_create_view, name="create"),
    path("<int:aircraft_id>/update/", views.aircraft_update_view, name="update"),
]
