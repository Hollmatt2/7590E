"""Create the demonstration data: a login for each role, the playbook, and sample agreements (brief, section 8).

Run it with:  python manage.py seed_demo
Running it again is safe. It resets the four demo passwords, reloads the playbook, and adds any
sample agreement that is not there yet. The deployed site runs it every time it starts.
The sample contracts in seed/sample_contracts/ come from CUAD (CC BY 4.0).
"""
import os
from datetime import timedelta

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Agreement, User

DEMO_USERS = [
    ("requester", User.Role.REQUESTER),
    ("reviewer", User.Role.REVIEWER),
    ("approver", User.Role.APPROVER),
    ("admin", User.Role.ADMIN),
]

SAMPLES = settings.BASE_DIR / "seed" / "sample_contracts"
# File in seed/sample_contracts/, vendor, agreement type, business unit.
SAMPLE_AGREEMENTS = [
    ("opera-service-agreement.pdf", "Opera Ltd (CUAD sample)", Agreement.AgreementType.SERVICES, "Corporate office"),
    ("sphere3d-consulting-agreement.pdf", "Sphere 3D (CUAD sample)", Agreement.AgreementType.SERVICES, "Shared services"),
    ("hubei-minkang-outsourcing-agreement.pdf", "Hubei Minkang (CUAD sample)", Agreement.AgreementType.SERVICES,
     "Distribution center 2"),
    ("mossimo-endorsement-agreement.pdf", "Mossimo (CUAD sample)", Agreement.AgreementType.LICENSING, "Corporate office"),
]


class Command(BaseCommand):
    help = "Create or reset the demo logins, load the playbook, and add the sample agreements."

    def handle(self, *args, **options):
        # On the deployed site the password comes from an environment variable instead.
        password = os.environ.get("DEMO_PASSWORD", "calder-demo")
        for username, role in DEMO_USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"role": role})
            user.role = role
            # Only the administrator may open Django's built-in admin screens at /admin/.
            user.is_staff = user.is_superuser = role == User.Role.ADMIN
            user.set_password(password)
            user.save()
            self.stdout.write(f"{'Created' if created else 'Reset'} {username} ({role.label})")

        call_command("load_playbook", stdout=self.stdout)

        requester = User.objects.get(username="requester")
        for filename, vendor, agreement_type, business_unit in SAMPLE_AGREEMENTS:
            path = SAMPLES / filename
            if not path.exists() or Agreement.objects.filter(vendor=vendor).exists():
                continue
            with path.open("rb") as f:
                Agreement.objects.create(
                    vendor=vendor,
                    agreement_type=agreement_type,
                    business_unit=business_unit,
                    needed_by=timezone.localdate() + timedelta(days=14),
                    document=File(f, name=filename),
                    submitted_by=requester,
                )
            self.stdout.write(f"Added sample agreement {vendor}; process_agreements will read it")
