"""Delete the uploaded file of agreements whose review finished longer ago than the retention setting.

    python manage.py purge_documents            # delete what is due
    python manage.py purge_documents --dry-run  # list what would go

The retention period is an administrator setting (Configuration.document_retention_days, on the admin
screen). 0 means keep documents until an administrator sets a period, which is the default: see the
ambiguity log, question 5. The review record, its findings and its decisions are never deleted; only the
file goes, and the agreement page then says when it went.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.config import retention_days
from core.models import Agreement

FINISHED = [Agreement.Status.CLEARED, Agreement.Status.CLEARED_WITH_CONDITIONS, Agreement.Status.ESCALATED]


class Command(BaseCommand):
    help = "Delete uploaded files kept longer than the retention setting allows."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="List the files instead of deleting them.")

    def handle(self, *args, **options):
        days = retention_days()
        if not days:
            self.stdout.write("Retention is 0 days, which means keep documents. Nothing to do.")
            return
        cutoff = timezone.now() - timedelta(days=days)
        due = [
            agreement
            for agreement in Agreement.objects.filter(status__in=FINISHED).exclude(document="")
            if (agreement.dispositions.last() and agreement.dispositions.last().decided_at < cutoff)
        ]
        for agreement in due:
            if options["dry_run"]:
                self.stdout.write(f"Would delete the file of {agreement}")
                continue
            agreement.document.delete(save=False)
            agreement.document = ""
            agreement.document_removed_at = timezone.now()
            agreement.save(update_fields=["document", "document_removed_at"])
            self.stdout.write(f"Deleted the file of {agreement}; the record remains")
        self.stdout.write(f"{len(due)} agreement(s) past the {days}-day retention period.")
