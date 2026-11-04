"""Optional redaction of high-entropy identifiers before storage.

Off unless ``ManagerParams.redact_identifiers`` is set. Bidder names, CPMs,
and ad slot ids are not matched by these patterns. Turning the option on
changes stored HTTP bodies, so content hashes will not match the raw bytes.
"""

from __future__ import annotations

import re

_PATTERNS = (
    re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{4,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-._~+/]{12,}={0,2}"),
    re.compile(r"\b[A-Fa-f0-9]{32,}\b"),
)

_TEXT_FIELDS = {"post_data", "content", "body", "response_body", "message"}


def redact_text(value: str) -> str:
    for pattern in _PATTERNS:
        value = pattern.sub("[redacted]", value)
    return value


def redact_bytes(blob: bytes) -> bytes:
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError:
        return blob
    return redact_text(text).encode("utf-8")


def redact_record(data: dict) -> dict:
    cleaned = dict(data)
    for key in _TEXT_FIELDS:
        value = cleaned.get(key)
        if isinstance(value, str):
            cleaned[key] = redact_text(value)
    return cleaned
