from django.db.models import Count, Q
from django.shortcuts import render

from accounts.decorators import role_required
from aircraft.models import Aircraft
from aircraft.services import ensure_demo_aircraft
from faults.models import Fault
from faults.services import ensure_demo_faults


def _status_badge(status):
    return {
        "New": "secondary",
        "Assigned": "primary",
        "Under Analysis": "warning",
        "Root Cause Identified": "info",
        "Fix In Progress": "warning",
        "Resolved": "success",
        "Verified Closed": "success",
    }.get(status, "dark")


@role_required("Admin", "Test Manager")
def reports_view(request):
    ensure_demo_aircraft()
    ensure_demo_faults(request.user)

    report_type = request.GET.get("report_type", "summary").strip() or "summary"
    status_filter = request.GET.get("status", "").strip()
    severity_filter = request.GET.get("severity", "").strip()
    aircraft_filter = request.GET.get("aircraft", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    filtered_faults = Fault.objects.select_related("aircraft", "assigned_to")
    if status_filter:
        filtered_faults = filtered_faults.filter(current_status=status_filter)
    if severity_filter:
        filtered_faults = filtered_faults.filter(severity=severity_filter)
    if aircraft_filter.isdigit():
        filtered_faults = filtered_faults.filter(aircraft_id=int(aircraft_filter))
    if date_from:
        filtered_faults = filtered_faults.filter(reported_date__date__gte=date_from)
    if date_to:
        filtered_faults = filtered_faults.filter(reported_date__date__lte=date_to)

    filtered_faults = filtered_faults.order_by("-reported_date")
    all_faults = Fault.objects.select_related("aircraft", "assigned_to").all()

    total_faults = filtered_faults.count()
    critical_faults = filtered_faults.filter(severity="Critical").count()
    resolved_faults = filtered_faults.filter(current_status__in=["Resolved", "Verified Closed"]).count()
    open_faults = filtered_faults.exclude(current_status__in=["Resolved", "Verified Closed"]).count()
    resolution_values = list(filtered_faults.exclude(resolution_time_hours__isnull=True).values_list("resolution_time_hours", flat=True))
    avg_resolution_hours = round(sum(resolution_values) / len(resolution_values), 1) if resolution_values else 0

    aircraft_stats = list(
        Aircraft.objects.annotate(
            total_faults=Count("faults", filter=Q(faults__in=filtered_faults)),
            critical_faults=Count("faults", filter=Q(faults__in=filtered_faults, faults__severity="Critical")),
            major_faults=Count("faults", filter=Q(faults__in=filtered_faults, faults__severity="Major")),
            minor_faults=Count("faults", filter=Q(faults__in=filtered_faults, faults__severity="Minor")),
            active_faults=Count(
                "faults",
                filter=Q(faults__in=filtered_faults) & ~Q(faults__current_status__in=["Resolved", "Verified Closed"]),
            ),
            resolved_faults=Count(
                "faults",
                filter=Q(faults__in=filtered_faults, faults__current_status__in=["Resolved", "Verified Closed"]),
            ),
        )
        .filter(total_faults__gt=0)
        .order_by("-total_faults", "tail_number")
    )

    subsystem_stats = list(
        filtered_faults.values("subsystem")
        .annotate(
            count=Count("id"),
            critical=Count("id", filter=Q(severity="Critical")),
            major=Count("id", filter=Q(severity="Major")),
            minor=Count("id", filter=Q(severity="Minor")),
        )
        .order_by("-count", "subsystem")
    )
    for item in subsystem_stats:
        item["name"] = item["subsystem"] or "Unknown"
        item["percentage"] = round((item["count"] / total_faults) * 100, 1) if total_faults else 0

    recent_faults = list(filtered_faults[:10])
    for fault in recent_faults:
        fault.status_badge = _status_badge(fault.current_status)
        fault.assigned_name = (
            fault.assigned_to.get_full_name() or fault.assigned_to.username if fault.assigned_to else "Unassigned"
        )

    severity_breakdown = {
        "Critical": filtered_faults.filter(severity="Critical").count(),
        "Major": filtered_faults.filter(severity="Major").count(),
        "Minor": filtered_faults.filter(severity="Minor").count(),
    }

    context = {
        "active_page": "reports",
        "report_type": report_type,
        "total_faults": total_faults,
        "critical_faults": critical_faults,
        "resolved_faults": resolved_faults,
        "open_faults": open_faults,
        "avg_resolution_hours": avg_resolution_hours,
        "aircraft_stats": aircraft_stats,
        "subsystem_stats": subsystem_stats,
        "recent_faults": recent_faults,
        "status_options": [choice[0] for choice in Fault.STATUS_CHOICES],
        "severity_options": [choice[0] for choice in Fault.SEVERITY_CHOICES],
        "aircraft_list": Aircraft.objects.all(),
        "selected_status": status_filter,
        "selected_severity": severity_filter,
        "selected_aircraft": aircraft_filter,
        "selected_date_from": date_from,
        "selected_date_to": date_to,
        "severity_breakdown": severity_breakdown,
        "report_type_options": [
            ("summary", "Summary Report"),
            ("by_aircraft", "By Aircraft"),
            ("by_severity", "By Severity"),
            ("by_subsystem", "By Subsystem"),
        ],
        "matching_faults": filtered_faults,
        "portfolio_faults": all_faults.count(),
    }
    return render(request, "reports/index.html", context)
