"""Structured security audit events.

One JSON object per line. The correlation id ties a command sequence to the
profile and storage events from the same TaskManager. Bodies and bid payloads
are not written here.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any


def emit(event: str, correlation_id: str, log_path: str, **fields: Any) -> None:
    if not log_path:
        return
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "correlation_id": correlation_id,
        "severity": "info",
    }
    for key, value in fields.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            record[key] = value
        else:
            record[key] = str(value)
    directory = os.path.dirname(log_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
