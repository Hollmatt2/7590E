"""Automatic identification: workflow stage 3 without a person. Text rules now; the AI model next.

After a document is read, this runs the automatic methods over its clauses and saves what they find
as flags. If every playbook provision has an automatic method, the agreement goes straight to review.
Otherwise it waits on the manual identification screen, where the automatic findings are already
listed and a person adds the rest. Either way, a person decides on every flag (brief, section 5).
"""
from django.conf import settings
from django.db import transaction

from .models import Agreement, Flag, Provision
from .rules import COMPILED, find_with_rules


def identify_automatically(agreement):
    """Add automatic findings to an agreement that is waiting for identification. Runs once per agreement."""
    if "rules" not in settings.AUTO_IDENTIFY:
        return agreement
    if agreement.status != Agreement.Status.AWAITING_IDENTIFICATION:
        return agreement
    if agreement.flags.exclude(source=Flag.Source.MANUAL).exists():
        return agreement  # already done

    provisions = {provision.cuad_category: provision for provision in Provision.objects.all()}
    flags = []
    for clause in agreement.clauses.all():
        for category, sentence in find_with_rules(clause.text, provisions):
            provision = provisions[category]
            flags.append(Flag(
                agreement=agreement,
                provision=provision,
                clause=clause,
                kind=Flag.Kind.PRESENT,
                severity=provision.default_severity,
                source_text=sentence,
                reason=f"Matched the text rule for {provision.name}.",
                source=Flag.Source.RULE,
            ))
    every_provision_covered = all(category in COMPILED for category in provisions)

    with transaction.atomic():
        Flag.objects.bulk_create(flags)
        if every_provision_covered:
            agreement.status = Agreement.Status.IN_REVIEW
            agreement.save(update_fields=["status"])
    return agreement
