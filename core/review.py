"""The review rules, workflow stages 7 to 9: decide each flag, record the agreement's outcome, keep the record.

Decisions and outcomes are only ever added, never edited, so together they are the audit record.
"""
from django.db import transaction

from .models import Agreement, Disposition, Flag, FlagDecision

# A decision on a flag sets the flag's status to match.
STATUS_AFTER = {
    FlagDecision.Action.ACCEPT: Flag.Status.ACCEPTED,
    FlagDecision.Action.DISMISS: Flag.Status.DISMISSED,
    FlagDecision.Action.ESCALATE: Flag.Status.ESCALATED,
}


class ReviewError(Exception):
    """A review step the rules do not allow right now. The message is shown to the user."""


def record_decision(flag, user, action, reason):
    """Add a decision on one flag. An earlier decision stays in the record; the newest one counts."""
    action = FlagDecision.Action(action)
    with transaction.atomic():
        decision = FlagDecision.objects.create(flag=flag, decided_by=user, action=action, reason=reason)
        flag.status = STATUS_AFTER[action]
        flag.save(update_fields=["status"])
    return decision


def undecided_count(agreement):
    """How many of the agreement's flags nobody has decided yet."""
    return agreement.flags.filter(status=Flag.Status.OPEN).count()


def allowed_outcomes(agreement):
    """The outcomes that may be recorded now."""
    Outcome = Disposition.Outcome
    if agreement.status == Agreement.Status.ESCALATED:
        return [Outcome.CLEARED, Outcome.CLEARED_WITH_CONDITIONS]  # the approver's final decision
    if agreement.flags.filter(status=Flag.Status.ESCALATED).exists():
        return [Outcome.ESCALATED]  # an escalated finding means the approver must see the agreement
    return [Outcome.CLEARED, Outcome.CLEARED_WITH_CONDITIONS, Outcome.ESCALATED]


def record_disposition(agreement, user, outcome, conditions=""):
    """Record the agreement's outcome and move it to the matching status."""
    if undecided_count(agreement):
        raise ReviewError("Decide every finding before recording the outcome.")
    if outcome not in allowed_outcomes(agreement):
        raise ReviewError("That outcome is not available for this agreement right now.")
    with transaction.atomic():
        # Change the status only if nobody else recorded an outcome in the meantime.
        moved = Agreement.objects.filter(pk=agreement.pk, status=agreement.status).update(status=outcome)
        if not moved:
            raise ReviewError("Someone else recorded an outcome for this agreement first.")
        return Disposition.objects.create(agreement=agreement, decided_by=user, outcome=outcome, conditions=conditions)


def audit_history(agreement):
    """Everything people did to this agreement, oldest first, as (when, who, what, reason) rows."""
    events = []
    for flag in agreement.flags.filter(created_by__isnull=False).select_related("provision", "created_by"):
        events.append((flag.created_at, flag.created_by.username, f"Marked {flag.provision} present", ""))
    decisions = FlagDecision.objects.filter(flag__agreement=agreement).select_related("flag__provision", "decided_by")
    for decision in decisions:
        what = f"{decision.get_action_display()}: {decision.flag.provision}"
        events.append((decision.decided_at, decision.decided_by.username, what, decision.reason))
    for disposition in agreement.dispositions.select_related("decided_by"):
        what = f"Outcome: {disposition.get_outcome_display()}"
        events.append((disposition.decided_at, disposition.decided_by.username, what, disposition.conditions))
    return sorted(events, key=lambda event: event[0])
