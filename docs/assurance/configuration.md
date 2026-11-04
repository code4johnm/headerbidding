# Configuration

## Auction path

No environment variables are required. There is no API key and no network endpoint.

```bash
python3 -m pip install -r requirements-auction.txt
sh scripts/run-auction.sh
```

`requirements-auction.txt` pins `pytest==9.1.1`. The auction imports only the standard library.

`python3 demo.py` and `python3 demo.py --headless` both run the auction. `--headless` does not start Firefox or Chromium. The flag remains so the older CI demo command does not fail on an unknown argument.

## Crawl path

The OpenWPM conda environment is `environment.yaml`. That file is the pin for the browser stack. It is not required to run the auction tests.

OpenWPM-1776 dashboard settings, saved in `datadir/crawl-settings.json`:

| Field | Values |
| --- | --- |
| `profile` | `training`, `testing`, `baseline` |
| `user_agent` | String. Empty keeps the preset. |
| `viewport` | `WIDTHxHEIGHT`, from 200 to 3840 by 2160 |
| `geolocation` | IANA timezone name stored on the browser as `timezone_id`. `UTC` is allowed. |
| `cookie_state` | `empty` or `blocked` sets `tp_cookies` to `never`. `preserved` sets `always`. |
| `consent` | `reject`, `accept`, or `absent`. Reject and accept try to click a matching banner button. Absent does not. |
| `inject_script` | Page script, at most 2000 characters. The testing preset sets `window.__hbAdversarial`. |
| `fingerprint_resistance` | Stored as a browser pref. The testing preset turns it on. |

The crawl Job still refuses callstack instrumentation. Do not turn that instrument on in this tree.

## Secrets

Do not put tokens, account passwords, or publisher credentials in this repository. The auction path has nowhere to read them. GitHub Actions secrets are the place for any future CI credential. None are required for the auction workflow.
