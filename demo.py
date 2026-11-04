#!/usr/bin/env python3
"""Run the header-bidding auction without a browser.

The previous demo imported ``automation`` and called
``TaskManager.load_default_params``. This tree's measurement stack is the
``openwpm`` package, and ``TaskManager`` now requires dataclass configs plus
a storage provider. That import failed before any bid was sent.

    python3 demo.py
    python3 -m pytest test/test_hb_auction.py test/test_script_utils_bids.py -q

A live crawl still belongs to OpenWPM's TaskManager and is not started here.
"""

from __future__ import annotations

import argparse
import json
import sys

from hb.auction import demo_auction, result_document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local header-bidding auction."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Accepted so the existing CI demo job can call this command. No browser is started.",
    )
    parser.parse_args()
    result = demo_auction()
    document = result_document(result)
    stages = [
        "bid_request",
        "adapter_response",
        "auction_cleared",
        "win_notice",
        "impression",
    ]
    print("header bidding auction {0}".format(document["request_id"]))
    for stage in stages:
        rows = [event for event in document["events"] if event["kind"] == stage]
        print("{0}: {1}".format(stage, len(rows)))
        for event in rows:
            print(
                "  {0} {1}".format(
                    event["bidder"] or "-", json.dumps(event["detail"], sort_keys=True)
                )
            )
    if document["winner"] != "rubicon" or document["clearing_cpm"] != 1.80:
        print("unexpected clearing result", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
