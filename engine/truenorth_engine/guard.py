"""AI-specific input defense (SC-3): prompt-injection / retrieval-poisoning screening.

Evidence and user-supplied text are *data*, not instructions. This module scans that text
for common prompt-injection patterns (instruction overrides, injected role turns, prompt
exfiltration, guardrail-override attempts) and returns human-readable flags. The pipeline
records the flags on the decision and forces human review when anything is detected —
detection + flag + a person in the loop, rather than silently rewriting the input.
"""

from __future__ import annotations

import re

from .schemas import DecisionRequest, EvidencePack

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"ignore\s+(all\s+)?(the\s+)?(previous|prior|above|earlier)\s+"
            r"(instructions|prompts?|rules|context)",
            re.I,
        ),
        "ignore-previous-instructions",
    ),
    (re.compile(r"disregard\s+(all\s+)?(previous|prior|above|the)\b", re.I), "disregard-instructions"),
    (re.compile(r"\b(system|developer)\s+prompt\b", re.I), "references-system-prompt"),
    (re.compile(r"\byou\s+are\s+now\b", re.I), "role-override"),
    (re.compile(r"^\s*(system|assistant|developer)\s*:", re.I | re.M), "injected-role-turn"),
    (
        re.compile(r"reveal\s+(your|the)\s+(system\s+)?(prompt|instructions)", re.I),
        "prompt-exfiltration",
    ),
    (re.compile(r"\b(BEGIN|END)\s+(SYSTEM|PROMPT)\b"), "prompt-boundary-injection"),
    (re.compile(r"override\s+(your|the)\s+(rules|guardrails?|safety|instructions)", re.I), "guardrail-override"),
]


def scan_for_injection(text: str) -> list[str]:
    """Return the distinct injection-pattern labels found in `text` (empty if clean)."""
    if not text:
        return []
    return sorted({label for pattern, label in _PATTERNS if pattern.search(text)})


def scan_decision_inputs(request: DecisionRequest, evidence: EvidencePack) -> list[str]:
    """Scan the question, context, supplied inputs, and gathered evidence for injection."""
    chunks = [request.question, request.context or ""]
    chunks += [str(v) for v in request.inputs.values()]
    chunks += [f"{item.claim} {item.value}" for item in evidence.items]
    flags: set[str] = set()
    for chunk in chunks:
        flags.update(scan_for_injection(chunk))
    return sorted(flags)
