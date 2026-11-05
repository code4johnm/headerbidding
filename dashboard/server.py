"""Header-bidding console.

Runs the in-process auction from ``hb.auction``. The page can set the bid
request, the price rule, and the local adapters. No browser is started and
no publisher site is visited. Stdlib only. Bind ``0.0.0.0`` so a phone on
the LAN can open it.
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(os.environ.get("HB_ROOT", ""))
if not (ROOT / "hb" / "auction.py").is_file():
    ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hb.auction import (  # noqa: E402
    Adapter,
    Auction,
    Bid,
    BidRequest,
    demo_adapters,
    demo_auction,
    result_document,
)

PAGE = Path(__file__).resolve().parent / "index.html"
HOST = os.environ.get("HB_DASH_HOST", "0.0.0.0")
PORT = int(os.environ.get("HB_DASH_PORT", "8771"))
_LOCK = threading.Lock()
_LAST: dict | None = None
_NAME = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")
_STATUSES = {"bid", "no-bid", "timeout", "error"}


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def firefox_present() -> bool:
    return (ROOT / "firefox-bin" / "firefox-bin").is_file()


def _text(value: object, default: str, limit: int, label: str) -> str:
    if value is None or value == "":
        return default
    if not isinstance(value, str):
        raise ApiError(400, label + " must be text")
    text = " ".join(value.split())
    if not text:
        return default
    return text[:limit]


def _number(value: object, default: float, low: float, high: float, label: str) -> float:
    if value is None or value == "":
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ApiError(400, label + " must be a number")
    if value < low or value > high:
        raise ApiError(400, label + " is out of range")
    return float(value)


def _whole(value: object, default: int, low: int, high: int, label: str) -> int:
    if value is None or value == "":
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise ApiError(400, label + " must be an integer")
    if value < low or value > high:
        raise ApiError(400, label + " is out of range")
    return value


def _sizes(value: object) -> list:
    if value is None:
        return [[728, 90], [300, 250]]
    if not isinstance(value, list) or not value or len(value) > 8:
        raise ApiError(400, "sizes must be 1 to 8 pairs")
    sizes = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ApiError(400, "each size is [width, height]")
        width, height = pair
        if (
            isinstance(width, bool)
            or isinstance(height, bool)
            or not isinstance(width, int)
            or not isinstance(height, int)
        ):
            raise ApiError(400, "size values must be integers")
        if width < 1 or height < 1 or width > 10000 or height > 10000:
            raise ApiError(400, "size is out of range")
        sizes.append([width, height])
    return sizes


def _request_view(request: BidRequest) -> dict:
    return {
        "request_id": request.request_id,
        "ad_unit": request.ad_unit,
        "sizes": request.sizes,
        "timeout_ms": request.timeout_ms,
        "currency": request.currency,
        "floor_cpm": request.floor_cpm,
    }


def _one_adapter(item: object) -> Adapter:
    if not isinstance(item, dict):
        raise ApiError(400, "each adapter must be an object")
    name = item.get("name")
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise ApiError(400, "adapter name must be letters, numbers, _ or -")
    status = item.get("status") or "bid"
    if status not in _STATUSES:
        raise ApiError(400, "adapter status must be bid, no-bid, timeout, or error")
    message = _text(item.get("message"), "", 200, "message")
    if status == "timeout":
        def timed_out(request: BidRequest, _name=name) -> Bid:
            raise TimeoutError("adapter exceeded {0}ms".format(request.timeout_ms))

        return Adapter(name, timed_out)
    if status == "error":
        detail = message or "adapter error"

        def failed(request: BidRequest, _name=name, text=detail) -> Bid:
            raise RuntimeError(text)

        return Adapter(name, failed)
    cpm = _number(item.get("cpm"), 0.0, 0, 100000, "cpm")
    ms = _whole(item.get("ms"), 0, 0, 60000, "ms")
    currency = _text(item.get("currency"), "USD", 3, "currency").upper()
    if not _CURRENCY.fullmatch(currency):
        raise ApiError(400, "currency must be three letters")
    width = _whole(item.get("width"), 300, 0, 10000, "width")
    height = _whole(item.get("height"), 250, 0, 10000, "height")
    ad_id = _text(item.get("ad_id"), name + "-1", 40, "ad_id")

    def respond(
        request: BidRequest,
        adapter_name=name,
        bid_id=ad_id,
        bid_cpm=cpm,
        bid_currency=currency,
        bid_ms=ms,
        bid_status=status,
        bid_width=width,
        bid_height=height,
        bid_message=message,
    ) -> Bid:
        return Bid(
            bidder=adapter_name,
            ad_id=bid_id,
            cpm=bid_cpm,
            currency=bid_currency,
            time_to_respond_ms=bid_ms,
            status=bid_status,
            width=bid_width,
            height=bid_height,
            nurl="https://{0}.example/win".format(adapter_name),
            burl="https://{0}.example/imp".format(adapter_name),
            message=bid_message or ("Bid available" if bid_status == "bid" else bid_status),
        )

    return Adapter(name, respond)


def _adapters(value: object) -> list:
    if value is None:
        return demo_adapters()
    if not isinstance(value, list) or not value or len(value) > 12:
        raise ApiError(400, "adapters must be 1 to 12 entries")
    return [_one_adapter(item) for item in value]


def _document(result) -> dict:
    document = result_document(result)
    document["request"] = _request_view(result.request)
    return document


def auction_document(spec: dict | None = None) -> dict:
    """Clear one local auction. No network and no browser.

    An empty spec, or ``{"demo": true}`` alone, is ``demo_auction()``.
    Any other object builds a ``BidRequest`` and an ``Auction``.
    """
    global _LAST
    if not spec or (spec.get("demo") is True and set(spec) <= {"demo"}):
        result = demo_auction()
    else:
        if not isinstance(spec, dict):
            raise ApiError(400, "body must be a JSON object")
        price_rule = spec.get("price_rule") or "first"
        if price_rule not in {"first", "second"}:
            raise ApiError(400, "price_rule must be first or second")
        currency = _text(spec.get("currency"), "USD", 3, "currency").upper()
        if not _CURRENCY.fullmatch(currency):
            raise ApiError(400, "currency must be three letters")
        request = BidRequest(
            request_id=_text(spec.get("request_id"), "demo-1", 80, "request_id"),
            ad_unit=_text(spec.get("ad_unit"), "/demo/homepage/leaderboard", 120, "ad_unit"),
            sizes=_sizes(spec.get("sizes")),
            timeout_ms=_whole(spec.get("timeout_ms"), 200, 1, 60000, "timeout_ms"),
            currency=currency,
            floor_cpm=_number(spec.get("floor_cpm"), 0.5, 0, 100000, "floor_cpm"),
        )
        result = Auction(_adapters(spec.get("adapters")), price_rule=price_rule).run(request)
    document = _document(result)
    with _LOCK:
        _LAST = document
    return document


def status_document() -> dict:
    with _LOCK:
        last = _LAST
    return {
        "firefox_binary": firefox_present(),
        "crawl": "not-started",
        "last": last,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "headerbidding-dash"

    def log_message(self, fmt: str, *args: object) -> None:
        print("{0} {1}".format(self.address_string(), fmt % args), flush=True)

    def send_json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_page(self) -> None:
        raw = PAGE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            if path in ("/", "/index.html"):
                self.send_page()
                return
            if path == "/api/status":
                self.send_json(200, status_document())
                return
            self.send_json(404, {"error": "not found"})
        except ApiError as exc:
            self.send_json(exc.status, {"error": exc.message})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or "0")
        if length < 0 or length > 32768:
            self.send_json(413, {"error": "body is too large"})
            return
        spec = None
        if length:
            try:
                loaded = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                self.send_json(400, {"error": "body must be JSON"})
                return
            if loaded is None:
                spec = None
            elif not isinstance(loaded, dict):
                self.send_json(400, {"error": "body must be a JSON object"})
                return
            else:
                spec = loaded or None
        try:
            if path != "/api/auction":
                self.send_json(404, {"error": "not found"})
                return
            self.send_json(200, auction_document(spec))
        except ApiError as exc:
            self.send_json(exc.status, {"error": exc.message})


class Server(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    httpd = Server((HOST, PORT), Handler)
    print(
        "header bidding dashboard listening on {0}:{1}".format(HOST, PORT),
        flush=True,
    )
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
