"""The settings an administrator can change while the site is running.

The values live in one database row (core.models.Configuration) so the administrator screen can edit them,
which the brief asks for in section 3. The environment variables are only the starting values.
"""
from django.conf import settings


def current():
    """The configuration row, created from the environment variables the first time it is needed."""
    from .models import Configuration

    config = Configuration.objects.first()
    if config is None:
        config = Configuration.objects.create(ai_low_confidence=settings.AI_LOW_CONFIDENCE)
    return config


def low_confidence_threshold():
    """AI findings below this are marked "check carefully" and listed last. See docs/threshold-note.md."""
    return current().ai_low_confidence


def retention_days():
    """How many days after its outcome an agreement's file is kept. 0 keeps it until an administrator decides."""
    return current().document_retention_days
