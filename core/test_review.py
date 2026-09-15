"""Checks for review, outcomes, the audit record and reports. Run them with:  python manage.py test"""
from django.db.models import ProtectedError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Agreement, Clause, Disposition, Flag, FlagDecision, Provision, Severity, User
from .templatetags.review_extras import highlight


class ReviewTests(TestCase):
    def setUp(self):
        self.requester = User.objects.create_user("req", password="pw", role=User.Role.REQUESTER)
        self.reviewer = User.objects.create_user("rev", password="pw", role=User.Role.REVIEWER)
        self.approver = User.objects.create_user("app", password="pw", role=User.Role.APPROVER)
        self.agreement = Agreement.objects.create(
            vendor="Acme",
            agreement_type=Agreement.AgreementType.SERVICES,
            business_unit="Corporate",
            needed_by=timezone.localdate(),
            document="agreements/acme.pdf",
            submitted_by=self.requester,
            status=Agreement.Status.IN_REVIEW,
        )
        clause = Clause.objects.create(
            agreement=self.agreement,
            position=1,
            text="Liability is capped at twelve months of fees. This Agreement is governed by Georgia law.",
        )
        self.cap, self.law = [
            Flag.objects.create(
                agreement=self.agreement,
                clause=clause,
                provision=Provision.objects.create(name=name),
                severity=Severity.MEDIUM,
                source_text=words,
                reason="Marked present.",
                source=Flag.Source.MANUAL,
                created_by=self.reviewer,
            )
            for name, words in [("Cap on liability", "capped at twelve months of fees"),
                                ("Governing law", "governed by Georgia law")]
        ]
        self.client.login(username="rev", password="pw")

    def decide(self, flag, action, reason="Checked against the clause."):
        prefix = f"flag{flag.pk}"
        return self.client.post(
            reverse("decide_flag", args=[self.agreement.pk, flag.pk]),
            {f"{prefix}-action": action, f"{prefix}-reason": reason},
        )

    def dispose(self, outcome, conditions=""):
        return self.client.post(reverse("dispose", args=[self.agreement.pk]), {"outcome": outcome, "conditions": conditions})

    def status(self):
        self.agreement.refresh_from_db()
        return self.agreement.status

    def test_a_decision_records_who_what_and_why(self):
        self.decide(self.cap, "accept", "Twelve months is acceptable.")
        decision = FlagDecision.objects.get()
        self.assertEqual(decision.decided_by, self.reviewer)
        self.assertEqual(decision.action, FlagDecision.Action.ACCEPT)
        self.assertEqual(decision.reason, "Twelve months is acceptable.")
        self.cap.refresh_from_db()
        self.assertEqual(self.cap.status, Flag.Status.ACCEPTED)

    def test_a_decision_needs_a_reason(self):
        response = self.decide(self.cap, "accept", reason="")
        self.assertEqual(response.status_code, 200)  # the review page comes back showing the error
        self.assertFalse(FlagDecision.objects.exists())

    def test_changing_a_decision_keeps_the_earlier_one(self):
        self.decide(self.cap, "accept")
        self.decide(self.cap, "dismiss", "On a second reading this is not a cap.")
        self.assertEqual(self.cap.decisions.count(), 2)
        self.cap.refresh_from_db()
        self.assertEqual(self.cap.status, Flag.Status.DISMISSED)

    def test_the_outcome_waits_until_every_finding_is_decided(self):
        self.decide(self.cap, "accept")
        self.dispose("cleared")
        self.assertEqual(self.status(), Agreement.Status.IN_REVIEW)
        self.assertFalse(Disposition.objects.exists())

    def test_clearing_with_conditions_needs_the_conditions(self):
        self.decide(self.cap, "accept")
        self.decide(self.law, "accept")
        self.dispose("cleared_conditions", conditions="")
        self.assertEqual(self.status(), Agreement.Status.IN_REVIEW)
        self.dispose("cleared_conditions", conditions="Add a renewal reminder 30 days before the deadline.")
        self.assertEqual(self.status(), Agreement.Status.CLEARED_WITH_CONDITIONS)
        self.assertEqual(Disposition.objects.get().conditions, "Add a renewal reminder 30 days before the deadline.")

    def test_an_escalated_finding_means_the_agreement_is_escalated(self):
        self.decide(self.cap, "escalate", "The cap may be too low for this vendor.")
        self.decide(self.law, "accept")
        self.dispose("cleared")
        self.assertEqual(self.status(), Agreement.Status.IN_REVIEW)  # clearing is not offered
        self.dispose("escalated")
        self.assertEqual(self.status(), Agreement.Status.ESCALATED)

    def test_only_the_approver_decides_an_escalated_agreement(self):
        Flag.objects.update(status=Flag.Status.ACCEPTED)
        Agreement.objects.filter(pk=self.agreement.pk).update(status=Agreement.Status.ESCALATED)
        self.assertEqual(self.dispose("cleared").status_code, 403)  # the reviewer is refused
        self.client.login(username="app", password="pw")
        self.dispose("cleared")
        self.assertEqual(self.status(), Agreement.Status.CLEARED)

    def test_nobody_reviews_an_agreement_they_submitted(self):
        Agreement.objects.filter(pk=self.agreement.pk).update(submitted_by=self.reviewer)
        self.assertEqual(self.client.get(reverse("review", args=[self.agreement.pk])).status_code, 403)

    def test_a_finding_with_decisions_cannot_be_deleted(self):
        self.decide(self.cap, "accept")
        with self.assertRaises(ProtectedError):
            self.cap.delete()

    def test_the_requester_sees_the_outcome_and_conditions_but_not_the_findings(self):
        self.decide(self.cap, "accept")
        self.decide(self.law, "accept")
        self.dispose("cleared_conditions", conditions="Add a renewal reminder 30 days before the deadline.")
        self.client.login(username="req", password="pw")
        page = self.client.get(reverse("agreement_detail", args=[self.agreement.pk]))
        self.assertContains(page, "Add a renewal reminder 30 days before the deadline.")
        self.assertNotContains(page, "Findings (")

    def test_reports_count_the_provisions_found_and_are_for_staff_only(self):
        self.assertContains(self.client.get(reverse("reports")), "<td>Cap on liability</td><td>1</td>")
        self.client.login(username="req", password="pw")
        self.assertEqual(self.client.get(reverse("reports")).status_code, 403)

    def test_a_reviewer_can_add_a_finding_identification_missed(self):
        missed = Provision.objects.create(name="Assignment restriction")
        response = self.client.post(reverse("add_missed_finding", args=[self.agreement.pk]), {
            "provision": missed.pk, "clause": self.cap.clause.pk, "source_text": "governed by Georgia law",
        })
        self.assertRedirects(response, reverse("review", args=[self.agreement.pk]))
        flag = Flag.objects.get(provision=missed)
        self.assertEqual(flag.status, Flag.Status.OPEN)  # it still needs a decision
        self.assertEqual((flag.source, flag.created_by), (Flag.Source.MANUAL, self.reviewer))


class HighlightTests(SimpleTestCase):
    def test_the_supporting_words_are_marked_even_across_a_line_break(self):
        self.assertEqual(
            highlight("governed by the laws of\nthe State", "laws of the State"),
            "governed by the <mark>laws of\nthe State</mark>",
        )

    def test_the_rest_of_the_text_is_escaped(self):
        self.assertEqual(highlight("a < b and c", "b and"), "a &lt; <mark>b and</mark> c")
