# Control mapping

Mapped to NIST SP 800-53 revision 5 families named in the recovery task. "In place" means the repository does this today. "Gap" means it does not, and this file does not pretend otherwise. SSDF practices are called out under the family they support.

## AC — access control

In place: `CODEOWNERS` names `@code4johnm`. The GitHub repository is private.

Gap: the auction and the OpenWPM dashboard have no user login. Anyone who can open the host port can read the dashboard. That is a host-network control, not an application control.

## AU — audit and accountability

In place: auction events record request, each adapter response, clearing, win notice, and impression. `HeaderBiddingCommand` appends a JSON line per visit with latency, error, consent result, and profile name. OpenWPM writes `openwpm.log` for a crawl.

Gap: there is no remote log collector and no tamper-evident store.

## CM — configuration management

In place: git history, `requirements-auction.txt` for the auction tests, `environment.yaml` for the browser stack, and dashboard settings written as JSON. The auction workflow runs the critical-path tests on push and pull request.

Gap: the full browser suite is not part of that small workflow. A green auction check does not mean Firefox tests passed.

## IA — identification and authentication

In place: pushes use the `code4johnm` GitHub identity over SSH.

Gap: no application identity. Crawl jobs use the cluster service account that already existed for the dashboard.

## SA — system and services acquisition

SSDF: requirements are the auction stages and the profile categories. Design notes are in `architecture.md`. Defaults are first-price, headless crawl, callstack off, and no network in the auction.

In place: third-party versions for the auction test runner and the conda stack are pinned. The SBOM lists the auction component and the test runner.

Gap: the conda stack is large. This mapping does not review every package.

## SC — system and communications protection

In place: the auction does not open connections. Win and impression URLs are data. Crawl links must be `http` or `https` and cannot carry a username or password.

Gap: a crawl speaks to whatever host is on the link list. TLS validation is the browser's.

## SI — system and information integrity

SSDF verify: `test/test_hb_auction.py`, `test/test_script_utils_bids.py`, and OpenWPM-1776 `test_header_bidding.py`. The harvest writer no longer uses `json.dump(..., indent=True)`, which raised and discarded bids.

Gap: no static-analysis job is wired to the auction workflow. CodeQL remains on the older browser workflow. Vulnerability handling is `disclosure.md`. There is no external coordination center and no claim of a CISA binding operational directive.
