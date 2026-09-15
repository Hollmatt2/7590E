"""Template filters for the review pages. Load them in a template with {% load review_extras %}."""
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight(text, words):
    """Show `text` with the first occurrence of `words` marked, allowing any spacing between the words.

    Everything is HTML-escaped first, so contract text can never inject markup into the page.
    """
    pieces = words.split()
    if not text or not pieces:
        return text
    match = re.search(r"\s+".join(re.escape(piece) for piece in pieces), text)
    if not match:
        return text
    start, end = match.span()
    return mark_safe(f"{escape(text[:start])}<mark>{escape(text[start:end])}</mark>{escape(text[end:])}")
