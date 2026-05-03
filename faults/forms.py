from django import forms
from django.contrib.auth.models import User

from .models import Fault


class FaultForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role__in=["Test Engineer", "Maintenance Engineer"]).order_by("username"),
        required=False,
        empty_label="Unassigned",
    )

    class Meta:
        model = Fault
        fields = [
            "title",
            "description",
            "aircraft",
            "subsystem",
            "severity",
            "component_affected",
            "environmental_conditions",
            "flight_phase",
            "assigned_to",
            "current_status",
            "analysis_findings",
            "root_cause",
            "resolution_action",
            "severity_score",
            "resolution_time_hours",
            "ai_explanation",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Brief description of the fault"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Detailed description of the fault"}),
            "subsystem": forms.TextInput(attrs={"placeholder": "e.g., Hydraulics, Avionics, Fuel"}),
            "component_affected": forms.TextInput(attrs={"placeholder": "e.g., Main Landing Gear Actuator"}),
            "environmental_conditions": forms.TextInput(attrs={"placeholder": "e.g., Heavy rain, low visibility"}),
            "analysis_findings": forms.Textarea(attrs={"rows": 4, "placeholder": "Key findings from fault analysis"}),
            "root_cause": forms.Textarea(attrs={"rows": 4, "placeholder": "Confirmed or suspected root cause"}),
            "resolution_action": forms.Textarea(attrs={"rows": 4, "placeholder": "Corrective action taken"}),
            "ai_explanation": forms.Textarea(attrs={"rows": 5, "placeholder": "AI explanation output"}),
            "severity_score": forms.NumberInput(attrs={"min": 1, "max": 10, "placeholder": "1 = Low, 10 = Critical"}),
            "resolution_time_hours": forms.NumberInput(attrs={"step": "0.1", "min": 0, "placeholder": "e.g., 4.5"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()

        self.fields["title"].widget.attrs.setdefault("autocomplete", "off")
        self.fields["description"].widget.attrs.setdefault("style", "resize: vertical;")
