"""Exception transport between BrowserManager processes.

The status queue used to carry ``pickle.dumps(sys.exc_info())``. A pickled
exception can execute code on load. This module sends a JSON object and
rebuilds only an allow-listed exception type. Anything else becomes
``ResearchInstrumentError`` and keeps the original type name in the message.
"""

from __future__ import annotations

import json
import sys
import traceback
from types import TracebackType
from typing import Optional, Tuple, Type

from openwpm.errors import (
    BrowserConfigError,
    BrowserCrashError,
    CommandExecutionError,
    ConfigError,
    ProfileLoadError,
    ResearchInstrumentError,
)

SCHEMA = "openwpm.exc.v1"

_STATIC: dict[str, Type[BaseException]] = {
    "Exception": Exception,
    "RuntimeError": RuntimeError,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "AttributeError": AttributeError,
    "OSError": OSError,
    "TimeoutError": TimeoutError,
    "BrowserCrashError": BrowserCrashError,
    "BrowserConfigError": BrowserConfigError,
    "ProfileLoadError": ProfileLoadError,
    "CommandExecutionError": CommandExecutionError,
    "ConfigError": ConfigError,
    "ResearchInstrumentError": ResearchInstrumentError,
}


def _allowed() -> dict[str, Type[BaseException]]:
    allowed = dict(_STATIC)
    try:
        from selenium.common.exceptions import TimeoutException, WebDriverException
    except ImportError:
        return allowed
    allowed["WebDriverException"] = WebDriverException
    allowed["TimeoutException"] = TimeoutException
    return allowed


def dump_exception(
    exc_info: Optional[
        Tuple[
            Optional[Type[BaseException]],
            Optional[BaseException],
            Optional[TracebackType],
        ]
    ] = None,
) -> bytes:
    if exc_info is None:
        exc_info = sys.exc_info()
    exc_type, value, tb = exc_info
    name = exc_type.__name__ if exc_type is not None else "Exception"
    payload = {
        "schema": SCHEMA,
        "type": name if name in _allowed() else "ResearchInstrumentError",
        "original_type": name,
        "message": "" if value is None else str(value),
        "traceback": "".join(traceback.format_exception(exc_type, value, tb)),
    }
    if name not in _allowed():
        payload["message"] = "{0}: {1}".format(name, payload["message"])
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def load_exception(payload: bytes) -> Tuple[BaseException, str]:
    if payload.startswith(b"\x80") or payload.startswith(b"(c"):
        raise ValueError("rejected pickle exception payload")
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("rejected exception payload") from exc
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("rejected exception payload")
    name = data.get("type")
    message = data.get("message")
    tb_text = data.get("traceback")
    if (
        not isinstance(name, str)
        or not isinstance(message, str)
        or not isinstance(tb_text, str)
    ):
        raise ValueError("rejected exception payload")
    cls = _allowed().get(name, ResearchInstrumentError)
    if cls is ResearchInstrumentError and name != "ResearchInstrumentError":
        message = "{0}: {1}".format(name, message)
    if cls is CommandExecutionError:
        exc = CommandExecutionError(message, None)
    else:
        exc = cls(message)
    return exc, tb_text
