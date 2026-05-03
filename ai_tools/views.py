import json
import os
from urllib import error, request as urllib_request

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from faults.models import Fault
from faults.services import build_fault_description, build_fault_explanation


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODELS = ["nvidia/nemotron-3-super-120b-a12b:free","google/gemma-4-31b-it:free", "minimax/minimax-m2.5:free"]


def _read_payload(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST


def _configured_models():
    models_value = os.getenv("OPENROUTER_MODELS", "").strip()
    if models_value:
        return [item.strip() for item in models_value.split(",") if item.strip()]
    single_model = os.getenv("OPENROUTER_MODEL", "").strip()
    if single_model:
        return [single_model]
    return DEFAULT_MODELS


def _call_openrouter(prompt, max_tokens):
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None, "OpenRouter is not configured. A local template response was generated instead."

    last_error = None
    for model_name in _configured_models():
        payload = {
            "model": model_name,
            "temperature": 0.5,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an experienced aircraft maintenance engineer. Return plain text only.",
                },
                {"role": "user", "content": prompt},
            ],
        }
        req = urllib_request.Request(
            OPENROUTER_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "http://localhost:8000"),
                "X-Title": os.getenv("OPENROUTER_TITLE", "Aircraft Fault Django Clone"),
            },
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
                return {"content": body["choices"][0]["message"]["content"].strip(), "model": model_name}, None
        except (error.HTTPError, error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = str(exc)

    return None, f"OpenRouter request failed. A local template response was generated instead. Details: {last_error}"


@login_required
@require_POST
def generate_description_view(request):
    payload = _read_payload(request)
    aircraft_label = str(payload.get("aircraft", "")).strip()
    subsystem = str(payload.get("subsystem", "")).strip()
    severity = str(payload.get("severity", "")).strip()
    flight_phase = str(payload.get("flightPhase", "") or payload.get("flight_phase", "")).strip()

    if not all([aircraft_label, subsystem, severity]):
        return JsonResponse(
            {
                "success": False,
                "error": "Aircraft, subsystem, and severity are required before generating a description.",
            },
            status=400,
        )

    prompt = (
        "Generate a concise aircraft maintenance fault description in 2-3 sentences.\n"
        f"Aircraft: {aircraft_label}\nSubsystem: {subsystem}\nSeverity: {severity}\n"
        f"Flight Phase: {flight_phase or 'Not provided'}"
    )
    ai_result, warning = _call_openrouter(prompt, 250)
    description = ai_result["content"] if ai_result else build_fault_description(aircraft_label, subsystem, severity, flight_phase)
    return JsonResponse(
        {
            "success": True,
            "description": description,
            "warning": warning,
            "modelUsed": ai_result["model"] if ai_result else None,
        }
    )


@login_required
@require_POST
def explain_fault_view(request, fault_id):
    fault = get_object_or_404(Fault.objects.select_related("aircraft"), pk=fault_id)
    aircraft_label = f"{fault.aircraft.tail_number} - {fault.aircraft.model}"
    prompt = (
        "Explain the following aircraft fault in 3 short sections titled Summary, Operational Impact, and Recommended Next Step.\n"
        f"Fault ID: {fault.pk}\nTitle: {fault.title}\nAircraft: {aircraft_label}\nSubsystem: {fault.subsystem}\n"
        f"Severity: {fault.severity}\nCurrent Status: {fault.current_status}\nDescription: {fault.description}\n"
        f"Component Affected: {fault.component_affected or 'Not provided'}\n"
        f"Flight Phase: {fault.flight_phase or 'Not provided'}\n"
        f"Environmental Conditions: {fault.environmental_conditions or 'Not provided'}\n"
        f"Analysis Findings: {fault.analysis_findings or 'Not provided'}\n"
        f"Root Cause: {fault.root_cause or 'Not provided'}\n"
        f"Resolution Action: {fault.resolution_action or 'Not provided'}"
    )
    ai_result, warning = _call_openrouter(prompt, 450)
    explanation = ai_result["content"] if ai_result else build_fault_explanation(fault, aircraft_label)
    if fault.ai_explanation != explanation:
        fault.ai_explanation = explanation
        fault.save(update_fields=["ai_explanation"])

    return JsonResponse(
        {
            "success": True,
            "explanation": explanation,
            "warning": warning,
            "modelUsed": ai_result["model"] if ai_result else None,
        }
    )
