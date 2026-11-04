"""JSON exception transport rejects pickle and unknown types."""

import json

import pytest

from openwpm.errors import CommandExecutionError, ResearchInstrumentError
from openwpm.ipc_exceptions import SCHEMA, dump_exception, load_exception


class WeirdError(Exception):
    pass


def test_round_trip_keeps_allow_listed_type():
    try:
        raise ValueError("bid floor")
    except ValueError:
        payload = dump_exception()
    exc, tb_text = load_exception(payload)
    assert type(exc) is ValueError
    assert "bid floor" in str(exc)
    assert "ValueError" in tb_text
    assert json.loads(payload)["schema"] == SCHEMA


def test_command_execution_error_round_trip():
    try:
        raise CommandExecutionError("outside allow list", "get")
    except CommandExecutionError:
        payload = dump_exception()
    exc, _tb_text = load_exception(payload)
    assert type(exc) is CommandExecutionError
    assert exc.command is None
    assert "outside allow list" in str(exc)


def test_unknown_type_is_not_evaluated():
    try:
        raise WeirdError("boom")
    except WeirdError:
        payload = dump_exception()
    exc, _tb_text = load_exception(payload)
    assert type(exc) is ResearchInstrumentError
    assert "WeirdError" in str(exc)


def test_pickle_payload_is_rejected():
    with pytest.raises(ValueError):
        load_exception(b"\x80\x04\x95")
    with pytest.raises(ValueError):
        load_exception(b"(cos\nsystem\n")
