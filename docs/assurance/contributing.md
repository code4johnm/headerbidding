# Contributor guide

Ownership of the maintained tree is `@code4johnm`, recorded in `CODEOWNERS`.

Work from `/mnt/5TB/git/github/headerbidding`. The remote is `git@github.com:code4johnm/headerbidding.git`. The branch is `master`.

Before a change to the auction:

```bash
python3 -m pip install -r requirements-auction.txt
python3 -m pytest test/test_hb_auction.py test/test_script_utils_bids.py -q
python3 demo.py
```

The browser suite under `test/` imports OpenWPM inside fixtures. Collecting the auction tests does not import `dataclasses_json`. Running a browser test still needs the conda environment and Firefox.

Do not commit `datadir/`, crawl databases, `results/` bid dumps, or `docs/PROJECT.md` stubs. Do not commit cookies or browser profiles.

The older checkout at `/mnt/5TB/git/headerbidding` tracks `https://github.com/jmcook1982/headerbidding.git`. It is a different history. Do not force it onto `code4johnm/headerbidding`.

OpenWPM-1776 integration tests:

```bash
cd /mnt/5TB/git/github/OpenWPM-1776
python3 -m pytest test_header_bidding.py -q
```

That test needs `dataclasses-json==0.6.7`, which `environment.yaml` already pins for the browser stack.
