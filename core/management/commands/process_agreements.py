"""Read every agreement that is waiting to be read, then run automatic identification on it.

Run once:        python manage.py process_agreements
Keep running:    python manage.py process_agreements --watch

The web app never reads documents itself. Submitting only saves the file, and this command
does the slow part separately, so a large PDF can never make the submit page hang
(Change Notice 1: "submission and analysis cannot live in the same request").
"""
import time

from django.core.management.base import BaseCommand

from core.auto_identify import identify_automatically
from core.models import Agreement
from core.reading import read_agreement


class Command(BaseCommand):
    help = "Read submitted agreements, split them into clauses, and run automatic identification."

    def add_arguments(self, parser):
        parser.add_argument("--watch", action="store_true", help="Keep checking for new submissions.")
        parser.add_argument("--every", type=int, default=10, help="Seconds between checks when watching.")

    def handle(self, *args, watch, every, **options):
        while True:
            self.process_waiting_agreements()
            if not watch:
                break
            time.sleep(every)

    def process_waiting_agreements(self):
        waiting = Agreement.objects.filter(status=Agreement.Status.SUBMITTED).order_by("submitted_at")
        for agreement_id in waiting.values_list("pk", flat=True):
            agreement = read_agreement(agreement_id)
            if agreement is None:
                continue  # another worker took it first
            if agreement.status == Agreement.Status.READ_FAILED:
                self.stdout.write(self.style.WARNING(f"{agreement}: could not read. {agreement.read_error}"))
                continue
            identify_automatically(agreement)
            found = agreement.flags.count()
            self.stdout.write(
                f"{agreement}: {agreement.clauses.count()} clauses, {found} automatic finding{'' if found == 1 else 's'}, "
                f"now {agreement.get_status_display().lower()}"
            )
