"""The AI step: Claude reads an agreement's clauses and reports which playbook provisions are present.

For each provision it finds, it gives the clause number, the exact supporting words, a confidence from
0 to 1, and a one-sentence reason. It does not extract values or judge whether a term is acceptable
(Change Notice 1). Every finding goes to a person for review, like any other finding.

The key comes from the ANTHROPIC_API_KEY environment variable and never enters the repository.
"""
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import anthropic
from django.conf import settings

from .forms import squash

logger = logging.getLogger(__name__)

# If Claude declines a request, the API re-runs it on another Claude model instead of failing.
FALLBACK_BETA = "server-side-fallback-2026-07-01"

INSTRUCTIONS = """You review vendor agreements for Calder Industrial Supply, an industrial distributor. A person \
checks every finding you report, so report each passage where one of the provisions listed below is present, \
and nothing else.

For every finding, give:
- category: the provision's name, exactly as listed below
- clause: the number of the clause that contains the passage
- quote: the passage copied word for word from that clause, long enough to show the provision (usually one \
sentence). Do not paraphrase, shorten with ellipses, or join text from different clauses.
- confidence: a number from 0 to 1 for how sure you are that the passage is this provision as defined: about \
0.9 or higher when the text states it plainly, about 0.5 when it depends on interpretation, lower when it \
only might apply
- reason: one plain sentence saying why the passage fits the definition

A provision can appear in several clauses; report each one. Report nothing for a provision the agreement does \
not contain. A heading, a table-of-contents entry, or a cross-reference to another section is not the \
provision itself. Identify provisions only: do not judge whether a term is acceptable, and do not give legal \
advice."""


class AIUnavailable(Exception):
    """The AI step could not run: no key, no network, rate limits, or a declined request.
    The agreement then waits for a person, exactly as if the AI were switched off."""


@dataclass
class AIFinding:
    name: str  # the provision's name
    clause: int  # position of the clause in the list, counting from 0
    quote: str  # the supporting words, with spacing normalized
    confidence: float
    reason: str


def credentials_configured():
    """True if the Anthropic library has a key or a saved login to use."""
    return bool(
        os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        or (Path.home() / ".config" / "anthropic").exists()
    )


def output_schema(names):
    """The JSON shape the answer must take. The API guarantees the answer matches it."""
    finding = {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": names},
            "clause": {"type": "integer"},
            "quote": {"type": "string"},
            "confidence": {"type": "number"},
            "reason": {"type": "string"},
        },
        "required": ["category", "clause", "quote", "confidence", "reason"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"findings": {"type": "array", "items": finding}},
        "required": ["findings"],
        "additionalProperties": False,
    }


def build_prompt(clauses, definitions):
    """The instructions (the same for every agreement, so they can be cached) and the agreement itself."""
    system = INSTRUCTIONS + "\n\nProvisions:\n" + "\n".join(
        f"- {name}: {definition}" for name, definition in definitions.items()
    )
    user = "Agreement text, split into numbered clauses:\n\n" + "\n\n".join(
        f'<clause number="{number}">\n{text}\n</clause>' for number, text in enumerate(clauses, start=1)
    )
    return system, user


def ask_claude(system, user, schema):
    """Send one request and return (answer text, usage). API errors become AIUnavailable."""
    try:
        client = anthropic.Anthropic()
        with client.beta.messages.stream(
            model=settings.AI_MODEL,
            max_tokens=32000,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        ) as stream:
            message = stream.get_final_message()
    except anthropic.AuthenticationError as error:
        raise AIUnavailable("The Anthropic API key is missing or not valid.") from error
    except anthropic.RateLimitError as error:
        raise AIUnavailable("The Anthropic API is limiting requests right now.") from error
    except anthropic.APIConnectionError as error:
        raise AIUnavailable("Could not reach the Anthropic API.") from error
    except anthropic.APIStatusError as error:
        raise AIUnavailable(f"The Anthropic API returned an error ({error.status_code}).") from error
    except anthropic.AnthropicError as error:
        raise AIUnavailable(f"The AI step could not start ({error.__class__.__name__}).") from error

    if message.stop_reason == "refusal":
        raise AIUnavailable("Claude declined to process this agreement.")
    if message.stop_reason == "max_tokens":
        raise AIUnavailable("The answer was cut off before it finished.")
    text = next((block.text for block in message.content if block.type == "text"), None)
    if text is None:
        raise AIUnavailable("The response contained no answer.")
    return text, message.usage


def find_with_ai(clauses, definitions):
    """Ask Claude which provisions in `definitions` ({name: definition}) appear in `clauses` (texts, in order).

    Returns (findings, usage). A finding whose quote is not word for word in the agreement is dropped,
    because every finding must point to real source text (brief, section 5). A quote given the wrong
    clause number is moved to the clause that contains it.
    """
    if not credentials_configured():
        raise AIUnavailable("No Anthropic API key is set (ANTHROPIC_API_KEY).")
    system, user = build_prompt(clauses, definitions)
    text, usage = ask_claude(system, user, output_schema(list(definitions)))
    try:
        answer = json.loads(text)["findings"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise AIUnavailable("The answer was not in the expected format.") from error

    squashed = [squash(clause) for clause in clauses]
    findings, seen, dropped = [], set(), 0
    for item in answer:
        name, quote = item.get("category"), squash(str(item.get("quote", "")))
        if name not in definitions or not quote:
            dropped += 1
            continue
        position = int(item.get("clause", 0)) - 1
        if not (0 <= position < len(clauses) and quote in squashed[position]):
            position = next((index for index, text in enumerate(squashed) if quote in text), None)
            if position is None:
                dropped += 1
                continue
        if (name, position, quote) in seen:
            continue
        seen.add((name, position, quote))
        confidence = min(max(float(item.get("confidence", 0)), 0.0), 1.0)
        findings.append(AIFinding(name, position, quote, confidence, str(item.get("reason", "")).strip()))
    if dropped:
        logger.warning("AI step dropped %d finding(s) whose provision or quote was not in the agreement", dropped)
    return findings, usage
