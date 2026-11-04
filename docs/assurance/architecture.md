# Architecture

## What this tree is

`headerbidding` measures Prebid-style auctions. Two paths exist.

The in-process auction (`hb/auction.py`) sends one bid request to each adapter, collects a bid, no-bid, timeout, or error, clears on the highest valid CPM, and records a win notice and an impression for the winner. It does not open a socket. `demo.py` runs that path. Tests in `test/test_hb_auction.py` cover it.

The crawl path is OpenWPM. `TrackerProject/src/ScriptUtils/scriptUtils.py` reads `pbjs.getBidResponses()` and `pbjs.getAllWinningBids()` inside a visited page and writes JSON under `results/`. OpenWPM-1776's `HeaderBiddingCommand` does the same read after `GetCommand` and appends `datadir/hb-events.jsonl`. If the page has no Prebid object, the command records `source: absent`. It does not invent bids for that page.

A third, labeled path lives in OpenWPM-1776 `openwpm/header_bidding.py`. `run_profile_auction()` builds a deterministic auction for the training, testing, or baseline profile. The dashboard uses it for the comparison table and the JSON and CSV export. Those rows are labeled fixtures, not observations from a publisher.

## Data flow

1. Publisher page, only on a real crawl. The browser loads the page. Prebid, if present, runs its own adapter calls. OpenWPM records HTTP, cookies, navigation, JavaScript, and DNS when those instruments are on. Callstack instrumentation stays off.
2. Harvest. The command or `ScriptUtils.getCpm` reads the in-page bid objects and writes them to disk on the researcher machine.
3. Local auction. Adapters are Python callables. Clearing price and notices stay in the result object. Win URLs are formatted and stored. They are not requested.
4. Dashboard. Profile settings are saved in `datadir/crawl-settings.json`. Export reads the fixture auctions, not the live page log.

## Clearing rule

The default price rule is first-price: the highest CPM wins and that CPM is the clearing price. Ties break toward the faster response, then the bidder name. Bids in another currency, below the floor, timed out, or in error do not win. `price_rule="second"` clears at the runner-up CPM plus one cent, capped at the winner's own CPM.

## Trust boundary

The researcher host is trusted. The page and any real bidder endpoint are not. The in-process auction never crosses that boundary. A crawl does.
