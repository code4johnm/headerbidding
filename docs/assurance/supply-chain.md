# Supply chain

CISA's guidance on third-party components asks operators to know what they ship, pin it, and separate runtime from development tools. This page is that inventory for the auction path. It is not a supplier assessment.

## Runtime of the auction

The module `hb/auction.py` imports the Python standard library only. A compromised PyPI package cannot enter that process unless a later change adds an import.

## Test and CI

`requirements-auction.txt` pins `pytest==9.1.1`. The GitHub Actions workflow `Auction` installs that file on `ubuntu-latest` with Python 3.12 from `actions/setup-python@v5` and `actions/checkout@v4`. Those actions are third-party code. Review updates before changing the major version.

## Browser stack

`environment.yaml` pins the conda packages used by a crawl, including `dataclasses-json==0.6.7` from pip. That stack is what launches Chromium or Firefox and parses pages. Treat an update there as a measurement change, not as a formatting change. The auction tests do not install it.

## OpenWPM-1776

The crawl image and the dashboard are separate. The dashboard process is `python:3.12-alpine` and imports `openwpm.header_bidding` from the mounted source tree. The measurement image is `openwpm-1776:local` and is not pulled from a registry (`imagePullPolicy: Never`). If that image is missing, the crawl Job does not start. The dashboard can still export fixture rows.

## What is not a dependency

Prebid.js is not vendored. On a crawl it is whatever the page loaded. Bidder endpoints are not called by this repository.
