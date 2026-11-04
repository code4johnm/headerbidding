"""Filesystem coordination for the transitional TrackerProject layer.

``writing.json`` used to be treated as a mutex. Nothing held it across a
read-modify-write, so two harvests could drop each other's bid rows.
``update_json`` holds an exclusive ``fcntl`` lock for the whole update.

Paths come from ``HB_TRACKER_ROOT``. When that variable is unset, files
live under ``TrackerProject/var`` relative to this repository.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator


def tracker_root() -> Path:
    raw = os.environ.get("HB_TRACKER_ROOT", "").strip()
    root = (
        Path(raw).expanduser() if raw else Path(__file__).resolve().parents[1] / "var"
    )
    root.mkdir(parents=True, exist_ok=True)
    return root


def tracker_path(*parts: str) -> Path:
    path = tracker_root().joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _lock_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in name)
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:16]
    return (cleaned[:80] or "lock") + "-" + digest + ".lock"


def archive_root() -> Path:
    """Parent of ``ml_training`` and ``ml_testing``.

    ``HB_ARCHIVE_DIR`` selects that parent explicitly. When it is unset, the
    parent is ``HB_TRACKER_ROOT`` (or ``TrackerProject/var``). The root is not
    given an extra ``archive/`` prefix, so pointing ``HB_TRACKER_ROOT`` at an
    old archive tree does not double the path.
    """
    raw = os.environ.get("HB_ARCHIVE_DIR", "").strip()
    path = Path(raw).expanduser() if raw else tracker_root()
    path.mkdir(parents=True, exist_ok=True)
    return path


def training_manifest_path() -> Path:
    raw = os.environ.get("HB_TRAINING_MANIFEST", "").strip()
    if raw:
        path = Path(raw).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return tracker_path("ml_testing", "training_manifest.json")


def safe_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ".-_" else "_" for ch in str(value))
    while ".." in cleaned:
        cleaned = cleaned.replace("..", "_")
    cleaned = cleaned.strip("._")[:180]
    return cleaned or "artifact"


def site_slug(value: str) -> str:
    """Hostname slug safe to join onto a results directory."""
    raw = value.split("://", 1)[1] if "://" in value else value
    host = raw.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    return safe_name(host)


@contextmanager
def exclusive_lock(name: str) -> Iterator[None]:
    handle_path = tracker_root() / "locks" / _lock_name(name)
    handle_path.parent.mkdir(parents=True, exist_ok=True)
    with open(handle_path, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def update_json(path: str, default: Any, mutator: Callable[[Any], None]) -> Any:
    """Apply ``mutator`` to the JSON document at ``path`` under one lock."""
    absolute = os.path.abspath(path)
    with exclusive_lock(absolute):
        try:
            with open(absolute, encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, ValueError):
            value = default
        if not isinstance(value, type(default)):
            value = default
        mutator(value)
        directory = os.path.dirname(absolute)
        if directory:
            os.makedirs(directory, exist_ok=True)
        temporary = absolute + ".tmp"
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=4, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary, absolute)
        return value
