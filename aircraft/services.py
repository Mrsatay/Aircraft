from .models import Aircraft


def ensure_demo_aircraft():
    if Aircraft.objects.exists():
        return

    Aircraft.objects.bulk_create(
        [
            Aircraft(tail_number="PK-AF001", model="B737-800", manufacturer="Boeing", current_status="Testing"),
            Aircraft(tail_number="PK-AF009", model="A320neo", manufacturer="Airbus", current_status="Maintenance Review"),
            Aircraft(tail_number="PK-AF017", model="B777-300ER", manufacturer="Boeing", current_status="Operational"),
            Aircraft(tail_number="PK-AF021", model="ATR 72-600", manufacturer="ATR", current_status="Available"),
        ]
    )
