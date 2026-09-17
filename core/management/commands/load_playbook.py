"""Load Calder's playbook, the provisions the system looks for, from seed/playbook.csv.

    python manage.py load_playbook

Each row names a provision, the CUAD category it matches, its default severity, how the system looks
for it ("rules" for a text rule, "ai" for the AI step), and its definition (CUAD's description of the
category). If a row's definition is empty, it is read from the CUAD dataset when that is in data/cuad/.
The CSV is the source of truth: running this again updates the same provisions to match it.
docs/playbook-maintenance.md explains how to change the playbook.
"""
import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.cuad import CUAD_JSON, category_summary
from core.models import Provision, Severity

PLAYBOOK = settings.BASE_DIR / "seed" / "playbook.csv"


class Command(BaseCommand):
    help = "Create or update the playbook provisions listed in seed/playbook.csv."

    def handle(self, *args, **options):
        with PLAYBOOK.open(newline="") as f:
            rows = list(csv.DictReader(f))
        descriptions = {}
        if CUAD_JSON.exists():
            descriptions = {category: info[2] for category, info in category_summary()[1].items()}

        for row in rows:
            name, category = row["name"].strip(), row["cuad_category"].strip()
            severity = row["default_severity"].strip().lower()
            method = (row.get("method") or "ai").strip().lower()
            if severity not in Severity.values:
                raise CommandError(f"{name}: severity must be one of {', '.join(Severity.values)}, not {severity!r}")
            if method not in Provision.Method.values:
                raise CommandError(f"{name}: method must be one of {', '.join(Provision.Method.values)}, not {method!r}")
            if descriptions and category not in descriptions:
                self.stdout.write(self.style.WARNING(f"{name}: {category!r} is not a CUAD category"))
            definition = (row.get("definition") or "").strip() or descriptions.get(category, "")
            # Keywords are semicolon-separated in the CSV and stored one per line.
            keywords = "\n".join(k.strip() for k in (row.get("keywords") or "").split(";") if k.strip())
            # Agreement types are semicolon-separated in the CSV; empty means every type.
            types = ",".join(t.strip() for t in (row.get("agreement_types") or "").split(";") if t.strip())
            _, created = Provision.objects.update_or_create(
                name=name,
                defaults={"cuad_category": category, "default_severity": severity, "method": method,
                          "definition": definition, "keywords": keywords, "agreement_types": types},
            )
            self.stdout.write(f"{'Added' if created else 'Updated'} {name} ({method})")

        # The CSV is the source of truth, so a provision it no longer lists leaves the playbook.
        # One that already has findings against it stays, because deleting it would delete review history.
        listed = {row["name"].strip() for row in rows}
        for provision in Provision.objects.exclude(name__in=listed):
            if provision.flags.exists():
                self.stdout.write(self.style.WARNING(
                    f"{provision.name}: no longer in the playbook, but it has findings, so it was kept."))
            else:
                provision.delete()
                self.stdout.write(f"Removed {provision.name}, no longer in the playbook")
