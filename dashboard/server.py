"""Header-bidding console.

Runs the in-process auction from ``hb.auction``. No browser is started and
no publisher site is visited. Stdlib only. Bind ``0.0.0.0`` so a phone on
the LAN can open it.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(os.environ.get("HB_ROOT", ""))
if not (ROOT / "hb" / "auction.py").is_file():
    ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hb.auction import demo_auction, result_document  # noqa: E402

PAGE = Path(__file__).resolve().parent / "index.html"
HOST = os.environ.get("HB_DASH_HOST", "0.0.0.0")
PORT = int(os.environ.get("HB_DASH_PORT", "8771"))
_LOCK = threading.Lock()
_LAST: dict | None = None


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def firefox_present() -> bool:
    return (ROOT / "firefox-bin" / "firefox-bin").is_file()


def auction_document() -> dict:
    """Clear the local demo auction. No network and no browser."""
    global _LAST
    document = result_document(demo_auction())
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
        if length > 4096:
            self.send_json(413, {"error": "body is too large"})
            return
        if length:
            self.rfile.read(length)
        try:
            if path != "/api/auction":
                self.send_json(404, {"error": "not found"})
                return
            document = auction_document()
            if document.get("winner") != "rubicon" or document.get("clearing_cpm") != 1.8:
                self.send_json(500, {"error": "unexpected clearing result"})
                return
            self.send_json(200, document)
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
