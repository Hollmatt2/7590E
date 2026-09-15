"""Load Calder's playbook, the provisions the system looks for, from seed/playbook.csv.

    python manage.py load_playbook

Each row names a provision, the CUAD category it matches, its default severity, and its definition
(CUAD's own description of the category). If a row's definition is empty, it is read from the CUAD
dataset when that is in data/cuad/. The CSV is the source of truth: running this again updates the
same provisions to match it. docs/playbook-maintenance.md explains how to change the playbook.
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
            if severity not in Severity.values:
                raise CommandError(f"{name}: severity must be one of {', '.join(Severity.values)}, not {severity!r}")
            if descriptions and category not in descriptions:
                self.stdout.write(self.style.WARNING(f"{name}: {category!r} is not a CUAD category"))
            definition = (row.get("definition") or "").strip() or descriptions.get(category, "")
            _, created = Provision.objects.update_or_create(
                name=name,
                defaults={"cuad_category": category, "default_severity": severity, "definition": definition},
            )
            self.stdout.write(f"{'Added' if created else 'Updated'} {name}")
