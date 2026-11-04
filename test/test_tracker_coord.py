"""Concurrent JSON updates and path slugs for the transitional tracker layer."""

import json
import multiprocessing
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "TrackerProject" / "src"))
sys.path.insert(0, str(ROOT / "TrackerProject" / "src" / "ScriptUtils"))

import coord  # noqa: E402
from scriptUtils import ScriptUtils  # noqa: E402


class FakeDriver:
    def __init__(self, bids):
        self.current_url = "https://publisher.example/article"
        self.bids = bids

    def execute_script(self, script):
        return self.bids


def _increment(value):
    value["count"] = int(value.get("count", 0)) + 1


def _worker(path, root, times):
    os.environ["HB_TRACKER_ROOT"] = root
    for _ in range(times):
        coord.update_json(path, {"count": 0}, _increment)


def test_concurrent_updates_keep_every_increment(tmp_path, monkeypatch):
    root = tmp_path / "var"
    target = tmp_path / "counter.json"
    monkeypatch.setenv("HB_TRACKER_ROOT", str(root))
    ctx = multiprocessing.get_context("fork")
    procs = [
        ctx.Process(target=_worker, args=(str(target), str(root), 25)) for _ in range(4)
    ]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join(30)
        assert proc.exitcode == 0
    saved = json.loads(target.read_text(encoding="utf-8"))
    assert saved["count"] == 100


def test_site_slug_stays_inside_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HB_TRACKER_ROOT", str(tmp_path / "var"))
    destination = ScriptUtils().getCpm(
        "news",
        "visit-1",
        "https://../../etc/passwd",
        "INTENT",
        driver=FakeDriver([{"cpm": 1.2, "bidder": "rubicon"}]),
    )
    resolved = Path(destination).resolve()
    assert resolved.is_relative_to((tmp_path / "results").resolve())
    assert ".." not in resolved.parts
    assert not (tmp_path / "writing.json").exists()


def test_archive_root_does_not_add_an_extra_prefix(tmp_path, monkeypatch):
    monkeypatch.setenv("HB_TRACKER_ROOT", str(tmp_path / "archive_save"))
    monkeypatch.delenv("HB_ARCHIVE_DIR", raising=False)
    monkeypatch.delenv("HB_TRAINING_MANIFEST", raising=False)
    assert coord.archive_root() == tmp_path / "archive_save"
    assert (
        coord.training_manifest_path()
        == tmp_path / "archive_save" / "ml_testing" / "training_manifest.json"
    )
    monkeypatch.setenv("HB_ARCHIVE_DIR", str(tmp_path / "custom"))
    assert coord.archive_root() == tmp_path / "custom"
