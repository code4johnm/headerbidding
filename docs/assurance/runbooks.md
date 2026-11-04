# Runbooks

## Deploy the auction check

There is nothing to deploy. Run `sh scripts/run-auction.sh` on a machine with Python 3.12 or the system Python 3. The command exits non-zero if the demo winner is not `rubicon` at CPM 1.80.

## Deploy a crawl

Use the OpenWPM-1776 dashboard at `http://192.168.0.47:8770/`. Save the link list and the profile, then Launch crawl. That creates Job `openwpm-crawl`. Stop crawl deletes that Job. The dashboard Deployment is separate and was already running. Do not apply a manifest whose replica count is 0 over it.

The measurement image must already be loaded as `openwpm-1776:local`. This runbook does not build it.

## Monitor

Auction: the pytest output and the demo's five stage lines.

Crawl: dashboard log panel, `datadir/crawl-status.json`, and `datadir/hb-events.jsonl`. A line with `source: absent` means the page did not expose Prebid. A line with `error_rate` 1.0 means the command threw. That does not stop the rest of the visit list.

Profile table: `GET /api/profiles`. The testing row should show no winner and a non-zero error rate. The training winner is `rubicon`. The baseline winner is `appnexus`. If those change, the fixture adapters changed.

## Incident

If a crawl is hitting a site it should not, Stop crawl in the dashboard. Confirm Job `openwpm-crawl` is gone with `kubectl -n default get job openwpm-crawl`.

If bid files contain unexpected CPMs, treat `hb-events.jsonl` and `results/` as untrusted page data. Do not promote them into a training set until the visit URLs are reviewed.

If the dashboard process is down, the Service `openwpm-1776` has nothing behind it. Restart only the dashboard Deployment. Do not scale the bus listener and do not change `kube-system`.

## Recovery

The auction has no stored state. Re-run the tests.

Crawl state is `datadir/`. Removing `crawl-status.json` only removes the status display. Removing `hb-events.jsonl` removes visit observations. The link list and settings are the other two JSON files in that directory. They are gitignored. Copy them aside before deleting the directory.

Source recovery is `git clone git@github.com:code4johnm/headerbidding.git` and `git clone git@github.com:code4johnm/OpenWPM-1776.git`.
