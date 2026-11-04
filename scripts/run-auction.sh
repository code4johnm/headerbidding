#!/bin/sh
# Reproducible header-bidding auction check. No browser and no network.
set -eu
cd "$(dirname "$0")/.."
python3 -m pytest test/test_hb_auction.py test/test_script_utils_bids.py -q
python3 demo.py
