"""Prebid-style header bidding auction.

The flow is the one a page runs before an ad renders:

1. The publisher sends one bid request to each adapter.
2. Each adapter returns a bid, a no-bid, a timeout, or an error.
3. The auction clears on the highest valid CPM. Ties go to the faster
   response, then to the bidder name. The default price rule is first-price,
   which is what current Prebid.js auctions use. Second-price is available
   for older stacks and adds one cent to the runner-up.
4. The winner gets a win notice. An impression is recorded only when that
   creative is marked rendered.

No adapter is contacted over the network. Callers pass callables so the
same clearing rules run in unit tests and inside an OpenWPM visit.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, List, Optional
from urllib.parse import urlencode


@dataclass
class BidRequest:
    request_id: str
    ad_unit: str
    sizes: List[List[int]]
    timeout_ms: int = 200
    currency: str = "USD"
    floor_cpm: float = 0.0


@dataclass
class Bid:
    bidder: str
    ad_id: str
    cpm: float
    currency: str
    time_to_respond_ms: int
    status: str
    width: int = 0
    height: int = 0
    nurl: str = ""
    burl: str = ""
    message: str = ""


@dataclass
class Adapter:
    name: str
    respond: Callable[[BidRequest], Bid]


@dataclass
class AuctionEvent:
    kind: str
    bidder: str
    detail: dict


@dataclass
class AuctionResult:
    request: BidRequest
    responses: List[Bid]
    winner: Optional[Bid]
    clearing_cpm: Optional[float]
    price_rule: str
    events: List[AuctionEvent] = field(default_factory=list)
    elapsed_ms: float = 0.0

    @property
    def error_rate(self) -> float:
        if not self.responses:
            return 0.0
        bad = sum(1 for bid in self.responses if bid.status in {"timeout", "error"})
        return bad / float(len(self.responses))

    def pbjs_records(self) -> List[dict]:
        """Shape extracted by TrackerProject ScriptUtils from pbjs.getBidResponses."""
        winner_id = self.winner.ad_id if self.winner else None
        records = []
        for bid in self.responses:
            if bid.status != "bid":
                continue
            records.append(
                {
                    "adunit": self.request.ad_unit,
                    "adId": bid.ad_id,
                    "bidder": bid.bidder,
                    "time": bid.time_to_respond_ms,
                    "cpm": bid.cpm,
                    "msg": bid.message or "Bid available",
                    "rendered": bid.ad_id == winner_id,
                    "clearingCpm": (
                        self.clearing_cpm if bid.ad_id == winner_id else None
                    ),
                }
            )
        return records


def _priced_url(template: str, bid: Bid, clearing_cpm: float) -> str:
    if not template:
        return ""
    query = urlencode(
        {
            "bidder": bid.bidder,
            "adid": bid.ad_id,
            "price": "{0:.4f}".format(clearing_cpm),
            "cur": bid.currency,
        }
    )
    join = "&" if "?" in template else "?"
    return template + join + query


class Auction:
    def __init__(self, adapters: List[Adapter], price_rule: str = "first") -> None:
        if price_rule not in {"first", "second"}:
            raise ValueError("price_rule must be 'first' or 'second'")
        self.adapters = adapters
        self.price_rule = price_rule

    def run(self, request: BidRequest) -> AuctionResult:
        started = time.perf_counter()
        events = [
            AuctionEvent(
                "bid_request",
                "*",
                {
                    "request_id": request.request_id,
                    "ad_unit": request.ad_unit,
                    "timeout_ms": request.timeout_ms,
                    "adapters": [adapter.name for adapter in self.adapters],
                },
            )
        ]
        responses: List[Bid] = []
        for adapter in self.adapters:
            bid = self._call_adapter(adapter, request)
            responses.append(bid)
            events.append(
                AuctionEvent(
                    "adapter_response",
                    adapter.name,
                    {
                        "status": bid.status,
                        "cpm": bid.cpm,
                        "time_to_respond_ms": bid.time_to_respond_ms,
                        "ad_id": bid.ad_id,
                        "message": bid.message,
                    },
                )
            )

        eligible = [
            bid
            for bid in responses
            if bid.status == "bid"
            and bid.currency == request.currency
            and bid.cpm >= request.floor_cpm
        ]
        eligible.sort(key=lambda bid: (-bid.cpm, bid.time_to_respond_ms, bid.bidder))
        winner = eligible[0] if eligible else None
        clearing = None
        if winner is not None:
            if self.price_rule == "second" and len(eligible) > 1:
                clearing = round(eligible[1].cpm + 0.01, 4)
                if clearing > winner.cpm:
                    clearing = winner.cpm
            else:
                clearing = winner.cpm
            events.append(
                AuctionEvent(
                    "auction_cleared",
                    winner.bidder,
                    {
                        "ad_id": winner.ad_id,
                        "clearing_cpm": clearing,
                        "price_rule": self.price_rule,
                        "bid_count": len(eligible),
                    },
                )
            )
            notice = _priced_url(winner.nurl, winner, clearing)
            events.append(
                AuctionEvent(
                    "win_notice",
                    winner.bidder,
                    {"nurl": notice, "clearing_cpm": clearing, "ad_id": winner.ad_id},
                )
            )
            impression = _priced_url(winner.burl, winner, clearing)
            events.append(
                AuctionEvent(
                    "impression",
                    winner.bidder,
                    {
                        "burl": impression,
                        "rendered": True,
                        "ad_id": winner.ad_id,
                        "ad_unit": request.ad_unit,
                    },
                )
            )
        else:
            events.append(
                AuctionEvent(
                    "auction_cleared",
                    "",
                    {
                        "clearing_cpm": None,
                        "price_rule": self.price_rule,
                        "bid_count": 0,
                    },
                )
            )

        elapsed = (time.perf_counter() - started) * 1000.0
        return AuctionResult(
            request=request,
            responses=responses,
            winner=winner,
            clearing_cpm=clearing,
            price_rule=self.price_rule,
            events=events,
            elapsed_ms=elapsed,
        )

    def _call_adapter(self, adapter: Adapter, request: BidRequest) -> Bid:
        try:
            bid = adapter.respond(request)
        except TimeoutError as exc:
            return Bid(
                bidder=adapter.name,
                ad_id="",
                cpm=0.0,
                currency=request.currency,
                time_to_respond_ms=request.timeout_ms,
                status="timeout",
                message=str(exc) or "timeout",
            )
        except Exception as exc:
            return Bid(
                bidder=adapter.name,
                ad_id="",
                cpm=0.0,
                currency=request.currency,
                time_to_respond_ms=0,
                status="error",
                message=str(exc) or exc.__class__.__name__,
            )
        if bid.time_to_respond_ms > request.timeout_ms:
            bid.status = "timeout"
            bid.message = bid.message or "exceeded bidder timeout"
            bid.cpm = 0.0
        return bid


def result_document(result: AuctionResult) -> dict:
    return {
        "request_id": result.request.request_id,
        "ad_unit": result.request.ad_unit,
        "price_rule": result.price_rule,
        "clearing_cpm": result.clearing_cpm,
        "winner": result.winner.bidder if result.winner else None,
        "elapsed_ms": round(result.elapsed_ms, 3),
        "error_rate": result.error_rate,
        "responses": [asdict(bid) for bid in result.responses],
        "events": [asdict(event) for event in result.events],
        "pbjs": result.pbjs_records(),
    }


def write_result(path: str, result: AuctionResult) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(result_document(result), handle, indent=2)
        handle.write("\n")


def _bid(
    name: str, ad_id: str, cpm: float, ms: int, status: str = "bid"
) -> Callable[[BidRequest], Bid]:
    def respond(request: BidRequest) -> Bid:
        return Bid(
            bidder=name,
            ad_id=ad_id,
            cpm=cpm,
            currency="USD",
            time_to_respond_ms=ms,
            status=status,
            width=300,
            height=250,
            nurl="https://{0}.example/win".format(name),
            burl="https://{0}.example/imp".format(name),
            message="Bid available" if status == "bid" else status,
        )

    return respond


def demo_adapters() -> List[Adapter]:
    def timed_out(request: BidRequest) -> Bid:
        raise TimeoutError("adapter exceeded {0}ms".format(request.timeout_ms))

    return [
        Adapter("appnexus", _bid("appnexus", "apn-1", 1.20, 40)),
        Adapter("rubicon", _bid("rubicon", "rub-1", 1.80, 55)),
        Adapter("ix", timed_out),
        Adapter("pubmatic", _bid("pubmatic", "pub-1", 0.0, 30, status="no-bid")),
    ]


def demo_auction() -> AuctionResult:
    auction = Auction(demo_adapters(), price_rule="first")
    request = BidRequest(
        request_id="demo-1",
        ad_unit="/demo/homepage/leaderboard",
        sizes=[[728, 90], [300, 250]],
        timeout_ms=200,
        floor_cpm=0.5,
    )
    return auction.run(request)
