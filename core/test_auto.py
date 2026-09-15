"""Checks for the text rules, automatic identification, and evaluation scoring. Run:  python manage.py test"""
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from .auto_identify import identify_automatically
from .evaluation import CategoryScore, score_contract
from .models import Agreement, Clause, Flag, Provision, Severity, User
from .rules import RULES, find_with_rules


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


class AutomaticIdentificationTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("req", password="pw")
        self.law = Provision.objects.create(name="Governing law", cuad_category="Governing Law", default_severity=Severity.LOW)
        self.cap = Provision.objects.create(name="Cap on liability", cuad_category="Cap On Liability")  # no rule
        self.agreement = Agreement.objects.create(
            vendor="Acme", agreement_type=Agreement.AgreementType.SERVICES, business_unit="Corporate",
            needed_by=timezone.localdate(), document="agreements/acme.pdf", submitted_by=user,
            status=Agreement.Status.AWAITING_IDENTIFICATION,
        )
        self.clause = Clause.objects.create(
            agreement=self.agreement, position=1, text="This Agreement is governed by the laws of Georgia."
        )
        Clause.objects.create(agreement=self.agreement, position=2, text="Liability is capped at the fees paid.")

    def test_rule_findings_are_saved_for_a_person_to_check(self):
        identify_automatically(self.agreement)
        flag = Flag.objects.get()
        self.assertEqual((flag.provision, flag.clause, flag.source), (self.law, self.clause, Flag.Source.RULE))
        self.assertEqual(flag.source_text, "This Agreement is governed by the laws of Georgia.")
        self.assertIsNone(flag.confidence)  # a rule is not a model, so it has no confidence score
        # "Cap on liability" has no automatic method, so a person still has to finish identification.
        self.assertEqual(self.agreement.status, Agreement.Status.AWAITING_IDENTIFICATION)

    def test_it_runs_only_once_per_agreement(self):
        identify_automatically(self.agreement)
        identify_automatically(self.agreement)
        self.assertEqual(Flag.objects.count(), 1)

    def test_when_every_provision_has_a_method_the_agreement_goes_to_review(self):
        self.cap.delete()
        identify_automatically(self.agreement)
        self.assertEqual(self.agreement.status, Agreement.Status.IN_REVIEW)

    @override_settings(AUTO_IDENTIFY=[])
    def test_switched_off_it_does_nothing(self):
        identify_automatically(self.agreement)
        self.assertFalse(Flag.objects.exists())


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
