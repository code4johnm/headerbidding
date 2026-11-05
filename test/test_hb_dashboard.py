"""The dashboard auction is the local auction and does not touch the network."""

import pytest

from dashboard.server import ApiError, auction_document, status_document


def test_dashboard_auction_is_the_local_demo():
    document = auction_document()
    assert document["winner"] == "rubicon"
    assert document["clearing_cpm"] == 1.8
    assert document["request_id"] == "demo-1"
    assert document["price_rule"] == "first"
    assert document["request"]["floor_cpm"] == 0.5
    assert document["request"]["timeout_ms"] == 200
    assert {event["kind"] for event in document["events"]} >= {
        "bid_request",
        "adapter_response",
        "auction_cleared",
        "win_notice",
        "impression",
    }
    assert document["pbjs"]
    assert document["error_rate"] == 0.25
    status = status_document()
    assert status["crawl"] == "not-started"
    assert status["last"]["winner"] == "rubicon"


def test_page_can_set_price_rule_floor_and_adapters():
    second = auction_document({"price_rule": "second"})
    assert second["winner"] == "rubicon"
    assert second["clearing_cpm"] == 1.21
    assert second["request"]["currency"] == "USD"
    custom = auction_document(
        {
            "price_rule": "first",
            "floor_cpm": 0,
            "timeout_ms": 100,
            "currency": "USD",
            "request_id": "req-web",
            "ad_unit": "/web/unit",
            "sizes": [[300, 250]],
            "adapters": [
                {"name": "low", "cpm": 0.4, "ms": 10, "status": "bid"},
                {"name": "high", "cpm": 2.5, "ms": 20, "status": "bid"},
                {"name": "late", "status": "timeout"},
                {"name": "down", "status": "error", "message": "adapter down"},
            ],
        }
    )
    assert custom["winner"] == "high"
    assert custom["clearing_cpm"] == 2.5
    assert custom["request"]["ad_unit"] == "/web/unit"
    notices = [event for event in custom["events"] if event["kind"] == "win_notice"]
    assert notices[0]["detail"]["nurl"].startswith("https://high.example/win")
    assert "price=2.5000" in notices[0]["detail"]["nurl"]
    rendered = [row for row in custom["pbjs"] if row["rendered"]]
    assert rendered[0]["bidder"] == "high"
    assert custom["error_rate"] == 0.5


def test_bad_auction_fields_are_refused():
    with pytest.raises(ApiError):
        auction_document({"price_rule": "third"})
    with pytest.raises(ApiError):
        auction_document({"adapters": []})
