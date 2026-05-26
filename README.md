# HeaderBidding Research Platform

**A large-scale web measurement and analysis framework for studying Header Bidding (HB), Real-Time Bidding (RTB), and Prebid.js auction dynamics in the ad-tech ecosystem.**

> **Version**: 0.8.0-hb (research snapshot)  
> **Date**: 2026-04  
> **License**: Mozilla Public License 2.0 (MPL-2.0)  
> **Status**: Research / Academic Use Only – Significant technical debt and security limitations apply.

---

## Security & Responsible Use Warning (Critical)

This platform is a **research instrument** designed for controlled, ethical measurement of web advertising technologies. It:

- Launches instrumented browsers that visit arbitrary web pages.
- Collects highly sensitive telemetry including HTTP requests/responses (with bodies and stack traces), JavaScript API calls, cookies, and detailed real-time bid responses (CPM, bidders, ad units).
- Supports A/B experimentation with custom tracker/ad blocking profiles that can materially affect publisher revenue.

**Before using this software you MUST:**

1. Operate exclusively in isolated environments (dedicated research VMs, hardened containers, or air-gapped networks).
2. Obtain explicit legal and IRB/ethics approval for any data collection involving real user traffic or third-party sites.
3. Implement strict data minimization, retention limits, access controls, and deletion policies for bid landscapes and inferred interest profiles.
4. Never run against production properties or without rate limiting and allow-listing.

**Known Critical Limitations (2026)**

- Firefox 52 ESR (EOL 2018) and geckodriver 0.15 are bundled/expected by install scripts. These contain unpatched vulnerabilities.
- The instrumentation extension uses the long-deprecated Add-on SDK.
- Numerous absolute, researcher-specific paths (`/home/johncook/...`) remain in the TrackerProject layer.
- File-based "mutex" synchronization via JSON files introduces race conditions and data loss risk.

See [docs/Security-and-Privacy.md](docs/Security-and-Privacy.md) for full threat model, hardening requirements, and modernization roadmap.

**Do not use this codebase in its current form for any production, high-volume, or security-sensitive measurement without substantial remediation.**

---

## Overview

HeaderBidding extends the OpenWPM (Open Web Privacy Measurement) framework with specialized tooling for header bidding research:

- **Core Automation (`automation/`)**: Multi-process, instrumented Firefox orchestration with deep HTTP, JavaScript, and cookie telemetry. Supports parallel browsers, command sequencing, SQLite/Parquet/S3 aggregation, and crash-resilient execution.
- **Header Bidding Research Layer (`TrackerProject/`)**:
  - Prebid.js / `pbjs` bid response harvesting (`getBidResponses()`, winning bids, CPM, time-to-respond, bidder participation).
  - Category-based site crawling (Alexa top sites across 17 verticals).
  - A/B testing framework (intent vs. no-intent, tracker blocking profiles using modified uBlock Origin / Disconnect / Ghostery lists).
  - ML pipeline for bid-based user profile generation and interest inference studies.
  - Custom HB logging and result aggregation for revenue/auction dynamics analysis.

The platform enables reproducible studies on:

- Bidder landscape and header bidding adoption across the web.
- Impact of privacy extensions and tracker blocking on eCPM and win rates.
- Potential for cross-site user profiling via observed bid patterns.
- Privacy implications of real-time bidding systems.

---

## Key Features

| Component              | Capability                                                                 |
|------------------------|----------------------------------------------------------------------------|
| Browser Orchestration  | N browsers in parallel processes; synchronized (`**`) or sharded execution |
| HTTP Instrumentation   | Full requests, responses, redirects, POST bodies, referrer, CSP, stack traces |
| JavaScript Instrumentation | Property accesses, method calls, call stacks on sensitive APIs            |
| Cookie Instrumentation | Both profile cookies and `document.cookie` / JS-set cookies                |
| Header Bidding Harvest | Direct `pbjs.getBidResponses()` + winner extraction via injected scripts   |
| Blocking Profiles      | uBlock Origin, Ghostery, Disconnect + custom entity blocklists for A/B     |
| Data Export            | SQLite (primary), Apache Parquet (analytics), S3 support                   |
| ML / Profiling         | Bid collection → feature extraction → synthetic profile generation & training |
| A/B Experimentation    | Intent/volume/category + blocking variants with JSON state coordination    |

---

## Quick Start

### Prerequisites (Legacy Environment)

- Ubuntu 18.04+ (or equivalent)
- Python 2.7 or 3.4–3.6 (hybrid support in original)
- Root/sudo for Firefox + geckodriver installation

**Strongly recommended**: Use the provided Docker images or a modernized fork with current Firefox + Playwright/CDP instrumentation.

```bash
git clone https://github.com/<your-org>/headerbidding.git
cd headerbidding
./install.sh --no-flash   # WARNING: installs ancient Firefox 52 ESR
```

See [docs/Installation-Guide.md](docs/Installation-Guide.md) for development installs, Docker, and macOS variants.

### Minimal Crawl Example (Core OpenWPM)

```python
from automation import CommandSequence, TaskManager

NUM_BROWSERS = 2
sites = ["https://example.com", "https://news.example.com"]

manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

for i in range(NUM_BROWSERS):
    browser_params[i]["http_instrument"] = True
    browser_params[i]["js_instrument"] = True
    browser_params[i]["cookie_instrument"] = True
    browser_params[i]["headless"] = True

manager = TaskManager.TaskManager(manager_params, browser_params)

for site in sites:
    cs = CommandSequence.CommandSequence(site)
    cs.get(sleep=5, timeout=60)
    cs.dump_profile_cookies(120)
    manager.execute_command_sequence(cs, index="**")  # synchronized

manager.close()
```

### Header Bidding Specific Usage

See `TrackerProject/src/crawling/doCrawl.py` and `TrackerProject/src/ScriptUtils/scriptUtils.py` for `pbjs` extraction patterns and the `TrainingCrawl` / A/B orchestration classes.

Example bid extraction JS (injected at runtime):

```js
var responses = pbjs.getBidResponses();
var winners = pbjs.getAllWinningBids();
// ... per-bid record with cpm, bidder, timeToRespond, rendered flag
```

Results are written to structured JSON under researcher-defined `results/bids_{intent|no_intent}/` directories (paths require sanitization before use).

---

## Project Structure

```
headerbidding/
├── automation/                  # OpenWPM core (instrumentation + orchestration)
│   ├── Commands/                # Browser commands (get, dump cookies, custom JS, etc.)
│   ├── DataAggregator/          # Local / S3 / Parquet writers + schema
│   ├── DeployBrowsers/          # Firefox profile, extensions (uBO, Ghostery, etc.), Selenium
│   ├── Extension/firefox/       # Privileged instrumentation extension (HTTP, JS, cookies)
│   ├── TaskManager.py           # Central orchestrator, watchdog, failure handling
│   └── ...
├── TrackerProject/
│   ├── src/
│   │   ├── crawling/            # doCrawl.py, launcher, site selection
│   │   ├── HBLogging/           # HB-specific structured logger
│   │   ├── ScriptUtils/         # getCpm.js, pbjsVersion.js, bid harvesting logic
│   │   ├── ML/                  # Bid collection, profile generation, training
│   │   ├── AB_Testing/          # Site lists (17 IAB categories), training/testing state
│   │   └── config/              # browser_params.json / manager_params.json variants
│   └── ...
├── docs/                        # This professional documentation set
├── demo.py
├── Dockerfile / Dockerfile-dev
├── install.sh / install-dev.sh
├── requirements.txt
├── VERSION
└── README.md                    # This file
```

Full details: [docs/Architecture.md](docs/Architecture.md)

---

## Configuration

See [docs/Configuration.md](docs/Configuration.md) for:

- `manager_params` vs `browser_params`
- Enabling instruments (`http_instrument`, `js_instrument`, `cookie_instrument`)
- Enabling privacy extensions and custom uBlock lists
- Data directory, failure limits, output formats (local vs S3)
- HB-specific A/B and ML configuration patterns

Example hardened browser profile for measurement (research use only):

```json
{
  "http_instrument": true,
  "js_instrument": true,
  "cookie_instrument": true,
  "ublock-origin": true,
  "headless": true,
  "bot_mitigation": true
}
```

---

## Data Model (High-Level)

Primary tables / Parquet datasets produced:

- `site_visits`
- `http_requests`, `http_responses`, `http_redirects` (full headers + POST bodies + `req_call_stack`)
- `javascript` (instrumented property gets/sets/calls + arguments + call stacks)
- `javascript_cookies`, `profile_cookies`
- Custom HB bid JSON files (bidder, cpm, adUnitCode, timeToRespond, rendered)
- Crawl history and configuration snapshots

See [docs/Architecture.md](docs/Architecture.md) for complete schema and data flow diagrams.

---

## Documentation

All documentation lives under `headerbidding/docs/`:

- [Architecture.md](docs/Architecture.md) – System design, Mermaid diagrams, data flows
- [Installation-Guide.md](docs/Installation-Guide.md)
- [Usage-Guide.md](docs/Usage-Guide.md) – HB experiments, A/B testing, ML pipeline
- [Security-and-Privacy.md](docs/Security-and-Privacy.md) – OWASP/NIST alignment, threat model, hardening
- [Configuration.md](docs/Configuration.md)
- [Development.md](docs/Development.md)
- [Deployment.md](docs/Deployment.md)
- [Troubleshooting.md](docs/Troubleshooting.md)

Root-level governance:

- [SECURITY.md](SECURITY.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Contributing & Governance

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/Development.md](docs/Development.md).

All contributions must address the documented security and modernization gaps. PRs that only add features without hardening or tests will be declined.

---

## Acknowledgments

This project is derived from the original [OpenWPM](https://github.com/mozilla/OpenWPM) framework developed by the Princeton University Center for Information Technology Policy (CITP) and Mozilla.

Header bidding extensions were developed for academic research into the privacy, security, and economic properties of real-time advertising auctions.

---

## License

Mozilla Public License 2.0. See [LICENSE](LICENSE) for full text.

---

**Maintained for research transparency and reproducibility. Not intended for operational ad-tech use.**

For questions on responsible use or modernization, open an issue with the `security` or `modernization` label.
