"""The Prebid harvest writer used to crash on indent=True and missing files."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "TrackerProject", "src", "ScriptUtils"))

from scriptUtils import ScriptUtils, dump_json_object  # noqa: E402


class FakeDriver:
    def __init__(self, bids):
        self.current_url = "https://publisher.example/article"
        self.bids = bids

    def execute_script(self, script):
        assert "pbjs.getBidResponses" in script
        return self.bids


def test_get_cpm_writes_rendered_flag_and_creates_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    utils = ScriptUtils()
    bids = [
        {
            "adunit": "/home",
            "adId": "win",
            "bidder": "rubicon",
            "time": 40,
            "cpm": 1.5,
            "msg": "Bid available",
            "rendered": True,
        }
    ]
    destination = utils.getCpm(
        "news",
        "visit-1",
        "https://publisher.example",
        "INTENT",
        driver=FakeDriver(bids),
    )
    saved = json.loads(open(destination, encoding="utf-8").read())
    stored = saved["news"]["https://publisher.example"]["visit-1"][0]
    assert stored["rendered"] is True
    assert stored["cpm"] == 1.5
    done = json.loads(open("testingDone.json", encoding="utf-8").read())
    assert done["news"] == 1


def test_empty_bid_list_records_a_count_without_dropping_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dump_json_object(
        "no_bid_sites.json",
        {
            "https://publisher.example": {
                "count": 2,
                "crawl_info": [{"site": "old", "visit": "0"}],
            }
        },
    )
    utils = ScriptUtils()
    utils.getCpm(
        "news",
        "visit-2",
        "https://publisher.example",
        "NO_INTENT",
        driver=FakeDriver([]),
    )
    recorded = json.loads(open("no_bid_sites.json", encoding="utf-8").read())
    entry = recorded["https://publisher.example"]
    assert entry["count"] == 3
    assert len(entry["crawl_info"]) == 2
    path = tmp_path / "results" / "bids_no_intent" / "publisher.example_news.json"
    assert path.is_file()
