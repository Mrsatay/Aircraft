from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.user_list_view, name="users"),
    path("users/create/", views.user_create_view, name="user_create"),
    path("users/<int:user_id>/update/", views.user_update_view, name="user_update"),
    path("users/<int:user_id>/delete/", views.user_delete_view, name="user_delete"),
]
