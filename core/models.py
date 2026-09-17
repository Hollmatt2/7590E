from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Someone who can log in. Django's built-in user, plus a role."""

    class Role(models.TextChoices):
        REQUESTER = "requester", "Requester"
        REVIEWER = "reviewer", "Reviewer"
        APPROVER = "approver", "Approver"
        ADMIN = "admin", "Administrator"

    role = models.CharField(max_length=20, choices=Role, default=Role.REQUESTER)


class Severity(models.TextChoices):
    """How much attention a finding needs. Shared by playbook entries and flags."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Provision(models.Model):
    """One entry in Calder's playbook: a type of contract term the system looks for."""

    class Method(models.TextChoices):
        RULES = "rules", "Text rule"
        AI = "ai", "AI model"

    name = models.CharField(max_length=100, unique=True)  # e.g. "Cap on liability"
    cuad_category = models.CharField(max_length=100, blank=True)  # the matching CUAD label, used when testing
    definition = models.TextField(blank=True)  # what counts as this kind of clause
    # How serious it is when a contract contains this provision. New flags start at this severity.
    default_severity = models.CharField(max_length=10, choices=Severity, default=Severity.MEDIUM)
    # How the system looks for it automatically: the brief's rules-versus-model split (section 9).
    method = models.CharField(max_length=10, choices=Method, default=Method.AI)

    # Which agreement types this provision applies to, as a comma-separated list of Agreement.AgreementType
    # codes. Empty means every type. This is the per-agreement-type playbook (ambiguity log, question 3).
    agreement_types = models.CharField(max_length=200, blank=True)

    # Words an administrator wants looked for as well, one per line. They run whatever the method is,
    # so a category the AI is weak at (uncapped liability) still gets a text pass. A word matches the
    # start of a longer word too, so "indemnif" finds "indemnification".
    keywords = models.TextField(blank=True)

    # Stretch work since Change Notice 1 (9/9): comparing against standard positions, and gap detection.
    # Kept so that work has a place to go later. Nothing in the required workflow uses these two fields.
    standard_position = models.TextField(blank=True)  # the version Calder accepts
    required = models.BooleanField(default=False)  # if a contract lacks it, raise a "gap" flag

    def types(self):
        """The agreement type codes this provision applies to, or an empty list meaning all of them."""
        return [code.strip() for code in self.agreement_types.split(",") if code.strip()]

    def applies_to(self, agreement_type):
        """True if this provision is looked for in agreements of that type."""
        codes = self.types()
        return not codes or agreement_type in codes

    def __str__(self):
        return self.name


class Configuration(models.Model):
    """The settings an administrator changes without a deployment (brief, section 3: "configure thresholds").

    One row, read through core.config.current(). The environment variables set its starting values.
    """

    ai_low_confidence = models.FloatField(default=0.9)  # AI findings below this are marked and listed last
    document_retention_days = models.PositiveIntegerField(default=0)  # 0 keeps documents until told otherwise
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configuration"

    def save(self, *args, **kwargs):
        # There is only ever one row: saving a second one updates the first instead of failing.
        self.pk = 1
        kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuration"


class Agreement(models.Model):
    """A contract someone submitted for review."""

    class AgreementType(models.TextChoices):
        SOFTWARE = "software", "Software subscription"
        SERVICES = "services", "Professional services"
        LICENSING = "licensing", "Licensing"
        LOGISTICS = "logistics", "Logistics"
        DATA_PROCESSING = "dpa", "Data processing addendum"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"  # saved; the document has not been read yet
        PROCESSING = "processing", "Reading document"  # text extraction and segmentation are running
        READ_FAILED = "read_failed", "Could not read document"  # extraction failed; a person must look
        AWAITING_IDENTIFICATION = "awaiting_id", "Waiting for identification"  # clauses ready, provisions not marked
        IN_REVIEW = "in_review", "In review"  # flags exist and a reviewer is working them
        CLEARED = "cleared", "Cleared"
        CLEARED_WITH_CONDITIONS = "cleared_conditions", "Cleared with conditions"
        ESCALATED = "escalated", "Escalated"

    vendor = models.CharField(max_length=200)
    agreement_type = models.CharField(max_length=20, choices=AgreementType)
    business_unit = models.CharField(max_length=100)
    needed_by = models.DateField()
    document = models.FileField(upload_to="agreements/", blank=True)
    # Set when the file is deleted under the retention rule. The record of the review stays.
    document_removed_at = models.DateTimeField(null=True, blank=True)
    extracted_text = models.TextField(blank=True)  # filled in after the document is read
    read_error = models.TextField(blank=True)  # why reading failed, in words a reviewer can act on
    status = models.CharField(max_length=20, choices=Status, default=Status.SUBMITTED)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_agreements"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor} ({self.get_agreement_type_display()})"


class Clause(models.Model):
    """One piece of an agreement's text, after the text has been split up."""

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="clauses")
    position = models.PositiveIntegerField()  # 1 = first clause in the document
    text = models.TextField()

    class Meta:
        ordering = ["agreement", "position"]

    def __str__(self):
        return f"{self.agreement}, clause {self.position}"


class Flag(models.Model):
    """A finding for a reviewer: a playbook provision found in an agreement, with the text that shows it."""

    class Kind(models.TextChoices):
        PRESENT = "present", "Provision found"  # the required kind since Change Notice 1
        # Stretch kinds, not used by the required workflow:
        DEVIATION = "deviation", "Deviation"  # present, but differs from the standard position
        GAP = "gap", "Gap"  # the playbook expects it, and it is not there

    class Source(models.TextChoices):
        RULE = "rule", "Text rule"
        KEYWORD = "keyword", "Playbook keyword"
        AI = "ai", "AI model"
        MANUAL = "manual", "Marked by a person"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACCEPTED = "accepted", "Accepted"
        DISMISSED = "dismissed", "Dismissed"
        ESCALATED = "escalated", "Escalated"

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="flags")
    provision = models.ForeignKey(Provision, on_delete=models.PROTECT, related_name="flags")
    # The clause that triggered the flag. Empty for a gap, because there is no clause to point at.
    clause = models.ForeignKey(
        Clause, on_delete=models.SET_NULL, null=True, blank=True, related_name="flags"
    )
    kind = models.CharField(max_length=20, choices=Kind, default=Kind.PRESENT)
    severity = models.CharField(max_length=10, choices=Severity)
    source_text = models.TextField(blank=True)  # the exact words that triggered the flag
    reason = models.TextField()
    # 0.0 (a guess) to 1.0 (certain), from the AI model. Empty for flags from a person or a text rule.
    confidence = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=10, choices=Source)
    status = models.CharField(max_length=20, choices=Status, default=Status.OPEN)
    # The person who marked it, for flags made by hand. Empty for flags from a text rule or the AI.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="flags_marked"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # The database itself refuses a confidence below 0 or above 1.
            models.CheckConstraint(
                condition=models.Q(confidence__isnull=True) | models.Q(confidence__gte=0, confidence__lte=1),
                name="flag_confidence_between_0_and_1",
            ),
        ]

    @property
    def is_low_confidence(self):
        """True for an AI finding below the administrator's threshold. Such findings are marked and listed last."""
        from .config import low_confidence_threshold  # imported here because config reads this module

        return self.confidence is not None and self.confidence < low_confidence_threshold()

    def __str__(self):
        return f"{self.get_kind_display()}: {self.provision} in {self.agreement}"


class FlagDecision(models.Model):
    """One reviewer decision on one flag.

    Rows are only ever added, never changed, so this table is the audit record.
    PROTECT stops anyone from deleting a flag that has a decision recorded against it.
    """

    class Action(models.TextChoices):
        ACCEPT = "accept", "Accept"
        DISMISS = "dismiss", "Dismiss"
        ESCALATE = "escalate", "Escalate"

    flag = models.ForeignKey(Flag, on_delete=models.PROTECT, related_name="decisions")
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=10, choices=Action)
    reason = models.TextField()
    decided_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decided_by} chose {self.get_action_display()} on {self.flag}"


class Disposition(models.Model):
    """The final outcome of one review of an agreement. Also add-only."""

    class Outcome(models.TextChoices):
        CLEARED = "cleared", "Cleared"
        CLEARED_WITH_CONDITIONS = "cleared_conditions", "Cleared with conditions"
        ESCALATED = "escalated", "Escalated"

    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT, related_name="dispositions")
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    outcome = models.CharField(max_length=20, choices=Outcome)
    conditions = models.TextField(blank=True)  # the terms attached when cleared with conditions
    decided_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agreement}: {self.get_outcome_display()}"


class AgreementNote(models.Model):
    """A reviewer's note about an agreement as a whole (brief, section 3: a Reviewer can "add notes").

    Add-only, like decisions, and never shown to a Requester (ambiguity log question 6).
    """

    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name="notes")
    written_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    text = models.TextField()
    written_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["written_at"]

    def __str__(self):
        return f"Note by {self.written_by} on {self.agreement}"
