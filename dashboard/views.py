from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from aircraft.models import Aircraft
from aircraft.services import ensure_demo_aircraft
from faults.models import Fault, StatusHistory
from faults.services import ensure_demo_faults


@login_required
def dashboard_view(request):
    ensure_demo_aircraft()
    ensure_demo_faults(request.user)

    total_faults = Fault.objects.count()
    open_faults = Fault.objects.exclude(current_status__in=["Resolved", "Verified Closed"]).count()
    resolved_count = Fault.objects.filter(current_status__in=["Resolved", "Verified Closed"]).count()
    overdue_faults = Fault.objects.exclude(current_status__in=["Resolved", "Verified Closed"]).filter(
        reported_date__lt=timezone.now() - timezone.timedelta(days=7)
    ).count()
    closure_rate = round((resolved_count / total_faults) * 100) if total_faults else 0

    status_counts = {
        "new": 0,
        "assigned": 0,
        "under_analysis": 0,
        "root_cause": 0,
        "fix_progress": 0,
        "resolved": 0,
        "verified_closed": 0,
    }
    key_map = {
        "New": "new",
        "Assigned": "assigned",
        "Under Analysis": "under_analysis",
        "Root Cause Identified": "root_cause",
        "Fix In Progress": "fix_progress",
        "Resolved": "resolved",
        "Verified Closed": "verified_closed",
    }
    for item in Fault.objects.values("current_status").annotate(total=Count("id")):
        mapped = key_map.get(item["current_status"])
        if mapped:
            status_counts[mapped] = item["total"]

    severity_counts = {item["severity"]: item["total"] for item in Fault.objects.values("severity").annotate(total=Count("id"))}

    aircraft_hotspots = list(
        Aircraft.objects.annotate(
            total_faults=Count("faults"),
            open_faults=Count("faults", filter=~Q(faults__current_status__in=["Resolved", "Verified Closed"])),
            critical_faults=Count("faults", filter=Q(faults__severity="Critical")),
        ).filter(total_faults__gt=0).order_by("-total_faults", "tail_number")[:5]
    )

    critical_watchlist = Fault.objects.filter(severity__in=["Critical", "Major"]).exclude(
        current_status__in=["Resolved", "Verified Closed"]
    ).select_related("aircraft")[:5]

    oldest_open_faults = list(
        Fault.objects.exclude(current_status__in=["Resolved", "Verified Closed"]).select_related("aircraft").order_by("reported_date")[:5]
    )
    for item in oldest_open_faults:
        item.age_days = max((timezone.now() - item.reported_date).days, 0)

    recent_fault_activity = list(StatusHistory.objects.select_related("fault", "changed_by").all()[:5])
    for item in recent_fault_activity:
        actor = "System"
        if item.changed_by:
            actor = item.changed_by.get_full_name() or item.changed_by.username
        item.description = f"{actor} moved fault #{item.fault_id} to {item.new_status}"
        item.timestamp = item.change_timestamp

    subsystem_source = list(Fault.objects.values("subsystem").annotate(total=Count("id")).order_by("-total")[:5])
    phase_source = list(
        Fault.objects.values("flight_phase").exclude(flight_phase="").annotate(total=Count("id")).order_by("flight_phase")
    )

    resolution_values = list(Fault.objects.exclude(resolution_time_hours__isnull=True).values_list("resolution_time_hours", flat=True))
    avg_resolution_hours = round(sum(resolution_values) / len(resolution_values), 1) if resolution_values else 0

    context = {
        "active_page": "dashboard",
        "total_faults": total_faults,
        "open_faults": open_faults,
        "overdue_faults": overdue_faults,
        "closure_rate": closure_rate,
        "resolved_today": Fault.objects.filter(closed_date__date=timezone.localdate()).count(),
        "avg_resolution_hours": avg_resolution_hours,
        "critical_faults": severity_counts.get("Critical", 0),
        "major_faults": severity_counts.get("Major", 0),
        "minor_faults": severity_counts.get("Minor", 0),
        "status_counts": status_counts,
        "aircraft_hotspots": aircraft_hotspots,
        "critical_watchlist": critical_watchlist,
        "oldest_open_faults": oldest_open_faults,
        "recent_fault_activity": recent_fault_activity,
        "now": timezone.now(),
        "subsystem_labels": [item["subsystem"] for item in subsystem_source] or ["No Data"],
        "subsystem_values": [item["total"] for item in subsystem_source] or [0],
        "flight_phase_labels": [item["flight_phase"] for item in phase_source] or ["No Data"],
        "flight_phase_values": [item["total"] for item in phase_source] or [0],
    }
    return render(request, "dashboard/index.html", context)
