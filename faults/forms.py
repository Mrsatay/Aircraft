from django import forms
from django.contrib.auth.models import User

from .models import Fault


COMMON_SUBSYSTEM_CHOICES = [
    ("", "Select subsystem"),
    ("Engine", "Engine"),
    ("Electrical", "Electrical"),
    ("Avionics", "Avionics"),
    ("Hydraulics", "Hydraulics"),
    ("Landing Gear", "Landing Gear"),
    ("Flight Controls", "Flight Controls"),
    ("Fuel", "Fuel"),
    ("Environmental Control", "Environmental Control"),
    ("Navigation", "Navigation"),
    ("Communication", "Communication"),
    ("Other", "Other"),
]


COMPONENT_OPTIONS_BY_SUBSYSTEM = {
    "Engine": [
        "Engine Control Unit",
        "Fuel Injector",
        "Oil Pump",
        "Starter Motor",
        "Thrust Reverser",
    ],
    "Electrical": [
        "Generator Control Unit",
        "Battery Bus",
        "Wiring Harness",
        "Circuit Breaker",
        "Power Distribution Panel",
    ],
    "Avionics": [
        "Flight Management Computer",
        "FMS CDU",
        "Data Concentrator Unit",
        "PFD Display Unit",
        "IRS Unit",
    ],
    "Hydraulics": [
        "Hydraulic Pump A",
        "Hydraulic Pump B",
        "Pressure Manifold",
        "Actuator Return Line",
        "Reservoir",
    ],
    "Landing Gear": [
        "Main Landing Gear",
        "Nose Landing Gear",
        "Landing Gear Actuator",
        "Brake Assembly",
        "Wheel Speed Sensor",
    ],
    "Flight Controls": [
        "Aileron Actuator",
        "Elevator Servo",
        "Spoiler Control Module",
        "Rudder Actuator",
        "Flap Control Unit",
    ],
    "Fuel": [
        "Boost Pump",
        "Crossfeed Valve",
        "Fuel Quantity Sensor",
        "Fuel Quantity Indication System",
        "Fuel Control Valve",
    ],
    "Environmental Control": [
        "Pack Controller",
        "Cabin Pressure Valve",
        "Temperature Sensor",
        "Air Cycle Machine",
        "Bleed Air Valve",
    ],
    "Navigation": [
        "GPS Receiver",
        "VOR Antenna",
        "IRS Unit",
        "Navigation Computer",
        "Radio Altimeter",
    ],
    "Communication": [
        "VHF Radio",
        "HF Radio",
        "Audio Control Panel",
        "Transponder",
        "Antenna Coupler",
    ],
}

ALL_COMPONENT_CHOICES = [("", "Select component")]
for _subsystem, _components in COMPONENT_OPTIONS_BY_SUBSYSTEM.items():
    ALL_COMPONENT_CHOICES.extend((component, component) for component in _components)
ALL_COMPONENT_CHOICES.append(("Other", "Other"))


class FaultForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role__in=["Test Engineer", "Maintenance Engineer"]).order_by("username"),
        required=False,
        empty_label="Unassigned",
    )
    subsystem = forms.ChoiceField(choices=COMMON_SUBSYSTEM_CHOICES)
    subsystem_other = forms.CharField(
        required=False,
        label="Other Subsystem",
        widget=forms.TextInput(attrs={"placeholder": "Enter subsystem name"}),
    )
    component_affected = forms.ChoiceField(choices=ALL_COMPONENT_CHOICES, required=False)
    component_affected_other = forms.CharField(
        required=False,
        label="Other Component",
        widget=forms.TextInput(attrs={"placeholder": "Enter component name"}),
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
        self.fields["subsystem_other"].widget.attrs.setdefault("autocomplete", "off")
        self.fields["component_affected_other"].widget.attrs.setdefault("autocomplete", "off")

        if self.instance and self.instance.pk:
            current_subsystem = self.instance.subsystem
            common_values = {value for value, _label in COMMON_SUBSYSTEM_CHOICES}
            if current_subsystem in common_values:
                self.initial["subsystem"] = current_subsystem
            else:
                self.initial["subsystem"] = "Other"
                self.initial["subsystem_other"] = current_subsystem

            current_component = self.instance.component_affected
            known_components = {
                component
                for components in COMPONENT_OPTIONS_BY_SUBSYSTEM.values()
                for component in components
            }
            if current_component in known_components:
                self.initial["component_affected"] = current_component
            elif current_component:
                self.initial["component_affected"] = "Other"
                self.initial["component_affected_other"] = current_component

        component_initial = (
            self.data.get(self.add_prefix("component_affected"))
            if self.is_bound
            else self.initial.get("component_affected", "")
        )
        self.fields["component_affected"].widget.attrs["data-initial-value"] = component_initial or ""

    def clean(self):
        cleaned_data = super().clean()
        subsystem = cleaned_data.get("subsystem", "").strip()
        subsystem_other = cleaned_data.get("subsystem_other", "").strip()
        component = cleaned_data.get("component_affected", "").strip()
        component_other = cleaned_data.get("component_affected_other", "").strip()

        if subsystem == "Other":
            if not subsystem_other:
                self.add_error("subsystem_other", "Enter the subsystem name when Other is selected.")
            else:
                cleaned_data["subsystem"] = subsystem_other
        elif not subsystem:
            self.add_error("subsystem", "Select a subsystem.")

        if component == "Other":
            if not component_other:
                self.add_error("component_affected_other", "Enter the component name when Other is selected.")
            else:
                cleaned_data["component_affected"] = component_other
        elif component and subsystem in COMPONENT_OPTIONS_BY_SUBSYSTEM:
            allowed_components = COMPONENT_OPTIONS_BY_SUBSYSTEM[subsystem]
            if component not in allowed_components:
                self.add_error("component_affected", "Select a component that matches the selected subsystem.")

        return cleaned_data
