from django.contrib.auth.models import User
from django.utils import timezone

from aircraft.models import Aircraft
from aircraft.services import ensure_demo_aircraft

from .models import Fault, StatusHistory


WORKFLOW_TRANSITIONS = {
    "New": ["New", "Assigned"],
    "Assigned": ["Assigned", "Under Analysis"],
    "Under Analysis": ["Under Analysis", "Assigned", "Root Cause Identified"],
    "Root Cause Identified": ["Root Cause Identified", "Under Analysis", "Fix In Progress"],
    "Fix In Progress": ["Fix In Progress", "Root Cause Identified", "Resolved"],
    "Resolved": ["Resolved", "Fix In Progress", "Verified Closed"],
    "Verified Closed": ["Verified Closed"],
}


def get_allowed_statuses(current_status):
    return WORKFLOW_TRANSITIONS.get(current_status, [current_status] if current_status else [])


def is_valid_status_transition(current_status, new_status):
    if not new_status:
        return False
    if not current_status:
        return True
    return new_status in get_allowed_statuses(current_status)


def calculate_resolution_hours(reported_date, closed_date):
    if not reported_date or not closed_date:
        return None
    seconds = max((closed_date - reported_date).total_seconds(), 0)
    return round(seconds / 3600, 1)


def sync_fault_closure(fault, user=None):
    if fault.current_status in ["Resolved", "Verified Closed"]:
        fault.closed_date = fault.closed_date or timezone.now()
        fault.resolution_time_hours = calculate_resolution_hours(fault.reported_date, fault.closed_date)
        if user and not fault.closed_by:
            fault.closed_by = user
    else:
        fault.closed_date = None
        fault.closed_by = None
        fault.resolution_time_hours = None


def create_status_history(fault, old_status, user=None, notes=""):
    if old_status == fault.current_status:
        return None
    return StatusHistory.objects.create(
        fault=fault,
        old_status=old_status or "",
        new_status=fault.current_status,
        changed_by=user if getattr(user, "is_authenticated", False) else None,
        change_notes=notes or "",
    )


def build_fault_description(aircraft_label, subsystem, severity, flight_phase):
    severity_label = (severity or "Minor").strip()
    impact = {
        "Critical": "The condition has the potential to significantly affect aircraft safety and requires immediate technical action before further operation.",
        "Major": "The discrepancy is expected to affect system performance and should be investigated and corrected before the next planned operation.",
    }.get(severity_label, "The discrepancy appears limited in scope but should be documented, monitored, and corrected during scheduled maintenance activity.")

    return (
        f"During the {flight_phase or 'current'} phase, a {severity_label.lower()} fault indication was observed on aircraft "
        f"{aircraft_label} affecting the {subsystem} subsystem. Initial maintenance assessment indicates an abnormal "
        f"condition within the {subsystem} system that requires troubleshooting to confirm the source of the discrepancy. {impact}"
    )


def build_fault_explanation(fault, aircraft_label):
    def safe(value, default):
        return value.strip() if isinstance(value, str) and value.strip() else default

    summary = (
        f"Summary: Fault #{fault.pk} on {aircraft_label} indicates an issue in the "
        f"{safe(fault.subsystem, 'unspecified')} subsystem with {safe(fault.severity, 'unknown').lower()} severity. "
        f"The current workflow state is {safe(fault.current_status, 'not recorded')}."
    )
    impact = (
        f"Operational Impact: The affected component is {safe(fault.component_affected, 'not specified')}. "
        f"This may reduce testing continuity, subsystem reliability, or dispatch readiness until engineering review confirms the risk."
    )
    next_step = (
        "Recommended Next Step: Review the existing findings and continue with the next workflow action that matches the "
        "current state, making sure corrective action is validated before closure."
    )
    return "\n\n".join([summary, impact, next_step])


def ensure_demo_faults(user=None):
    ensure_demo_aircraft()
    if Fault.objects.exists():
        ensure_demo_status_history()
        return

    reporter = user if user and user.is_authenticated else User.objects.filter(is_superuser=True).first() or User.objects.first()
    assigned = User.objects.exclude(pk=getattr(reporter, "pk", None)).first() or reporter
    aircraft = list(Aircraft.objects.all()[:4])
    if not aircraft:
        return

    Fault.objects.bulk_create(
        [
            Fault(
                title="Hydraulic pressure fluctuation during taxi",
                description="Crew observed unstable hydraulic pressure on taxi-out with intermittent advisory indications.",
                aircraft=aircraft[0],
                reported_by=reporter,
                assigned_to=assigned,
                subsystem="Hydraulics",
                severity="Critical",
                current_status="Under Analysis",
                component_affected="Hydraulic Pump B",
                environmental_conditions="Hot and humid apron conditions",
                flight_phase="Taxi",
                analysis_findings="Pressure spikes correlated with pump temperature rise.",
            ),
            Fault(
                title="FMS intermittent data refresh delay",
                description="Navigation display requires several seconds to refresh route amendments after input.",
                aircraft=aircraft[1],
                reported_by=reporter,
                assigned_to=assigned,
                subsystem="Avionics",
                severity="Major",
                current_status="Assigned",
                component_affected="FMS CDU",
                environmental_conditions="Normal daylight operations",
                flight_phase="Cruise",
            ),
            Fault(
                title="Fuel quantity mismatch after engine start",
                description="Fuel indication shows asymmetrical reading after engine start sequence despite balanced fueling record.",
                aircraft=aircraft[2],
                reported_by=reporter,
                assigned_to=assigned,
                subsystem="Fuel",
                severity="Critical",
                current_status="Fix In Progress",
                component_affected="Fuel quantity indication system",
                environmental_conditions="Light rain before departure",
                flight_phase="Pre-Flight",
                root_cause="Suspected sensor calibration drift after overnight parking.",
            ),
            Fault(
                title="Spoiler armed indication mismatch",
                description="Spoiler armed annunciation remains amber briefly after selection and clears by itself.",
                aircraft=aircraft[3],
                reported_by=reporter,
                assigned_to=assigned,
                subsystem="Flight Controls",
                severity="Minor",
                current_status="Resolved",
                component_affected="Spoiler control logic",
                environmental_conditions="Dry runway condition",
                flight_phase="Landing",
                resolution_action="Performed logic module reset and post-maintenance operational check.",
                closed_date=timezone.now(),
                closed_by=assigned,
            ),
        ]
    )
    ensure_demo_status_history()


def ensure_demo_status_history():
    if StatusHistory.objects.exists():
        return

    for fault in Fault.objects.select_related("reported_by", "assigned_to", "closed_by").all():
        history_rows = []
        if fault.current_status != "New":
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="New",
                    new_status="Assigned",
                    changed_by=fault.reported_by,
                    change_notes="Initial triage and assignment.",
                )
            )
        if fault.current_status in ["Under Analysis", "Root Cause Identified", "Fix In Progress", "Resolved", "Verified Closed"]:
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="Assigned",
                    new_status="Under Analysis",
                    changed_by=fault.assigned_to or fault.reported_by,
                    change_notes="Engineering analysis started.",
                )
            )
        if fault.current_status in ["Root Cause Identified", "Fix In Progress", "Resolved", "Verified Closed"]:
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="Under Analysis",
                    new_status="Root Cause Identified",
                    changed_by=fault.assigned_to or fault.reported_by,
                    change_notes="Root cause isolated from troubleshooting data.",
                )
            )
        if fault.current_status in ["Fix In Progress", "Resolved", "Verified Closed"]:
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="Root Cause Identified",
                    new_status="Fix In Progress",
                    changed_by=fault.assigned_to or fault.reported_by,
                    change_notes="Corrective action moved into execution.",
                )
            )
        if fault.current_status in ["Resolved", "Verified Closed"]:
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="Fix In Progress",
                    new_status="Resolved",
                    changed_by=fault.closed_by or fault.assigned_to or fault.reported_by,
                    change_notes="Corrective action completed.",
                )
            )
        if fault.current_status == "Verified Closed":
            history_rows.append(
                StatusHistory(
                    fault=fault,
                    old_status="Resolved",
                    new_status="Verified Closed",
                    changed_by=fault.closed_by or fault.assigned_to or fault.reported_by,
                    change_notes="Closure verified after follow-up review.",
                )
            )
        if history_rows:
            StatusHistory.objects.bulk_create(history_rows)
