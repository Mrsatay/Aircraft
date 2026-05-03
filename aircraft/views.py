from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from accounts.utils import get_user_role

from .models import Aircraft
from .services import ensure_demo_aircraft


def _can_manage_aircraft(user):
    return get_user_role(user) in ["Admin", "Test Manager"]


@login_required
def aircraft_list_view(request):
    ensure_demo_aircraft()
    aircraft = list(Aircraft.objects.annotate(fault_count=Count("faults")).order_by("tail_number"))
    context = {
        "active_page": "aircraft",
        "aircraft_list": aircraft,
        "total_aircraft": len(aircraft),
        "active_aircraft": sum(1 for item in aircraft if item.current_status in ["Operational", "Testing", "Available"]),
        "maintenance_aircraft": sum(1 for item in aircraft if item.current_status == "Maintenance Review"),
        "can_manage_aircraft": _can_manage_aircraft(request.user),
        "status_options": [choice[0] for choice in Aircraft.STATUS_CHOICES],
    }
    return render(request, "aircraft/list.html", context)


@login_required
def aircraft_create_view(request):
    if request.method != "POST":
        return redirect("aircraft:list")
    if not _can_manage_aircraft(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("aircraft:list")

    tail_number = request.POST.get("tail_number", "").strip()
    model = request.POST.get("model", "").strip()
    manufacturer = request.POST.get("manufacturer", "").strip()
    current_status = request.POST.get("current_status", "").strip()

    if not tail_number or not model or current_status not in [choice[0] for choice in Aircraft.STATUS_CHOICES]:
        messages.error(request, "Please complete all required aircraft fields.")
        return redirect("aircraft:list")
    if Aircraft.objects.filter(tail_number=tail_number).exists():
        messages.error(request, "Tail number already exists.")
        return redirect("aircraft:list")

    Aircraft.objects.create(
        tail_number=tail_number,
        model=model,
        manufacturer=manufacturer,
        current_status=current_status,
    )
    messages.success(request, f"Aircraft {tail_number} created successfully.")
    return redirect("aircraft:list")


@login_required
def aircraft_update_view(request, aircraft_id):
    if request.method != "POST":
        return redirect("aircraft:list")
    if not _can_manage_aircraft(request.user):
        messages.error(request, "Akses ditolak untuk peran Anda.")
        return redirect("aircraft:list")

    aircraft = get_object_or_404(Aircraft, pk=aircraft_id)
    tail_number = request.POST.get("tail_number", "").strip()
    model = request.POST.get("model", "").strip()
    manufacturer = request.POST.get("manufacturer", "").strip()
    current_status = request.POST.get("current_status", "").strip()

    if not tail_number or not model or current_status not in [choice[0] for choice in Aircraft.STATUS_CHOICES]:
        messages.error(request, "Please complete all required aircraft fields.")
        return redirect("aircraft:list")
    if Aircraft.objects.exclude(pk=aircraft.pk).filter(tail_number=tail_number).exists():
        messages.error(request, "Tail number already exists.")
        return redirect("aircraft:list")

    aircraft.tail_number = tail_number
    aircraft.model = model
    aircraft.manufacturer = manufacturer
    aircraft.current_status = current_status
    aircraft.save()
    messages.success(request, f"Aircraft {tail_number} updated successfully.")
    return redirect("aircraft:list")
