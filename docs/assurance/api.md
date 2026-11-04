# API reference

## `hb.auction`

`BidRequest(request_id, ad_unit, sizes, timeout_ms=200, currency="USD", floor_cpm=0.0)`

`Adapter(name, respond)`. `respond(request)` returns a `Bid` or raises `TimeoutError` or another exception.

`Auction(adapters, price_rule="first").run(request)` returns `AuctionResult`.

`AuctionResult.events` is ordered: one `bid_request`, one `adapter_response` per adapter, one `auction_cleared`, and, only when there is a winner, one `win_notice` and one `impression`.

`AuctionResult.pbjs_records()` matches the fields `ScriptUtils` stores from Prebid: `adunit`, `adId`, `bidder`, `time`, `cpm`, `msg`, `rendered`. `rendered` is true only for the winner.

`AuctionResult.error_rate` is the share of responses whose status is `timeout` or `error`.

`write_result(path, result)` writes the JSON document.

`demo_auction()` is the fixed four-adapter example used by `demo.py`. The winner is `rubicon` at CPM 1.80.

## `ScriptUtils.getCpm`

`getCpm(iab, visit, site, crawl_type, driver=...)` runs the Prebid extraction script and writes `results/bids_intent/` or `results/bids_no_intent/`. Missing files are created. JSON is written with `indent=4`. `indent=True` used to raise `TypeError` and drop the file.

## OpenWPM-1776

`apply_profile(browser_params, settings)` sets `tp_cookies`, timezone, user-agent pref, fingerprint-resistance pref, and a window-size launch argument.

`HeaderBiddingCommand(profile, output_path).execute(...)` appends one JSON object per visit to `output_path`. A Prebid page yields `source: page`. Any other page yields `source: absent`.

`compare_profiles()` and `dataset_document()` return the training, testing, and baseline fixture auctions. `dataset_csv()` is the flat export.

Dashboard routes:

| Method and path | Behavior |
| --- | --- |
| `GET /api/profiles` | Profile presets and the comparison rows |
| `GET /api/export.json` | Fixture dataset |
| `GET /api/export.csv` | Same rows, CSV |
| `POST /api/settings` | Saves crawl settings, including the selected profile |

Profile names are `training`, `testing`, and `baseline`.
