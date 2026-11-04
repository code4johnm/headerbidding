"""Configuration, redaction, and audit-log controls."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from openwpm.config import (
    BrowserParams,
    ManagerParams,
    host_allowed,
    validate_browser_params,
    validate_manager_params,
)
from openwpm.errors import ConfigError
from openwpm.redact import redact_bytes, redact_record, redact_text
from openwpm.security_log import emit

ROOT = Path(__file__).resolve().parents[1]


def test_allowed_domains_required():
    with pytest.raises(ConfigError, match="allowed_domains"):
        validate_manager_params(ManagerParams())
    with pytest.raises(ConfigError, match="allowed_domains"):
        validate_manager_params(ManagerParams(allowed_domains=[]))
    validate_manager_params(ManagerParams(allowed_domains=["example.com"]))


def test_host_allowed_matches_suffix_not_prefix():
    domains = ["example.com", "localhost"]
    assert host_allowed("https://example.com/a", domains)
    assert host_allowed("http://a.example.com/a", domains)
    assert host_allowed("http://localhost:8000/test_pages", domains)
    assert not host_allowed("https://notexample.com/", domains)
    assert not host_allowed("file:///tmp/x", domains)
    assert not host_allowed("http://user:pass@example.com/", domains)
    assert not host_allowed("example.com", domains)


def test_save_content_requires_justification_and_cap():
    params = BrowserParams()
    params.save_content = True
    with pytest.raises(ConfigError, match="save_content=True"):
        validate_browser_params(params)
    params.save_content = "script"
    with pytest.raises(ConfigError, match="justification"):
        validate_browser_params(params)
    params.save_content_justification = "short"
    params.save_content_max_bytes = 100
    with pytest.raises(ConfigError, match="justification"):
        validate_browser_params(params)
    params.save_content_justification = "Retain script bodies for this controlled test."
    params.save_content_max_bytes = 100
    validate_browser_params(params)
    params.save_content_max_bytes = 5_000_001
    with pytest.raises(ConfigError, match="save_content_max_bytes"):
        validate_browser_params(params)


def test_redaction_leaves_bid_fields():
    text = (
        "user@example.com "
        "eyJaaaaaaaa.bbbbbbbb.cccc "
        "AKIAIOSFODNN7EXAMPLE "
        "bearer abcdefghijklmnop " + ("ab" * 16)
    )
    cleaned = redact_text(text)
    assert "user@" not in cleaned
    assert "eyJaaaaaaaa" not in cleaned
    assert "AKIA" not in cleaned
    assert "abcdefghijklmnop" not in cleaned
    assert "[redacted]" in cleaned
    record = redact_record(
        {
            "cpm": 1.8,
            "bidder": "rubicon",
            "ad_id": "slot-1",
            "post_data": "email=user@example.com",
        }
    )
    assert record["cpm"] == 1.8
    assert record["bidder"] == "rubicon"
    assert record["ad_id"] == "slot-1"
    assert "user@" not in record["post_data"]
    assert redact_bytes(b"\xff\xfe") == b"\xff\xfe"


def test_security_log_is_one_json_object_per_line(tmp_path):
    path = tmp_path / "security-audit.jsonl"
    emit("command_sequence", "cid-1", str(path), url="http://localhost/")
    emit("ignored", "cid-1", "")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["event"] == "command_sequence"
    assert record["correlation_id"] == "cid-1"
    assert record["severity"] == "info"
    assert record["url"] == "http://localhost/"


def test_minimal_crawl_check_accepts_hardened_defaults():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "minimal-crawl.py"), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "save_content=False" in completed.stdout
    assert "redact_identifiers=True" in completed.stdout


def test_protect_datadir_fails_closed_without_age(tmp_path):
    completed = subprocess.run(
        ["bash", str(ROOT / "scripts" / "protect-datadir.sh"), str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if shutil.which("age"):
        assert completed.returncode == 0
        assert "plaintext" in completed.stderr
    else:
        assert completed.returncode == 1
        assert "not encrypted" in completed.stderr
