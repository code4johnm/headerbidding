"""Critical path: bid request, adapter responses, clearing, win and impression."""

import json
import os
import subprocess
import sys

from hb.auction import Adapter, Auction, Bid, BidRequest, demo_auction, write_result


def _bid(name, ad_id, cpm, ms, status="bid", currency="USD"):
    def respond(request):
        return Bid(
            bidder=name,
            ad_id=ad_id,
            cpm=cpm,
            currency=currency,
            time_to_respond_ms=ms,
            status=status,
            nurl="https://{0}.example/win".format(name),
            burl="https://{0}.example/imp".format(name),
            message="Bid available" if status == "bid" else status,
        )

    return Adapter(name, respond)


def _request(**overrides):
    values = dict(
        request_id="req-1",
        ad_unit="/test/unit",
        sizes=[[300, 250]],
        timeout_ms=100,
        floor_cpm=0.0,
    )
    values.update(overrides)
    return BidRequest(**values)


def test_first_price_clearing_notifies_winner_only():
    auction = Auction(
        [
            _bid("low", "low-1", 0.40, 10),
            _bid("high", "high-1", 2.50, 20),
            _bid("slow", "slow-1", 0.0, 15, status="no-bid"),
        ],
        price_rule="first",
    )

    def too_slow(request):
        raise TimeoutError("late")

    auction.adapters.append(Adapter("late", too_slow))
    result = auction.run(_request())

    kinds = [event.kind for event in result.events]
    assert kinds[0] == "bid_request"
    assert kinds.count("adapter_response") == 4
    assert "auction_cleared" in kinds
    assert "win_notice" in kinds
    assert "impression" in kinds
    assert result.winner.bidder == "high"
    assert result.clearing_cpm == 2.50
    notices = [event for event in result.events if event.kind == "win_notice"]
    assert len(notices) == 1
    assert notices[0].bidder == "high"
    assert "price=2.5000" in notices[0].detail["nurl"]
    rendered = [row for row in result.pbjs_records() if row["rendered"]]
    assert [row["adId"] for row in rendered] == ["high-1"]
    assert result.error_rate == 0.25


def test_second_price_uses_runner_up_plus_one_cent():
    auction = Auction(
        [_bid("a", "a", 1.20, 10), _bid("b", "b", 3.00, 11)],
        price_rule="second",
    )
    result = auction.run(_request())
    assert result.winner.bidder == "b"
    assert result.clearing_cpm == 1.21


def test_timeout_and_floor_and_currency_do_not_win():
    def over_time(request):
        return Bid(
            bidder="slow",
            ad_id="slow",
            cpm=9.0,
            currency="USD",
            time_to_respond_ms=request.timeout_ms + 1,
            status="bid",
            nurl="https://slow.example/win",
            burl="https://slow.example/imp",
        )

    auction = Auction(
        [
            Adapter("slow", over_time),
            _bid("cheap", "cheap", 0.10, 5),
            _bid("euro", "euro", 8.0, 5, currency="EUR"),
        ]
    )
    result = auction.run(_request(floor_cpm=0.50, timeout_ms=50))
    assert result.winner is None
    assert result.clearing_cpm is None
    assert not any(event.kind == "win_notice" for event in result.events)
    assert any(bid.status == "timeout" for bid in result.responses)


def test_tie_prefers_faster_response():
    auction = Auction([_bid("late", "late", 1.0, 40), _bid("early", "early", 1.0, 12)])
    result = auction.run(_request())
    assert result.winner.bidder == "early"


def test_adapter_exception_is_an_error_not_a_crash():
    def boom(request):
        raise RuntimeError("adapter down")

    result = Auction([Adapter("bad", boom), _bid("ok", "ok", 0.8, 9)]).run(_request())
    assert result.winner.bidder == "ok"
    assert result.responses[0].status == "error"
    assert "adapter down" in result.responses[0].message


def test_demo_and_export(tmp_path):
    result = demo_auction()
    assert result.winner.bidder == "rubicon"
    path = tmp_path / "auction.json"
    write_result(str(path), result)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["winner"] == "rubicon"
    assert {event["kind"] for event in saved["events"]} >= {
        "bid_request",
        "adapter_response",
        "auction_cleared",
        "win_notice",
        "impression",
    }
    completed = subprocess.run(
        [sys.executable, "demo.py"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert "win_notice: 1" in completed.stdout
    assert "impression: 1" in completed.stdout
