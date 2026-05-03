import sqlite3
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction

from accounts.models import UserProfile
from aircraft.models import Aircraft
from faults.models import Fault, StatusHistory


class Command(BaseCommand):
    help = "Import existing data from the legacy SQLite database into the current configured database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sqlite-path",
            default="db.sqlite3",
            help="Path to the legacy SQLite database file. Defaults to db.sqlite3 in the project root.",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing application data in the target database before importing.",
        )

    def handle(self, *args, **options):
        sqlite_path = Path(options["sqlite_path"]).resolve()
        if not sqlite_path.exists():
            raise CommandError(f"SQLite database not found: {sqlite_path}")

        if not options["flush"] and self._target_has_data():
            raise CommandError(
                "Target database already contains application data. "
                "Run the command again with --flush if you want to replace it."
            )

        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row

        try:
            with transaction.atomic():
                if options["flush"]:
                    self._flush_target()

                self._import_users(sqlite_conn)
                self._import_profiles(sqlite_conn)
                self._import_aircraft(sqlite_conn)
                self._import_faults(sqlite_conn)
                self._import_status_history(sqlite_conn)
                self._reset_sequences()
        finally:
            sqlite_conn.close()

        self.stdout.write(self.style.SUCCESS("SQLite data import completed successfully."))

    def _target_has_data(self):
        return any(
            model.objects.exists()
            for model in [User, UserProfile, Aircraft, Fault, StatusHistory]
        )

    def _flush_target(self):
        StatusHistory.objects.all().delete()
        Fault.objects.all().delete()
        Aircraft.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True, username="postgres").delete()

    def _import_users(self, sqlite_conn):
        rows = sqlite_conn.execute(
            """
            SELECT id, password, last_login, is_superuser, username, first_name, last_name,
                   email, is_staff, is_active, date_joined
            FROM auth_user
            ORDER BY id
            """
        ).fetchall()

        for row in rows:
            user = User(
                id=row["id"],
                password=row["password"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                is_staff=bool(row["is_staff"]),
                is_active=bool(row["is_active"]),
                is_superuser=bool(row["is_superuser"]),
                last_login=row["last_login"],
                date_joined=row["date_joined"],
            )
            user.save(force_insert=True)

    def _import_profiles(self, sqlite_conn):
        rows = sqlite_conn.execute(
            "SELECT id, role, user_id FROM accounts_userprofile ORDER BY id"
        ).fetchall()

        for row in rows:
            profile = UserProfile(
                id=row["id"],
                user_id=row["user_id"],
                role=row["role"],
            )
            profile.save(force_insert=True)

    def _import_aircraft(self, sqlite_conn):
        rows = sqlite_conn.execute(
            """
            SELECT id, tail_number, model, manufacturer, current_status
            FROM aircraft_aircraft
            ORDER BY id
            """
        ).fetchall()

        for row in rows:
            aircraft = Aircraft(
                id=row["id"],
                tail_number=row["tail_number"],
                model=row["model"],
                manufacturer=row["manufacturer"],
                current_status=row["current_status"],
            )
            aircraft.save(force_insert=True)

    def _import_faults(self, sqlite_conn):
        rows = sqlite_conn.execute(
            """
            SELECT id, title, description, aircraft_id, reported_by_id, assigned_to_id, subsystem,
                   severity, current_status, reported_date, closed_date, closed_by_id,
                   analysis_findings, root_cause, resolution_action, severity_score,
                   resolution_time_hours, component_affected, environmental_conditions,
                   flight_phase, ai_explanation
            FROM faults_fault
            ORDER BY id
            """
        ).fetchall()

        for row in rows:
            fault = Fault(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                aircraft_id=row["aircraft_id"],
                reported_by_id=row["reported_by_id"],
                assigned_to_id=row["assigned_to_id"],
                subsystem=row["subsystem"],
                severity=row["severity"],
                current_status=row["current_status"],
                reported_date=row["reported_date"],
                closed_date=row["closed_date"],
                closed_by_id=row["closed_by_id"],
                analysis_findings=row["analysis_findings"],
                root_cause=row["root_cause"],
                resolution_action=row["resolution_action"],
                severity_score=row["severity_score"],
                resolution_time_hours=row["resolution_time_hours"],
                component_affected=row["component_affected"],
                environmental_conditions=row["environmental_conditions"],
                flight_phase=row["flight_phase"],
                ai_explanation=row["ai_explanation"],
            )
            fault.save(force_insert=True)

    def _import_status_history(self, sqlite_conn):
        rows = sqlite_conn.execute(
            """
            SELECT id, fault_id, old_status, new_status, changed_by_id, change_notes, change_timestamp
            FROM faults_statushistory
            ORDER BY id
            """
        ).fetchall()

        for row in rows:
            history = StatusHistory(
                id=row["id"],
                fault_id=row["fault_id"],
                old_status=row["old_status"],
                new_status=row["new_status"],
                changed_by_id=row["changed_by_id"],
                change_notes=row["change_notes"],
                change_timestamp=row["change_timestamp"],
            )
            history.save(force_insert=True)

    def _reset_sequences(self):
        models = [User, UserProfile, Aircraft, Fault, StatusHistory]
        statements = connection.ops.sequence_reset_sql(no_style(), models)
        if not statements:
            return
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
