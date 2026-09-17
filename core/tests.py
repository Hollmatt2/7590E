"""Automated checks. Run them with:  python manage.py test"""
import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Agreement, Clause, Flag, Provision, Severity, User
from .reading import read_agreement, split_into_clauses

# Tests save uploads in a throwaway folder, never in the real media/ folder.
TEST_MEDIA = tempfile.mkdtemp()

PDF_BYTES = b"%PDF-1.4\n% a tiny stand-in for a real contract\n"

# A short contract used by the reading tests. It should split into 5 clauses: the title joins
# clause 1 because it is short, and the "It renews" line belongs to clause 2.
SAMPLE_LINES = [
    "MASTER SERVICES AGREEMENT",
    "1. Definitions. In this Agreement the following terms have the meanings below.",
    "2. Term. This Agreement begins on the Effective Date and continues for one year.",
    "It renews automatically for one-year terms unless either party gives notice.",
    "3. Limitation of Liability. Neither party is liable for indirect damages.",
    "3.1 The total liability of each party is capped at the fees paid in twelve months.",
    "4. Governing Law. This Agreement is governed by the laws of the State of Georgia.",
]


def make_pdf(lines):
    """Build a small, real, one-page PDF containing these lines, so the tests need no sample files."""
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in lines]
    stream = ("BT /F1 11 Tf 14 TL 72 760 Td " + " ".join(f"({line}) '" for line in escaped) + " ET").encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_at = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    pdf += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref_at)
    return bytes(pdf)


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class IntakeTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA, ignore_errors=True)

    def setUp(self):
        self.requester = User.objects.create_user("req", password="pw", role=User.Role.REQUESTER)
        self.other = User.objects.create_user("other", password="pw", role=User.Role.REQUESTER)
        self.reviewer = User.objects.create_user("rev", password="pw", role=User.Role.REVIEWER)

    def form_data(self, **changes):
        """A valid intake form. Pass a field name to replace one value, e.g. form_data(vendor="")."""
        data = {
            "vendor": "Acme Software",
            "agreement_type": Agreement.AgreementType.SOFTWARE,
            "business_unit": "Atlanta DC",
            "needed_by": (timezone.localdate() + timedelta(days=14)).isoformat(),
            "document": SimpleUploadedFile("acme.pdf", PDF_BYTES, content_type="application/pdf"),
        }
        data.update(changes)
        return data

    def submit_as(self, username, **changes):
        self.client.login(username=username, password="pw")
        return self.client.post(reverse("submit_agreement"), self.form_data(**changes))

    def test_landing_page_is_public(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_pages_past_the_landing_page_need_a_login(self):
        response = self.client.get(reverse("submit_agreement"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("submit_agreement"))

    def test_submitting_saves_the_agreement_without_reading_it(self):
        response = self.submit_as("req")
        agreement = Agreement.objects.get()
        self.assertRedirects(response, reverse("agreement_detail", args=[agreement.pk]))
        self.assertEqual(agreement.status, Agreement.Status.SUBMITTED)
        self.assertEqual(agreement.submitted_by, self.requester)
        self.assertFalse(agreement.clauses.exists())  # reading happens later, in process_agreements

    def test_a_renamed_file_that_is_not_a_pdf_is_rejected(self):
        fake = SimpleUploadedFile("contract.pdf", b"PK\x03\x04 really a Word file", content_type="application/pdf")
        response = self.submit_as("req", document=fake)
        self.assertContains(response, "not a readable PDF")
        self.assertFalse(Agreement.objects.exists())

    def test_a_past_needed_by_date_is_rejected(self):
        yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
        response = self.submit_as("req", needed_by=yesterday)
        self.assertContains(response, "already past")
        self.assertFalse(Agreement.objects.exists())

    def test_requesters_cannot_open_someone_elses_agreement(self):
        self.submit_as("req")
        agreement = Agreement.objects.get()
        self.client.login(username="other", password="pw")
        self.assertEqual(self.client.get(reverse("agreement_detail", args=[agreement.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("agreement_document", args=[agreement.pk])).status_code, 403)

    def test_searching_an_agreement_shows_only_the_clauses_with_those_words(self):
        """A reviewer can search the contract's own text; the search is exact about words, not meaning."""
        self.submit_as("req")
        agreement = Agreement.objects.get()
        Clause.objects.create(agreement=agreement, position=1, text="Supplier shall indemnify the Buyer.")
        Clause.objects.create(agreement=agreement, position=2, text="Governed by the laws of Georgia.")
        self.client.login(username="rev", password="pw")
        url = reverse("agreement_detail", args=[agreement.pk])

        response = self.client.get(url, {"q": "INDEMNIFY"})  # capitals do not matter
        self.assertContains(response, "1 of 2 clauses contain")
        self.assertContains(response, "<mark>indemnify</mark>", html=False)
        self.assertNotContains(response, "laws of Georgia")

        empty = self.client.get(url, {"q": "arbitration"})
        self.assertContains(empty, "0 of 2 clauses contain")

    def test_reviewers_can_open_any_agreement(self):
        self.submit_as("req")
        agreement = Agreement.objects.get()
        self.client.login(username="rev", password="pw")
        self.assertEqual(self.client.get(reverse("agreement_detail", args=[agreement.pk])).status_code, 200)


class SplittingTests(SimpleTestCase):
    def test_numbered_sections_become_separate_clauses(self):
        clauses = split_into_clauses("\n".join(SAMPLE_LINES))
        self.assertEqual(len(clauses), 5)
        self.assertTrue(clauses[0].startswith("MASTER SERVICES AGREEMENT\n1. Definitions"))
        self.assertIn("renews automatically", clauses[1])
        self.assertTrue(clauses[3].startswith("3.1 The total liability"))

    def test_a_wrapped_line_starting_with_section_does_not_split(self):
        clauses = split_into_clauses("\n".join([
            "1. Term. This Agreement lasts one year from the Effective Date.",
            "2. Assignment. Neither party may assign this Agreement except as permitted under",
            "Section 9 of this Agreement or with the written consent of the other party.",
            "3. Notices. Notices must be in writing and sent to the addresses above.",
        ]))
        self.assertEqual(len(clauses), 3)
        self.assertIn("Section 9 of this Agreement", clauses[1])

    def test_page_numbers_are_removed(self):
        clauses = split_into_clauses("\n".join([
            "1. Term. One year from the Effective Date, renewing yearly after that.",
            "- 1 -",
            "2. Fees. Customer pays the fees in the order form within thirty days.",
            "Page 2 of 3",
            "3. Notices. Notices must be in writing and sent to the addresses above.",
        ]))
        self.assertEqual(len(clauses), 3)
        self.assertNotIn("Page 2", " ".join(clauses))

    def test_text_without_numbered_sections_falls_back_to_paragraphs(self):
        text = "\n\n".join(f"Paragraph {n} says the supplier will deliver the goods on time." for n in range(4))
        self.assertEqual(len(split_into_clauses(text)), 4)

    def test_a_very_long_clause_is_cut_into_pieces(self):
        long_section = " ".join(f"Sentence {n} of a very long section." for n in range(200))
        clauses = split_into_clauses("\n".join([
            "1. Long. " + long_section,
            "2. Payment. Customer pays each invoice within thirty days of receipt.",
            "3. Notices. Notices must be in writing and sent to the addresses above.",
        ]))
        self.assertGreater(len(clauses), 3)
        self.assertTrue(all(len(clause) <= 3000 for clause in clauses))

    def test_capitalized_titles_ending_in_a_full_stop_start_clauses(self):
        clauses = split_into_clauses("\n".join([
            "DUTIES.",
            "The Consultant will provide the services described in Exhibit A to the Company.",
            "CONSULTING SERVICES & COMPENSATION. The Company pays the Consultant monthly.",
            "TERM. This Agreement lasts twelve months from the Effective Date unless ended.",
        ]))
        self.assertEqual(len(clauses), 3)
        self.assertTrue(clauses[1].startswith("CONSULTING SERVICES & COMPENSATION."))

    def test_numbers_with_no_space_after_them_start_clauses(self):
        clauses = split_into_clauses("\n".join([
            "1.DGT shall pay Dolphin for carrying out the beta testing of their bandwidth;",
            "2.Upon completion of the beta testing stage, DGT will guarantee Dolphin work;",
            "3.Dolphin agrees to complete its services within 14 days of receiving photos;",
        ]))
        self.assertEqual(len(clauses), 3)

    def test_roman_and_lettered_sections_start_clauses(self):
        clauses = split_into_clauses("\n".join([
            "I. SERVICES. The Supplier provides the services listed in the order form.",
            "II. FEES. The Customer pays the fees listed in the order form each month.",
            "B. Late payments carry interest at one percent per month until they are paid.",
        ]))
        self.assertEqual(len(clauses), 3)

    def test_a_table_of_contents_stays_together(self):
        clauses = split_into_clauses("\n".join([
            "TABLE OF CONTENTS",
            "1. GRANT OF FRANCHISE 1",
            "1.1 Rights Granted to You 1",
            "1.2 Non-Exclusive Grant 2",
            "2. OPERATION OF THE FRANCHISED BUSINESS 2",
            "3. INITIAL AND EXTENDED TERMS 3",
            "1. GRANT OF FRANCHISE. We grant you the right to operate the franchised business.",
            "2. OPERATION. You must operate the business full time and follow the manuals.",
            "3. TERM. The initial term is ten years from the date of this Agreement.",
        ]))
        self.assertEqual(len(clauses), 4)
        self.assertTrue(clauses[0].startswith("TABLE OF CONTENTS"))
        self.assertIn("Rights Granted to You", clauses[0])
        self.assertTrue(clauses[1].startswith("1. GRANT OF FRANCHISE. We grant"))


@override_settings(MEDIA_ROOT=TEST_MEDIA)
class ReadingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("req", password="pw")

    def make_agreement(self, filename, content):
        return Agreement.objects.create(
            vendor="Acme",
            agreement_type=Agreement.AgreementType.SERVICES,
            business_unit="Corporate",
            needed_by=timezone.localdate(),
            document=SimpleUploadedFile(filename, content),
            submitted_by=self.user,
        )

    def test_a_pdf_is_read_and_split_into_clauses(self):
        agreement = read_agreement(self.make_agreement("msa.pdf", make_pdf(SAMPLE_LINES)).pk)
        self.assertEqual(agreement.status, Agreement.Status.AWAITING_IDENTIFICATION)
        self.assertEqual(list(agreement.clauses.values_list("position", flat=True)), [1, 2, 3, 4, 5])
        self.assertIn("Governing Law", agreement.extracted_text)

    def test_a_text_file_is_read_and_split_into_clauses(self):
        content = "\n".join(SAMPLE_LINES).encode("utf-8")
        agreement = read_agreement(self.make_agreement("msa.txt", content).pk)
        self.assertEqual(agreement.status, Agreement.Status.AWAITING_IDENTIFICATION)
        self.assertEqual(agreement.clauses.count(), 5)

    def test_a_pdf_with_no_text_fails_with_a_reason(self):
        agreement = read_agreement(self.make_agreement("scan.pdf", make_pdf([])).pk)
        self.assertEqual(agreement.status, Agreement.Status.READ_FAILED)
        self.assertIn("scan", agreement.read_error)
        self.assertFalse(agreement.clauses.exists())

    def test_a_damaged_pdf_fails_with_a_reason(self):
        agreement = read_agreement(self.make_agreement("broken.pdf", b"%PDF-1.4\nnot really a pdf\n").pk)
        self.assertEqual(agreement.status, Agreement.Status.READ_FAILED)
        self.assertIn("damaged", agreement.read_error)

    def test_an_agreement_is_only_read_once(self):
        agreement = self.make_agreement("msa.txt", "\n".join(SAMPLE_LINES).encode("utf-8"))
        self.assertIsNotNone(read_agreement(agreement.pk))
        self.assertIsNone(read_agreement(agreement.pk))  # no longer "Submitted", so nothing to do


class IdentificationTests(TestCase):
    """The manual identification screen: a reviewer marks provisions and the exact supporting words."""

    def setUp(self):
        self.requester = User.objects.create_user("req", password="pw", role=User.Role.REQUESTER)
        self.reviewer = User.objects.create_user("rev", password="pw", role=User.Role.REVIEWER)
        self.provision = Provision.objects.create(
            name="Governing law", cuad_category="Governing Law", default_severity=Severity.LOW
        )
        self.agreement = Agreement.objects.create(
            vendor="Acme",
            agreement_type=Agreement.AgreementType.SERVICES,
            business_unit="Corporate",
            needed_by=timezone.localdate(),
            document="agreements/acme.pdf",
            submitted_by=self.requester,
            status=Agreement.Status.AWAITING_IDENTIFICATION,
        )
        self.clause = Clause.objects.create(
            agreement=self.agreement,
            position=1,
            text="1. Governing Law. This Agreement is governed by the laws of\nthe State of Georgia.",
        )
        self.client.login(username="rev", password="pw")

    def add_finding(self, text):
        return self.client.post(
            reverse("identify", args=[self.agreement.pk]),
            {"provision": self.provision.pk, "clause": self.clause.pk, "source_text": text},
        )

    def test_a_reviewer_can_mark_a_provision_with_its_exact_words(self):
        # The words cross a line break in the clause. Spacing may differ; the words may not.
        response = self.add_finding("governed by the laws of the State of Georgia")
        self.assertRedirects(response, reverse("identify", args=[self.agreement.pk]))
        flag = Flag.objects.get()
        self.assertEqual(flag.source, Flag.Source.MANUAL)
        self.assertEqual(flag.kind, Flag.Kind.PRESENT)
        self.assertEqual(flag.severity, Severity.LOW)  # taken from the playbook entry
        self.assertEqual(flag.created_by, self.reviewer)
        self.assertIsNone(flag.confidence)  # a person's finding has no model score

    def test_words_that_are_not_in_the_clause_are_rejected(self):
        response = self.add_finding("governed by the laws of Delaware")
        self.assertContains(response, "does not appear in the chosen clause")
        self.assertFalse(Flag.objects.exists())

    def test_requesters_cannot_identify(self):
        self.client.login(username="req", password="pw")
        self.assertEqual(self.client.get(reverse("identify", args=[self.agreement.pk])).status_code, 403)

    def test_finishing_sends_the_agreement_to_review(self):
        self.add_finding("governed by the laws of the State of Georgia")
        self.client.post(reverse("finish_identification", args=[self.agreement.pk]))
        self.agreement.refresh_from_db()
        self.assertEqual(self.agreement.status, Agreement.Status.IN_REVIEW)
        # After that, the identification screen sends people back to the agreement page.
        response = self.client.get(reverse("identify", args=[self.agreement.pk]))
        self.assertRedirects(response, reverse("agreement_detail", args=[self.agreement.pk]))

    def test_findings_cannot_be_removed_once_review_starts(self):
        self.add_finding("governed by the laws of the State of Georgia")
        flag = Flag.objects.get()
        Agreement.objects.filter(pk=self.agreement.pk).update(status=Agreement.Status.IN_REVIEW)
        response = self.client.post(reverse("remove_finding", args=[self.agreement.pk, flag.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Flag.objects.filter(pk=flag.pk).exists())

    def test_the_work_queue_is_for_staff_only(self):
        self.assertContains(self.client.get(reverse("work_queue")), "Acme")
        self.client.login(username="req", password="pw")
        self.assertEqual(self.client.get(reverse("work_queue")).status_code, 403)

    def test_the_database_refuses_a_confidence_above_one(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Flag.objects.create(
                agreement=self.agreement, provision=self.provision, severity=Severity.LOW,
                reason="test", source=Flag.Source.AI, confidence=1.5,
            )
