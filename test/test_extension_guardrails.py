"""Source checks for privileged extension guardrails.

``node --check`` parses the experiment APIs Firefox loads directly.
The pre-instrumentation gate lives in ``Extension/src/feature.ts`` and
takes effect when the extension bundle is rebuilt.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _text(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def test_socket_connect_rejects_non_loopback():
    source = _text("Extension/bundled/privileged/sockets/api.js")
    connect = source.split("connect(id, host, port)", 1)[1]
    assert connect.index("isLoopbackHost(host)") < connect.index("createTransport")
    assert "127.0.0.1" in source
    assert "Unsupported serialization" in source


def test_profile_filenames_reject_traversal():
    source = _text("Extension/bundled/privileged/profileDirIO/api.js")
    assert "function isSafeProfileFilename" in source
    assert '".."' in source or "'..'" in source
    assert source.index("isSafeProfileFilename") < source.index("PathUtils.join")


def test_pre_instrumentation_eval_is_gated_and_instrument_eval_remains():
    feature = _text("Extension/src/feature.ts")
    assert "allow_pre_instrumentation_eval" in feature
    instruments = _text("Extension/src/lib/js-instruments.ts")
    assert "eval(item.object)" in instruments
    manifest = _text("Extension/bundled/manifest.json")
    assert "unsafe-eval" in manifest


def test_privileged_api_files_parse():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    for relative in (
        "Extension/bundled/privileged/sockets/api.js",
        "Extension/bundled/privileged/profileDirIO/api.js",
    ):
        subprocess.run([node, "--check", str(ROOT / relative)], check=True)
