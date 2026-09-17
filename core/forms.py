"""The app's forms. Django builds the HTML fields and checks the input."""
from pathlib import Path

from django import forms
from django.conf import settings
from django.utils import timezone

from .models import Agreement, AgreementNote, Disposition, Flag, FlagDecision, Provision

# PDFs, plus plain text: the brief allows switching to the corpus's plain-text files (section 9).
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def squash(text):
    """Collapse every run of spaces and line breaks into one space, so line wrapping does not matter."""
    return " ".join(text.split())


class AgreementForm(forms.ModelForm):
    """Intake: the details of an agreement and the document itself."""

    class Meta:
        model = Agreement
        fields = ["vendor", "agreement_type", "business_unit", "needed_by", "document"]
        widgets = {"needed_by": forms.DateInput(attrs={"type": "date"})}  # the browser shows a date picker
        labels = {"needed_by": "Needed by"}

    def clean_needed_by(self):
        """Refuse a date that has already passed."""
        needed_by = self.cleaned_data["needed_by"]
        if needed_by < timezone.localdate():
            raise forms.ValidationError("The needed-by date is already past.")
        return needed_by

    def clean_document(self):
        """Refuse files that are the wrong type, too large, or not really PDFs."""
        document = self.cleaned_data["document"]
        extension = Path(document.name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Upload a PDF or a plain-text (.txt) file.")
        if document.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f"The file is larger than {settings.MAX_UPLOAD_MB} MB.")
        if extension == ".pdf":
            # Every real PDF starts with the bytes "%PDF". A Word file or image renamed to .pdf does not.
            first_bytes = document.read(5)
            document.seek(0)
            if not first_bytes.startswith(b"%PDF"):
                raise forms.ValidationError("That file is not a readable PDF.")
        return document


class FindingForm(forms.ModelForm):
    """Manual identification: one playbook provision found in one clause, with the exact words that show it."""

    class Meta:
        model = Flag
        fields = ["provision", "clause", "source_text", "reason"]
        labels = {
            "source_text": "Supporting text (copy the exact words from the clause)",
            "reason": "Note (optional)",
        }
        widgets = {
            "source_text": forms.Textarea(attrs={"rows": 4}),
            "reason": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, agreement, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provision"].queryset = Provision.objects.order_by("name")
        self.fields["clause"].queryset = agreement.clauses.all()  # only this agreement's clauses
        self.fields["clause"].required = True
        self.fields["clause"].label_from_instance = lambda clause: f"Clause {clause.position}"
        self.fields["source_text"].required = True
        self.fields["reason"].required = False

    def clean(self):
        """Refuse supporting text that is not in the chosen clause (brief, section 5: every finding
        must be traceable to a specific span of source text)."""
        cleaned = super().clean()
        clause, text = cleaned.get("clause"), cleaned.get("source_text")
        if clause and text and squash(text) not in squash(clause.text):
            raise forms.ValidationError(
                "That text does not appear in the chosen clause. Copy it exactly from the clause."
            )
        return cleaned


class DecisionForm(forms.Form):
    """A reviewer's decision on one finding. The reason is required, because the record must say why."""

    action = forms.ChoiceField(choices=FlagDecision.Action.choices, widget=forms.RadioSelect, label="Decision")
    reason = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), label="Reason")


class DispositionForm(forms.Form):
    """The outcome for the whole agreement. Only the outcomes the rules allow right now are offered."""

    outcome = forms.ChoiceField(widget=forms.RadioSelect)
    conditions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Required when clearing with conditions: what the requester must do or accept.",
    )

    def __init__(self, *args, outcomes, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["outcome"].choices = [(outcome.value, outcome.label) for outcome in outcomes]

    def clean(self):
        cleaned = super().clean()
        conditions = cleaned.get("conditions", "").strip()
        if cleaned.get("outcome") == Disposition.Outcome.CLEARED_WITH_CONDITIONS and not conditions:
            self.add_error("conditions", "Write the conditions the requester must meet.")
        return cleaned


class NoteForm(forms.ModelForm):
    """A reviewer's note about the agreement. Notes are added, never edited."""

    class Meta:
        model = AgreementNote
        fields = ["text"]
        labels = {"text": "Note"}
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}
