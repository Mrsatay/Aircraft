from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import UserProfile
from .utils import get_user_role

ROLE_OPTIONS = ["Admin", "Test Engineer", "Maintenance Engineer", "Test Manager"]
PUBLIC_ROLE_OPTIONS = ["Test Engineer", "Maintenance Engineer", "Test Manager"]


def login_view(request):
    if request.user.is_authenticated:
        request.session["role"] = get_user_role(request.user)
        return redirect("dashboard:index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session["role"] = get_user_role(user)
            return redirect("dashboard:index")
        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        role = request.POST.get("role", "Test Engineer")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not full_name or not password:
            messages.error(request, "Please complete all required fields.")
        elif role not in PUBLIC_ROLE_OPTIONS:
            messages.error(request, "Please choose a valid role.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        elif password != confirm_password:
            messages.error(request, "Password confirmation does not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        else:
            first_name = full_name.split(" ", 1)[0]
            last_name = full_name.split(" ", 1)[1] if " " in full_name else ""
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            UserProfile.objects.create(
                user=user,
                role=role if role in ROLE_OPTIONS else "Test Engineer",
            )
            messages.success(request, "Registration successful. Please sign in.")
            return redirect("accounts:login")

    return render(request, "accounts/register.html", {"role_options": PUBLIC_ROLE_OPTIONS})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def _is_admin(user):
    return user.is_authenticated and get_user_role(user) == "Admin"


@login_required
def user_list_view(request):
    request.session["role"] = get_user_role(request.user)
    if not _is_admin(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("dashboard:index")

    users = User.objects.select_related("profile").order_by("id")
    context = {
        "active_page": "users",
        "users": users,
        "role_options": ROLE_OPTIONS,
    }
    return render(request, "accounts/users.html", context)


@login_required
def user_create_view(request):
    request.session["role"] = get_user_role(request.user)
    if not _is_admin(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("dashboard:index")

    if request.method != "POST":
        return redirect("accounts:users")

    username = request.POST.get("username", "").strip()
    full_name = request.POST.get("full_name", "").strip()
    password = request.POST.get("password", "")
    role = request.POST.get("role", "").strip()

    if not username or not full_name or not password or role not in ROLE_OPTIONS:
        messages.error(request, "Please complete all required fields with a valid role.")
        return redirect("accounts:users")
    if len(password) < 6:
        messages.error(request, "Password must be at least 6 characters long.")
        return redirect("accounts:users")
    if User.objects.filter(username=username).exists():
        messages.error(request, "Username is already taken.")
        return redirect("accounts:users")

    first_name = full_name.split(" ", 1)[0]
    last_name = full_name.split(" ", 1)[1] if " " in full_name else ""
    user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
    UserProfile.objects.create(user=user, role=role)
    messages.success(request, f"User {username} created successfully.")
    return redirect("accounts:users")


@login_required
def user_update_view(request, user_id):
    request.session["role"] = get_user_role(request.user)
    if not _is_admin(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("dashboard:index")
    if request.method != "POST":
        return redirect("accounts:users")

    user = get_object_or_404(User.objects.select_related("profile"), pk=user_id)
    full_name = request.POST.get("full_name", "").strip()
    password = request.POST.get("password", "")
    role = request.POST.get("role", "").strip()

    if not full_name or role not in ROLE_OPTIONS:
        messages.error(request, "Full name and valid role are required.")
        return redirect("accounts:users")

    user.first_name = full_name.split(" ", 1)[0]
    user.last_name = full_name.split(" ", 1)[1] if " " in full_name else ""
    user.save(update_fields=["first_name", "last_name"])
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save(update_fields=["role"])

    if password:
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("accounts:users")
        user.set_password(password)
        user.save(update_fields=["password"])

    if user.pk == request.user.pk:
        request.session["role"] = role
    messages.success(request, f"User {user.username} updated successfully.")
    return redirect("accounts:users")


@login_required
def user_delete_view(request, user_id):
    request.session["role"] = get_user_role(request.user)
    if not _is_admin(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("dashboard:index")
    if request.method != "POST":
        return redirect("accounts:users")

    user = get_object_or_404(User, pk=user_id)
    if user.pk == request.user.pk:
        messages.error(request, "You cannot delete the account you are currently using.")
        return redirect("accounts:users")

    username = user.username
    user.delete()
    messages.success(request, f"User {username} deleted successfully.")
    return redirect("accounts:users")
