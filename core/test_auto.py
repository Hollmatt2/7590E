"""Checks for the text rules, the AI step, automatic identification, and scoring. Run:  python manage.py test

The AI step is never really called here: `ask_claude` is replaced with a stand-in that returns a fixed
answer, so the tests are free, fast, and do not need a key.
"""
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .ai_identify import AIUnavailable, find_with_ai
from .auto_identify import identify_automatically
from .evaluation import CategoryScore, score_contract
from .models import Agreement, Clause, Flag, Provision, Severity, User
from .rules import RULES, find_with_rules

USAGE = SimpleNamespace(input_tokens=1000, output_tokens=200, cache_creation_input_tokens=0, cache_read_input_tokens=0)


def answer(*findings):
    """A stand-in for Claude's answer: each finding is (category, clause number, quote, confidence, reason)."""
    keys = ["category", "clause", "quote", "confidence", "reason"]
    return json.dumps({"findings": [dict(zip(keys, finding)) for finding in findings]}), USAGE


class RuleTests(SimpleTestCase):
    def categories_found(self, text):
        return {category for category, _ in find_with_rules(text, RULES)}

    def test_each_rule_finds_a_typical_sentence(self):
        examples = {
            "Governing Law": "This Agreement shall be governed by the laws of the State of New York.",
            "Renewal Term": "This Agreement shall automatically renew for successive one-year terms.",
            "Notice Period To Terminate Renewal": (
                "Either party may give notice of non-renewal at least ninety (90) days prior to the expiration "
                "of the then-current term."
            ),
            "Anti-Assignment": "Neither party may assign this Agreement without the prior written consent of the other.",
            "Insurance": "Supplier shall maintain commercial general liability insurance of at least $1,000,000.",
            "Audit Rights": "Company may audit Distributor's books and records once per year.",
            "Termination For Convenience": "Either party may terminate this Agreement for any reason on thirty days' notice.",
            "Change Of Control": "A change of control of Supplier shall be deemed an assignment.",
        }
        for category, sentence in examples.items():
            with self.subTest(category):
                self.assertIn(category, self.categories_found(sentence))

    def test_rules_ignore_an_unrelated_sentence(self):
        self.assertEqual(self.categories_found("The parties will meet each quarter to discuss marketing plans."), set())

    def test_the_supporting_text_is_the_whole_sentence(self):
        text = "1. Term. This lasts a year. This Agreement is governed by the laws of Georgia. Notices go by mail."
        self.assertEqual(
            find_with_rules(text, ["Governing Law"]),
            [("Governing Law", "This Agreement is governed by the laws of Georgia.")],
        )


@patch("core.ai_identify.credentials_configured", return_value=True)
@patch("core.ai_identify.ask_claude")
class AIStepTests(SimpleTestCase):
    clauses = [
        "1. Governing Law. This Agreement is governed by the laws of\nthe State of Georgia.",
        "2. Liability. Liability is capped at the fees paid in the prior twelve months.",
    ]
    definitions = {"Governing law": "Which law governs.", "Cap on liability": "A limit on liability."}

    def test_only_quotes_really_in_the_agreement_are_kept(self, ask, _):
        ask.return_value = answer(
            ("Governing law", 1, "governed by the laws of the State of Georgia", 0.95, "Names the governing law."),
            ("Cap on liability", 1, "capped at the fees paid", 0.8, "Caps liability."),  # wrong clause number
            ("Cap on liability", 2, "liability is unlimited", 0.6, "Invented."),  # not in the agreement
            ("Exclusivity", 1, "governed by", 0.9, "Not in the playbook."),  # unknown provision
        )
        findings, _ = find_with_ai(self.clauses, self.definitions)
        self.assertEqual([(f.name, f.clause) for f in findings], [("Governing law", 0), ("Cap on liability", 1)])

    def test_confidence_is_kept_between_0_and_1(self, ask, _):
        ask.return_value = answer(("Governing law", 1, "governed by the laws", 1.7, "Plainly stated."))
        findings, _ = find_with_ai(self.clauses, self.definitions)
        self.assertEqual(findings[0].confidence, 1.0)

    def test_an_answer_in_the_wrong_format_means_the_ai_is_unavailable(self, ask, _):
        ask.return_value = ("this is not JSON", USAGE)
        with self.assertRaises(AIUnavailable):
            find_with_ai(self.clauses, self.definitions)

    def test_without_a_key_the_ai_is_unavailable(self, ask, credentials):
        credentials.return_value = False
        with self.assertRaises(AIUnavailable):
            find_with_ai(self.clauses, self.definitions)
        ask.assert_not_called()


class AutomaticIdentificationTests(TestCase):
    def setUp(self):
        self.requester = User.objects.create_user("req", password="pw")
        self.law = Provision.objects.create(
            name="Governing law", cuad_category="Governing Law", default_severity=Severity.LOW,
            method=Provision.Method.RULES,
        )
        self.cap = Provision.objects.create(
            name="Cap on liability", cuad_category="Cap On Liability", definition="A limit on liability.",
            method=Provision.Method.AI,
        )
        self.agreement = Agreement.objects.create(
            vendor="Acme", agreement_type=Agreement.AgreementType.SERVICES, business_unit="Corporate",
            needed_by=timezone.localdate(), document="agreements/acme.pdf", submitted_by=self.requester,
            status=Agreement.Status.AWAITING_IDENTIFICATION,
        )
        self.law_clause = Clause.objects.create(
            agreement=self.agreement, position=1, text="This Agreement is governed by the laws of Georgia."
        )
        self.cap_clause = Clause.objects.create(
            agreement=self.agreement, position=2, text="Liability is capped at the fees paid."
        )

    @patch("core.ai_identify.credentials_configured", return_value=False)
    def test_a_provision_is_skipped_for_an_agreement_type_it_does_not_apply_to(self, _):
        """The playbook is scoped per agreement type (ambiguity log, question 3)."""
        self.law.agreement_types = "software,dpa"  # the agreement under test is professional services
        self.law.save(update_fields=["agreement_types"])
        identify_automatically(self.agreement)
        self.assertFalse(Flag.objects.filter(provision=self.law).exists())
        # It still applies to the types it lists.
        self.assertTrue(self.law.applies_to(Agreement.AgreementType.SOFTWARE))
        self.assertFalse(self.law.applies_to(Agreement.AgreementType.SERVICES))

    @patch("core.ai_identify.credentials_configured", return_value=False)
    def test_playbook_keywords_are_found_whatever_the_method(self, _):
        """An administrator's keywords run even for a provision the AI usually handles."""
        self.cap.keywords = "shall not be limited\nunlimited liability"
        self.cap.save(update_fields=["keywords"])
        Clause.objects.create(
            agreement=self.agreement, position=3,
            text="The Supplier's liability for breach of confidentiality shall not be limited in any way.",
        )
        identify_automatically(self.agreement)
        flag = Flag.objects.get(source=Flag.Source.KEYWORD)
        self.assertEqual(flag.provision, self.cap)
        self.assertIn("shall not be limited", flag.source_text)
        self.assertIn('keyword "shall not be limited"', flag.reason)

    @patch("core.ai_identify.credentials_configured", return_value=True)
    @patch("core.ai_identify.ask_claude")
    def test_a_keyword_does_not_repeat_a_finding_another_method_made(self, ask, _):
        self.cap.keywords = "capped at the fees"
        self.cap.save(update_fields=["keywords"])
        ask.return_value = answer(("Cap on liability", 2, "Liability is capped at the fees paid.", 0.9, "A cap."))
        identify_automatically(self.agreement)
        cap_flags = Flag.objects.filter(provision=self.cap)
        self.assertEqual([flag.source for flag in cap_flags], [Flag.Source.AI])

    @patch("core.ai_identify.credentials_configured", return_value=False)
    def test_when_the_ai_is_unavailable_rule_findings_wait_for_a_person(self, _):
        note = identify_automatically(self.agreement)
        flag = Flag.objects.get()
        self.assertEqual((flag.provision, flag.clause, flag.source), (self.law, self.law_clause, Flag.Source.RULE))
        self.assertIsNone(flag.confidence)  # a rule is not a model, so it has no confidence score
        self.assertTrue(note.startswith("AI unavailable"))
        # The AI could not look for "Cap on liability", so a person has to finish identification.
        self.assertEqual(self.agreement.status, Agreement.Status.AWAITING_IDENTIFICATION)

    @patch("core.ai_identify.credentials_configured", return_value=True)
    @patch("core.ai_identify.ask_claude")
    def test_ai_findings_are_saved_with_their_confidence(self, ask, _):
        ask.return_value = answer(("Cap on liability", 2, "capped at the fees paid", 0.8, "Caps liability."))
        identify_automatically(self.agreement)
        ai_flag = Flag.objects.get(source=Flag.Source.AI)
        self.assertEqual((ai_flag.provision, ai_flag.clause, ai_flag.confidence), (self.cap, self.cap_clause, 0.8))
        # Every provision's method ran, so the agreement goes straight to review.
        self.assertEqual(self.agreement.status, Agreement.Status.IN_REVIEW)

    @patch("core.ai_identify.credentials_configured", return_value=False)
    def test_it_runs_only_once_per_agreement(self, _):
        identify_automatically(self.agreement)
        identify_automatically(self.agreement)
        self.assertEqual(Flag.objects.count(), 1)

    @override_settings(AUTO_IDENTIFY=[])
    def test_switched_off_it_does_nothing(self):
        identify_automatically(self.agreement)
        self.assertFalse(Flag.objects.exists())

    def test_low_confidence_ai_findings_are_marked_on_the_review_page(self):
        User.objects.create_user("rev", password="pw", role=User.Role.REVIEWER)
        Agreement.objects.filter(pk=self.agreement.pk).update(status=Agreement.Status.IN_REVIEW)
        Flag.objects.create(
            agreement=self.agreement, provision=self.cap, clause=self.cap_clause, severity=Severity.MEDIUM,
            source_text="capped at the fees paid", reason="Maybe a cap.", source=Flag.Source.AI, confidence=0.3,
        )
        self.client.login(username="rev", password="pw")
        self.assertContains(self.client.get(reverse("review", args=[self.agreement.pk])), "Low confidence")


class ScoringTests(SimpleTestCase):
    def test_scoring_counts_found_labels_and_wrong_flags(self):
        text = "A. The law of Georgia governs this deal. B. Unrelated text sits here. C. This is also governed by Georgia law."
        first, last = "The law of Georgia governs this deal.", "This is also governed by Georgia law."
        labels = {"Governing Law": [
            (text.index(first), text.index(first) + len(first), first),
            (text.index(last), text.index(last) + len(last), last),
        ]}
        predictions = [("Governing Law", first), ("Governing Law", "Unrelated text sits here.")]
        scores = {"Governing Law": CategoryScore()}
        score_contract("Test contract", text, labels, predictions, scores)
        score = scores["Governing Law"]
        self.assertEqual((score.labeled, score.found, score.raised, score.wrong), (2, 1, 2, 1))
        self.assertEqual((score.recall, score.false_flag_rate), (0.5, 0.5))
        self.assertEqual(score.misses, [("Test contract", last)])
