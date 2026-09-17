"""Automatic identification: workflow stage 3 without a person, by text rules and the AI step.

After a document is read, each playbook provision is looked for by its own method (its "method" field:
a text rule or the AI model). Findings are saved as flags. If every provision's method ran, the
agreement goes straight to review. If any could not run (no rule for it, the AI switched off or
unavailable), it waits on the manual identification screen, where the automatic findings are already
listed and a person adds the rest. Either way, a person decides on every flag (brief, section 5).
"""
import logging

from django.conf import settings
from django.db import transaction

from .ai_identify import AIUnavailable, find_with_ai
from .models import Agreement, Flag, Provision
from .rules import COMPILED, compile_keywords, find_with_keywords, find_with_rules

logger = logging.getLogger(__name__)


def make_flag(agreement, provision, clause, words, source, reason, confidence=None):
    return Flag(
        agreement=agreement,
        provision=provision,
        clause=clause,
        kind=Flag.Kind.PRESENT,
        severity=provision.default_severity,
        source_text=words,
        reason=reason,
        source=source,
        confidence=confidence,
    )


def identify_automatically(agreement):
    """Add automatic findings to an agreement that is waiting for identification. Runs once per agreement.

    Returns a short note for the worker's log: "done", "skipped", or why the AI could not run.
    """
    if agreement.status != Agreement.Status.AWAITING_IDENTIFICATION:
        return "skipped"
    if agreement.flags.exclude(source=Flag.Source.MANUAL).exists():
        return "skipped"  # already done

    # The playbook is scoped per agreement type (ambiguity log, question 3).
    provisions = [p for p in Provision.objects.all() if p.applies_to(agreement.agreement_type)]
    clauses = list(agreement.clauses.all())
    flags, covered, note = [], set(), "done"

    if "rules" in settings.AUTO_IDENTIFY:
        by_category = {
            p.cuad_category: p for p in provisions if p.method == Provision.Method.RULES and p.cuad_category in COMPILED
        }
        for clause in clauses:
            for category, sentence in find_with_rules(clause.text, by_category):
                provision = by_category[category]
                reason = f"Matched the text rule for {provision.name}."
                flags.append(make_flag(agreement, provision, clause, sentence, Flag.Source.RULE, reason))
        covered.update(provision.pk for provision in by_category.values())

    ai_provisions = [p for p in provisions if p.method == Provision.Method.AI]
    if "ai" in settings.AUTO_IDENTIFY and ai_provisions:
        by_name = {p.name: p for p in ai_provisions}
        try:
            findings, _ = find_with_ai([clause.text for clause in clauses], {p.name: p.definition or p.name for p in ai_provisions})
        except AIUnavailable as error:
            logger.warning("AI step unavailable for agreement %s: %s", agreement.pk, error)
            note = f"AI unavailable: {error}"
        else:
            for finding in findings:
                flags.append(make_flag(
                    agreement, by_name[finding.name], clauses[finding.clause], finding.quote, Flag.Source.AI,
                    finding.reason or "Identified by the AI model.", confidence=finding.confidence,
                ))
            covered.update(provision.pk for provision in ai_provisions)

    # Playbook keywords run for every provision that has them, whatever its method, and never
    # repeat a finding another method already made.
    keywords = {p: compile_keywords(p.keywords.splitlines()) for p in provisions if p.keywords.strip()}
    if keywords:
        already = {(flag.provision_id, flag.clause_id, flag.source_text) for flag in flags}
        for clause in clauses:
            for provision, sentence, phrase in find_with_keywords(clause.text, keywords):
                if (provision.pk, clause.pk, sentence) in already:
                    continue
                already.add((provision.pk, clause.pk, sentence))
                reason = f'Matched the playbook keyword "{phrase}" for {provision.name}.'
                flags.append(make_flag(agreement, provision, clause, sentence, Flag.Source.KEYWORD, reason))
        # A provision looked for by text alone counts as checked once its keywords have run.
        covered.update(p.pk for p in keywords if p.method == Provision.Method.RULES)

    every_method_ran = all(provision.pk in covered for provision in provisions)
    with transaction.atomic():
        Flag.objects.bulk_create(flags)
        if every_method_ran:
            agreement.status = Agreement.Status.IN_REVIEW
            agreement.save(update_fields=["status"])
    return note
