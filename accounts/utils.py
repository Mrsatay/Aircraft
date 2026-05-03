from .models import UserProfile


def get_user_role(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"role": "Admin" if user.is_superuser else "Test Engineer"},
    )
    return profile.role
