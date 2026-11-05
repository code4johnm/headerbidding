"""The dashboard auction stays the local demo and does not touch the network."""

from dashboard.server import auction_document, status_document


def test_dashboard_auction_is_the_local_demo():
    document = auction_document()
    assert document["winner"] == "rubicon"
    assert document["clearing_cpm"] == 1.8
    assert document["request_id"] == "demo-1"
    assert document["price_rule"] == "first"
    status = status_document()
    assert status["crawl"] == "not-started"
    assert status["last"]["winner"] == "rubicon"
