from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.utils import get_user_role
from aircraft.models import Aircraft
from aircraft.services import ensure_demo_aircraft

from .forms import FaultForm
from .models import Fault, StatusHistory
from .services import (
    create_status_history,
    ensure_demo_faults,
    get_allowed_statuses,
    is_valid_status_transition,
    sync_fault_closure,
)

ASSIGNABLE_ENGINEER_ROLES = ["Test Engineer", "Maintenance Engineer"]
FAULT_MANAGER_ROLES = ["Admin", "Test Manager"]


def _fault_queryset():
    return Fault.objects.select_related("aircraft", "reported_by", "assigned_to", "closed_by")


def _can_update_fault(user, fault):
    if not user.is_authenticated:
        return False
    if fault.current_status == "Verified Closed":
        return False
    role = get_user_role(user)
    if role in FAULT_MANAGER_ROLES:
        return True
    if role in ["Test Engineer", "Maintenance Engineer"]:
        return fault.assigned_to_id == user.pk
    return False


def _can_manage_fault_record(user):
    return user.is_authenticated and get_user_role(user) in FAULT_MANAGER_ROLES


def _allowed_statuses_for_user(user, fault):
    allowed_statuses = get_allowed_statuses(fault.current_status)
    if get_user_role(user) not in FAULT_MANAGER_ROLES:
        return [status for status in allowed_statuses if status != "Verified Closed"]
    return allowed_statuses


def _validate_status_requirements(user, new_status, analysis_findings="", root_cause=""):
    if new_status == "Verified Closed" and get_user_role(user) not in FAULT_MANAGER_ROLES:
        return "Only Admin or Test Manager can verify and close a fault."
    if new_status == "Under Analysis" and not analysis_findings.strip():
        return "Analysis Findings are required when moving a fault to Under Analysis."
    if new_status == "Root Cause Identified" and not root_cause.strip():
        return "Root Cause Description is required when moving a fault to Root Cause Identified."
    return None


def _assignable_users():
    return User.objects.filter(profile__role__in=ASSIGNABLE_ENGINEER_ROLES).order_by("username")


@login_required
def fault_list_view(request):
    ensure_demo_aircraft()
    ensure_demo_faults(request.user)
    can_manage_faults = _can_manage_fault_record(request.user)

    faults = _fault_queryset()
    status = request.GET.get("status", "").strip()
    severity = request.GET.get("severity", "").strip()
    aircraft_id = request.GET.get("aircraft", "").strip()
    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "-reported_date").strip()
    sort_options = {
        "-reported_date": "Newest Reported",
        "reported_date": "Oldest Reported",
        "title": "Title A-Z",
        "-title": "Title Z-A",
        "severity": "Severity A-Z",
        "-severity": "Severity Z-A",
        "current_status": "Status A-Z",
        "-current_status": "Status Z-A",
        "aircraft__tail_number": "Aircraft A-Z",
        "-aircraft__tail_number": "Aircraft Z-A",
    }

    if status:
        faults = faults.filter(current_status=status)
    if severity:
        faults = faults.filter(severity=severity)
    if aircraft_id.isdigit():
        faults = faults.filter(aircraft_id=int(aircraft_id))
    if search:
        faults = faults.filter(
            Q(title__icontains=search) | Q(description__icontains=search) | Q(subsystem__icontains=search)
        )
    if sort not in sort_options:
        sort = "-reported_date"
    faults = faults.order_by(sort, "-id")

    paginator = Paginator(faults, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    all_faults = Fault.objects.all()
    context = {
        "active_page": "faults",
        "faults": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "pagination_query": query_params.urlencode(),
        "total_faults": all_faults.count(),
        "active_faults": all_faults.exclude(current_status__in=["Resolved", "Verified Closed"]).count(),
        "under_maintenance": all_faults.filter(
            current_status__in=["Under Analysis", "Root Cause Identified", "Fix In Progress"]
        ).count(),
        "open_faults": all_faults.exclude(current_status__in=["Resolved", "Verified Closed"]).count(),
        "status_options": [choice[0] for choice in Fault.STATUS_CHOICES],
        "severity_options": [choice[0] for choice in Fault.SEVERITY_CHOICES],
        "aircraft_list": Aircraft.objects.all(),
        "selected_status": status,
        "selected_severity": severity,
        "selected_aircraft": aircraft_id,
        "search": search,
        "sort": sort,
        "selected_sort_label": sort_options[sort],
        "sort_options": sort_options,
        "can_manage_faults": can_manage_faults,
    }
    return render(request, "faults/list.html", context)


@role_required("Admin", "Test Engineer", "Test Manager")
def create_fault_view(request):
    ensure_demo_aircraft()
    can_assign_on_create = _can_manage_fault_record(request.user)
    if request.method == "POST":
        form_data = request.POST.copy()
        form_data["current_status"] = "New"
        if not can_assign_on_create:
            form_data["assigned_to"] = ""

        form = FaultForm(form_data)
        if form.is_valid():
            fault = form.save(commit=False)
            fault.reported_by = request.user
            fault.current_status = "New"
            if not can_assign_on_create:
                fault.assigned_to = None
            sync_fault_closure(fault, request.user)
            fault.save()
            create_status_history(fault, "", request.user, "Fault record created.")
            messages.success(request, "Fault created successfully.")
            return redirect("faults:detail", fault_id=fault.pk)
    else:
        form = FaultForm(initial={"current_status": "New"})

    return render(
        request,
        "faults/form.html",
        {
            "active_page": "faults",
            "form": form,
            "page_title": "Create Fault",
            "submit_label": "Save Fault",
            "can_assign_on_create": can_assign_on_create,
        },
    )


@login_required
def fault_detail_view(request, fault_id):
    fault = get_object_or_404(_fault_queryset(), pk=fault_id)
    can_manage_faults = _can_manage_fault_record(request.user)
    return render(
        request,
        "faults/detail.html",
        {
            "active_page": "faults",
            "fault": fault,
            "status_history": StatusHistory.objects.select_related("changed_by").filter(fault=fault),
            "allowed_statuses": _allowed_statuses_for_user(request.user, fault),
            "can_update_status": _can_update_fault(request.user, fault),
            "can_assign_fault": can_manage_faults,
            "can_edit_fault": can_manage_faults,
            "can_delete_fault": can_manage_faults,
            "assignable_users": _assignable_users(),
        },
    )


@role_required("Admin", "Test Manager")
def fault_edit_view(request, fault_id):
    fault = get_object_or_404(_fault_queryset(), pk=fault_id)
    if request.method == "POST":
        form = FaultForm(request.POST, instance=fault)
        if form.is_valid():
            old_status = fault.current_status
            fault = form.save(commit=False)
            if not is_valid_status_transition(old_status, fault.current_status):
                form.add_error("current_status", f"Invalid transition from {old_status} to {fault.current_status}.")
            else:
                error_message = _validate_status_requirements(
                    request.user,
                    fault.current_status,
                    fault.analysis_findings,
                    fault.root_cause,
                )
                if error_message:
                    form.add_error("current_status", error_message)
                else:
                    sync_fault_closure(fault, request.user)
                    fault.save()
                    create_status_history(fault, old_status, request.user, "Fault updated from edit form.")
                    messages.success(request, "Fault updated successfully.")
                    return redirect("faults:detail", fault_id=fault.pk)
    else:
        form = FaultForm(instance=fault)

    return render(
        request,
        "faults/form.html",
        {
            "active_page": "faults",
            "form": form,
            "page_title": f"Edit Fault #{fault.pk}",
            "submit_label": "Update Fault",
            "fault": fault,
        },
    )


@role_required("Admin", "Test Engineer", "Maintenance Engineer", "Test Manager")
def fault_status_update_view(request, fault_id):
    fault = get_object_or_404(_fault_queryset(), pk=fault_id)
    if request.method != "POST":
        return redirect("faults:detail", fault_id=fault.pk)
    if fault.current_status == "Verified Closed":
        messages.error(request, "Verified closed faults cannot be updated.")
        return redirect("faults:detail", fault_id=fault.pk)
    if not _can_update_fault(request.user, fault):
        messages.error(request, "You do not have permission to update this fault.")
        return redirect("faults:detail", fault_id=fault.pk)

    new_status = request.POST.get("new_status", "").strip()
    notes = request.POST.get("status_notes", "").strip()
    assigned_to = request.POST.get("assigned_to", "").strip()
    analysis_findings = request.POST.get("analysis_findings", "").strip()
    root_cause = request.POST.get("root_cause", "").strip()
    resolution_action = request.POST.get("resolution_action", "").strip()

    if not is_valid_status_transition(fault.current_status, new_status):
        messages.error(request, f"Invalid status transition from {fault.current_status} to {new_status}.")
        return redirect("faults:detail", fault_id=fault.pk)

    error_message = _validate_status_requirements(request.user, new_status, analysis_findings, root_cause)
    if error_message:
        messages.error(request, error_message)
        return redirect("faults:detail", fault_id=fault.pk)

    if _can_manage_fault_record(request.user):
        if assigned_to.isdigit():
            assignee = _assignable_users().filter(pk=int(assigned_to)).first()
            if not assignee:
                messages.error(request, "Faults can only be assigned to Test Engineer or Maintenance Engineer users.")
                return redirect("faults:detail", fault_id=fault.pk)
            fault.assigned_to = assignee
        elif assigned_to == "":
            fault.assigned_to = None

        if new_status == "Assigned" and fault.assigned_to is None:
            messages.error(request, "Assign an engineer before moving a fault to Assigned.")
            return redirect("faults:detail", fault_id=fault.pk)

    if new_status == "Under Analysis":
        fault.analysis_findings = analysis_findings
    if new_status == "Root Cause Identified":
        fault.root_cause = root_cause
    if new_status == "Resolved":
        fault.resolution_action = resolution_action

    old_status = fault.current_status
    fault.current_status = new_status
    sync_fault_closure(fault, request.user)
    fault.save()
    create_status_history(fault, old_status, request.user, notes)
    messages.success(request, f"Status updated to {new_status}.")
    return redirect("faults:detail", fault_id=fault.pk)


@role_required("Admin", "Test Manager")
def fault_delete_view(request, fault_id):
    fault = get_object_or_404(Fault, pk=fault_id)
    if request.method == "POST":
        fault.delete()
        messages.success(request, "Fault deleted successfully.")
        return redirect("faults:list")
    return render(request, "faults/delete_confirm.html", {"active_page": "faults", "fault": fault})
