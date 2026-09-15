"""Views: each function receives a web request and returns the page to show."""
from statistics import median

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Min, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AgreementForm, DecisionForm, DispositionForm, FindingForm
from .models import Agreement, Flag, Provision
from .permissions import REVIEW_ROLES, STAFF_ROLES, can_review, can_view_agreement, role_required
from .review import (
    ReviewError, allowed_outcomes, audit_history, record_decision, record_disposition, undecided_count,
)

# The work queue's sections, in order: a heading, and the statuses listed under it.
QUEUE_SECTIONS = [
    ("Waiting for identification", [Agreement.Status.AWAITING_IDENTIFICATION]),
    ("In review", [Agreement.Status.IN_REVIEW]),
    ("Escalated", [Agreement.Status.ESCALATED]),
    ("Could not read the document", [Agreement.Status.READ_FAILED]),
    ("Not read yet", [Agreement.Status.SUBMITTED, Agreement.Status.PROCESSING]),
]


def home(request):
    """The public landing page. Logged-in users go straight to their starting page."""
    if request.user.is_authenticated:
        return redirect("work_queue" if request.user.role in STAFF_ROLES else "my_submissions")
    return render(request, "core/home.html")


@login_required
def submit_agreement(request):
    """Intake, workflow stage 1: the agreement's details and the document itself."""
    if request.method == "POST":
        form = AgreementForm(request.POST, request.FILES)
        if form.is_valid():
            agreement = form.save(commit=False)
            agreement.submitted_by = request.user
            agreement.save()
            # The document is read later, outside this request (Change Notice 1). It starts as "Submitted".
            messages.success(request, f"Submitted {agreement.vendor}. It is waiting to be read.")
            return redirect("agreement_detail", pk=agreement.pk)
    else:
        form = AgreementForm()
    return render(request, "core/submit.html", {"form": form})


@login_required
def my_submissions(request):
    """Every agreement this user has submitted, newest first, with its status."""
    agreements = Agreement.objects.filter(submitted_by=request.user).order_by("-submitted_at")
    return render(request, "core/my_submissions.html", {"agreements": agreements})


@login_required
def agreement_detail(request, pk):
    """One agreement: details, outcome, findings, history and clauses. Requesters can open only their own."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if not can_view_agreement(request.user, agreement):
        raise PermissionDenied
    # Requesters see the status and the outcome, not the findings. This is a default; see the ambiguity log.
    show_findings = request.user.role in STAFF_ROLES
    return render(request, "core/agreement_detail.html", {
        "agreement": agreement,
        "show_findings": show_findings,
        "history": audit_history(agreement) if show_findings else [],
        "can_identify": (
            request.user.role in REVIEW_ROLES and agreement.status == Agreement.Status.AWAITING_IDENTIFICATION
        ),
        "can_review": can_review(request.user, agreement),
    })


@login_required
def agreement_document(request, pk):
    """Send the uploaded file after the same permission check. Documents are never public (brief, section 3)."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if not can_view_agreement(request.user, agreement):
        raise PermissionDenied
    filename = agreement.document.name.rsplit("/", 1)[-1]
    return FileResponse(agreement.document.open("rb"), filename=filename)


@role_required(*STAFF_ROLES)
def work_queue(request):
    """Every agreement that still needs someone, grouped by what it is waiting for, most urgent first."""
    statuses = [status for _, group in QUEUE_SECTIONS for status in group]
    open_agreements = list(Agreement.objects.filter(status__in=statuses).order_by("needed_by"))
    sections = [
        (heading, [agreement for agreement in open_agreements if agreement.status in group])
        for heading, group in QUEUE_SECTIONS
    ]
    return render(request, "core/queue.html", {"sections": sections})


def save_manual_finding(form, agreement, user, default_reason):
    """Save a finding a person entered: marked present by that person, severity from the playbook entry."""
    flag = form.save(commit=False)
    flag.agreement = agreement
    flag.kind = Flag.Kind.PRESENT
    flag.source = Flag.Source.MANUAL
    flag.severity = flag.provision.default_severity
    flag.reason = flag.reason or default_reason
    flag.created_by = user
    flag.save()
    return flag


@role_required(*REVIEW_ROLES)
def identify(request, pk):
    """Manual identification, workflow stage 3: a reviewer marks which playbook provisions the
    agreement contains and pastes the words that show each one. Automatic findings are listed too."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if agreement.status != Agreement.Status.AWAITING_IDENTIFICATION:
        messages.error(request, "This agreement is not waiting for identification.")
        return redirect("agreement_detail", pk=pk)

    form = FindingForm(request.POST or None, agreement=agreement)
    if request.method == "POST" and form.is_valid():
        flag = save_manual_finding(form, agreement, request.user, f"Marked present by {request.user.username}.")
        messages.success(request, f"Added {flag.provision} (clause {flag.clause.position}).")
        return redirect("identify", pk=pk)

    return render(request, "core/identify.html", {
        "agreement": agreement,
        "form": form,
        "clauses": agreement.clauses.all(),
        "findings": agreement.flags.select_related("provision", "clause"),
    })


@require_POST
@role_required(*REVIEW_ROLES)
def remove_finding(request, pk, flag_pk):
    """Undo a finding added by mistake. Only allowed before review starts."""
    flag = get_object_or_404(Flag, pk=flag_pk, agreement_id=pk)
    if flag.agreement.status != Agreement.Status.AWAITING_IDENTIFICATION:
        raise PermissionDenied  # once review starts, findings are part of the record
    flag.delete()
    messages.success(request, f"Removed {flag.provision}.")
    return redirect("identify", pk=pk)


@require_POST
@role_required(*REVIEW_ROLES)
def finish_identification(request, pk):
    """Send the agreement to review. From here on its findings are part of the record."""
    finished = Agreement.objects.filter(pk=pk, status=Agreement.Status.AWAITING_IDENTIFICATION).update(
        status=Agreement.Status.IN_REVIEW
    )
    if finished:
        messages.success(request, "Identification finished. The agreement is now in review.")
    return redirect("agreement_detail", pk=pk)


@login_required
def review(request, pk):
    """Review, workflow stages 7 and 8: decide each finding, then record the agreement's outcome."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if not can_review(request.user, agreement):
        raise PermissionDenied
    return render_review(request, agreement)


def render_review(request, agreement, bound_forms=None, disposition_form=None, finding_form=None):
    """Show the review page. Forms that failed their checks are passed in, so their errors show."""
    bound_forms = bound_forms or {}
    flags = agreement.flags.select_related("provision", "clause", "created_by").prefetch_related(
        "decisions__decided_by"
    )
    # Low-confidence AI findings are listed last (and marked in the page): the app's low-confidence behavior.
    flags = sorted(flags, key=lambda flag: flag.is_low_confidence)
    items = [(flag, bound_forms.get(flag.pk) or DecisionForm(prefix=f"flag{flag.pk}")) for flag in flags]
    return render(request, "core/review.html", {
        "agreement": agreement,
        "items": items,
        "undecided": undecided_count(agreement),
        "disposition_form": disposition_form or DispositionForm(outcomes=allowed_outcomes(agreement)),
        "finding_form": finding_form or FindingForm(agreement=agreement),
    })


@require_POST
@login_required
def decide_flag(request, pk, flag_pk):
    """Record one decision (accept, dismiss or escalate) on one finding, with its reason."""
    flag = get_object_or_404(Flag.objects.select_related("agreement", "provision"), pk=flag_pk, agreement_id=pk)
    if not can_review(request.user, flag.agreement):
        raise PermissionDenied
    form = DecisionForm(request.POST, prefix=f"flag{flag.pk}")
    if not form.is_valid():
        return render_review(request, flag.agreement, bound_forms={flag.pk: form})
    record_decision(flag, request.user, form.cleaned_data["action"], form.cleaned_data["reason"])
    messages.success(request, f"Recorded: {flag.provision}, {flag.get_status_display().lower()}.")
    return redirect("review", pk=pk)


@require_POST
@login_required
def add_missed_finding(request, pk):
    """During review, add a provision that identification missed. It starts open, like every other finding."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if not can_review(request.user, agreement):
        raise PermissionDenied
    form = FindingForm(request.POST, agreement=agreement)
    if not form.is_valid():
        return render_review(request, agreement, finding_form=form)
    flag = save_manual_finding(
        form, agreement, request.user, f"Added during review by {request.user.username}; identification missed it."
    )
    messages.success(request, f"Added {flag.provision}. Decide it like the other findings.")
    return redirect("review", pk=pk)


@require_POST
@login_required
def dispose(request, pk):
    """Record the outcome for the whole agreement: cleared, cleared with conditions, or escalated."""
    agreement = get_object_or_404(Agreement, pk=pk)
    if not can_review(request.user, agreement):
        raise PermissionDenied
    form = DispositionForm(request.POST, outcomes=allowed_outcomes(agreement))
    if not form.is_valid():
        return render_review(request, agreement, disposition_form=form)
    try:
        disposition = record_disposition(
            agreement, request.user, form.cleaned_data["outcome"], form.cleaned_data["conditions"]
        )
    except ReviewError as error:
        messages.error(request, str(error))
        return redirect("review", pk=pk)
    messages.success(request, f"Recorded the outcome: {disposition.get_outcome_display()}.")
    return redirect("agreement_detail", pk=pk)


@role_required(*STAFF_ROLES)
def reports(request):
    """Reporting, workflow stage 10. Procurement's three questions (brief section 2, as amended by
    Change Notice 1): how many agreements are in review, how long they have waited, and which
    provisions come up most often."""
    now = timezone.now()
    waiting = []
    for heading, statuses in QUEUE_SECTIONS:
        days = [
            (now - submitted).days
            for submitted in Agreement.objects.filter(status__in=statuses).values_list("submitted_at", flat=True)
        ]
        waiting.append({
            "stage": heading,
            "count": len(days),
            "median": median(days) if days else None,
            "longest": max(days) if days else None,
        })

    # Turnaround: days from submission to the first recorded outcome, for agreements that have one.
    finished = Agreement.objects.annotate(first_outcome=Min("dispositions__decided_at")).exclude(first_outcome=None)
    turnaround = [(agreement.first_outcome - agreement.submitted_at).days for agreement in finished]

    provisions = Provision.objects.annotate(
        found=Count("flags"),
        agreements=Count("flags__agreement", distinct=True),
        accepted=Count("flags", filter=Q(flags__status=Flag.Status.ACCEPTED)),
        dismissed=Count("flags", filter=Q(flags__status=Flag.Status.DISMISSED)),
        escalated=Count("flags", filter=Q(flags__status=Flag.Status.ESCALATED)),
    ).order_by("-found", "name")

    return render(request, "core/reports.html", {
        "waiting": waiting,
        "finished": len(turnaround),
        "median_turnaround": median(turnaround) if turnaround else None,
        "provisions": provisions,
    })
