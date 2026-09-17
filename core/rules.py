"""Text rules: patterns for provisions that a pattern can find reliably (brief, section 9).

Each rule is a regular expression for one CUAD category. When it matches inside a clause, the
finding's supporting text is the whole sentence around the match, so a reviewer sees it in context.
Categories that need judgment (for example, whether a liability cap exists at all) have no rule
and are left to the AI model or a person. The evaluate_identification command measures every rule.

These patterns were written before the check set was chosen. Re-scoring a changed rule on the same
check set overstates how well it works; test changes on different contracts.
"""
import re

RULES = {
    "Governing Law": r"\b(?:governed\s+by|construed\s+(?:in\s+accordance\s+with|under)|governing\s+law)\b",
    "Renewal Term": (
        r"\b(?:automatic(?:ally)?\s+(?:renew|extend)|renew(?:s|ed)?\s+automatically"
        r"|shall\s+(?:be\s+)?(?:automatically\s+)?(?:renewed|extended)"
        r"|successive\s+(?:\w+\s+)?(?:\(\d+\)\s+)?(?:year|month)|renewal\s+term)"
    ),
    "Notice Period To Terminate Renewal": (
        r"(?:\(\d+\)|\b\d+)\s*(?:calendar\s+|business\s+)?(?:days?|months?)\b[^.]{0,150}"
        r"\b(?:prior\s+to|before)\b[^.]{0,100}\b(?:expiration|expiry|end\s+of|renewal)"
    ),
    "Anti-Assignment": (
        r"\b(?:not|neither\s+party\s+may|no\s+party\s+may)\b[^.]{0,60}\bassign"
        r"|\bassign(?:ment|ed)?\b[^.]{0,150}\bwithout\s+(?:the\s+)?(?:prior\s+)?(?:written\s+)?consent\b"
    ),
    "Insurance": r"\b(?:maintain|carry|procure|obtain)\b[^.]{0,120}\binsurance\b|\binsurance\s+(?:policy|policies|coverage)\b",
    "Audit Rights": (
        r"\b(?:audit|inspect)\w*\b[^.]{0,150}\b(?:books|records|accounts)\b"
        r"|\b(?:books|records)\b[^.]{0,150}\b(?:audit|inspect)\w*"
    ),
    "Termination For Convenience": (
        r"\bterminat\w*\b[^.]{0,150}\b(?:for\s+(?:any|no)\s+reason|for\s+convenience|without\s+cause"
        r"|at\s+any\s+time\s+(?:upon|by|on|with))"
    ),
    "Change Of Control": (
        r"\bchange\s+(?:of|in)\s+control\b"
        r"|\b(?:merger|consolidation|acquisition)\b[^.]{0,120}\b(?:assign|terminat|consent)"
    ),
}
COMPILED = {category: re.compile(pattern, re.IGNORECASE) for category, pattern in RULES.items()}

# A full stop or semicolon followed by a space or the end of the text. "2.1" and "U.S." do not count.
SENTENCE_END = re.compile(r"[.;](?=\s|$)")


def sentence_around(text, start, end):
    """The sentence containing text[start:end]: from after the previous full stop to the next one."""
    earlier = [match.end() for match in SENTENCE_END.finditer(text, 0, start)]
    begin = earlier[-1] if earlier else 0
    later = SENTENCE_END.search(text, end)
    finish = later.end() if later else len(text)
    return text[begin:finish].strip()


def compile_keywords(phrases):
    """Compile playbook keywords into patterns: spacing is flexible, capitals do not matter, and a
    phrase also matches the start of a longer word, so "indemnif" finds "indemnification"."""
    patterns = []
    for phrase in phrases:
        words = phrase.split()
        if not words:
            continue
        pattern = r"\s+".join(re.escape(word) for word in words)
        if words[0][0].isalnum():
            pattern = r"\b" + pattern
        patterns.append((phrase, re.compile(pattern, re.IGNORECASE)))
    return patterns


def find_with_keywords(text, by_key):
    """Return (key, sentence, phrase) for each keyword match in `text`, once per sentence and key.

    `by_key` maps anything (a provision, a category name) to the patterns from compile_keywords.
    """
    found = []
    for key, patterns in by_key.items():
        seen = set()
        for phrase, pattern in patterns:
            for match in pattern.finditer(text):
                sentence = sentence_around(text, *match.span())
                if sentence and sentence not in seen:
                    seen.add(sentence)
                    found.append((key, sentence, phrase))
    return found


def find_with_rules(text, categories):
    """Return (category, sentence) for each rule in `categories` that matches `text`, once per sentence."""
    found = []
    for category in categories:
        pattern = COMPILED.get(category)
        if pattern is None:
            continue
        seen = set()
        for match in pattern.finditer(text):
            sentence = sentence_around(text, *match.span())
            if sentence and sentence not in seen:
                seen.add(sentence)
                found.append((category, sentence))
    return found
