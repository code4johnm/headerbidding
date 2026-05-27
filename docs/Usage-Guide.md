# Usage Guide

**HeaderBidding Research Platform – Conducting Header Bidding & RTB Measurements**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-05-27T02:47:30Z

**Prerequisites**: Read [Security-and-Privacy.md](docs/Security-and-Privacy.md) and complete the Phase 0 containment steps in [Installation-Guide.md](docs/Installation-Guide.md) before running any experiment.

---

## 1. Core Concepts

### 1.1 Two Layers

1. **OpenWPM Core** – General purpose instrumented crawling (`automation/`).
2. **HB Research Layer** – Prebid.js extraction, A/B blocking experiments, ML profiling (`TrackerProject/src/`).

Most serious research uses the HB layer on top of the core.

### 1.2 CommandSequence (Core Primitive)

A declarative script of actions executed inside one browser visit:

```python
from automation import CommandSequence

cs = CommandSequence.CommandSequence("https://example.com")
cs.get(sleep=5, timeout=90)                    # Navigate + wait
cs.dump_profile_cookies(120)                   # Persist cookies to DB
cs.run_custom_function(my_hb_extractor, ...)   # Custom JS or Python
```

`index='**'` on `execute_command_sequence` runs the same sequence synchronously across all browsers (useful for A/B).

### 1.3 Instruments (Data Collection Knobs)

Controlled per-browser via `browser_params`:

- `http_instrument`: Full request/response/redirect + headers + POST bodies + stack traces.
- `js_instrument`: Sensitive JS property accesses and method calls (fingerprinting surface, tracking calls).
- `cookie_instrument`: Both `document.cookie` changes and profile cookie dumps.
- `save_javascript` / `save_all_content`: Heavy – use sparingly.

**Security Note**: Enabling all instruments on high-traffic sites generates enormous volumes of sensitive data very quickly.

---

## 2. Basic OpenWPM Crawl (Foundation)

See `demo.py` and the example in README.md.

---

## 3. Header Bidding Specific Workflows

### 3.1 Bid Harvesting with ScriptUtils

The key abstraction lives in `TrackerProject/src/ScriptUtils/scriptUtils.py`:

```python
from ScriptUtils.scriptUtils import ScriptUtils

pbjs = ScriptUtils()
# Inside a CommandSequence or via run_custom_function:
output = driver.execute_script(pbjs.GET_CPM)   # returns list of bid dicts
```

Each record includes:
- `bidder`, `cpm`, `timeToRespond`, `adUnitCode`, `statusMessage`, `rendered` (winner flag)

Results are aggregated into timestamped JSON files under researcher-defined `results/bids_*` directories.

### 3.2 A/B Testing Framework (High-Level)

The `TrainingCrawl` class (`doCrawl.py`) orchestrates:

- Loading category site lists from `AB_Testing/sites/` or `config/training/sites/`.
- Spawning multiple browser "personas" with different blocking profiles (`ublock-origin`, custom lists in extension storage).
- Intent vs No-Intent site subsets.
- Coordination via `trainingDone.json` / `testingDone.json` (fragile – see limitations).

**Typical Experiment Matrix**:

| Variant | Intent | Block Profile | Purpose |
|---------|--------|---------------|---------|
| A1 | NO_INTENT | none | Baseline HB auction |
| A2 | NO_INTENT | alphabet-all | Impact of major tracker block |
| B1 | INTENT | none | Intent-driven bidding lift |
| B2 | INTENT | pubmatic-some | Selective supply-side blocking |

### 3.3 ML Pipeline Usage

Located under `TrackerProject/src/ML/dataCollection/`:

1. `bid_collection/ml_testing.py` – Harvest bids at scale for training/testing split.
2. `profile_generation/generate_profiles.py` – Create synthetic or derived interest profiles from observed bid patterns.
3. `profile_training/ml_training.py` – Train models that predict category / intent from bid features.
4. `processing/ml_analysis.py` – Post-experiment statistical analysis.

**Critical**: These scripts contain many hardcoded paths and were written for a single researcher's environment. They must be refactored before reuse.

---

## 4. Recommended Safe Experiment Lifecycle

1. **Design** – Write a one-page experiment protocol (research question, variants, success metrics, data retention plan).
2. **Containment** – Launch inside hardened Docker with dedicated results volume.
3. **Small Pilot** – 5–10 sites, 1 browser, minimal instruments. Validate data quality and path sanitization.
4. **Full Run** – With monitoring (memory, disk, anomalous CPM spikes).
5. **Export & Redaction** – Apply PII scrubbing + aggregation before any analysis workstation transfer.
6. **Analysis** – Use Parquet exports + pandas / DuckDB. Never work directly on raw `crawl-data.sqlite` for large studies.
7. **Publication** – Release only aggregated statistics or heavily redacted datasets + methodology + DPIA summary.
8. **Deletion** – Enforce retention policy; cryptographically shred raw records.

---

## 5. Monitoring & Observability During Runs

- Tail the per-browser logs under `log_directory`.
- Watch `DataAggregator` queue depth (TaskManager blocks when > 10k records).
- Use `psutil` / `htop` inside the container for memory pressure (old Firefox is leaky).
- Implement custom alerts on `HBLogger` for "no bids returned" rate or extreme CPM outliers (possible data corruption or site cloaking).

---

## 6. Common Usage Patterns & Gotchas

- **Synchronized vs Independent Browsers**: Use `index='**'` when you need identical timing for A/B fairness. Use sharded assignment for throughput.
- **Profile Persistence**: `profile_archive_dir` + `profile_tar` allow warm browser profiles (cookies, localStorage) across restarts – powerful for longitudinal studies but dangerous for privacy (carry-over contamination).
- **Bot Mitigation**: `browser_params[i]['bot_mitigation'] = True` enables basic human-like scrolling / timing. Insufficient against modern bot detection.
- **Custom JS Injection**: Prefer `run_custom_function` + `execute_script` over modifying the instrumentation extension when possible.

---

## 7. Limitations & Anti-Patterns to Avoid

- Do **not** rely on the JSON mutex files (`testingDone.json`, `writing.json`) for anything important – they are racy and lossy.
- Do **not** enable every instrument "just in case".
- Do **not** run against the top 1M without a robust allow-list and egress proxy.
- Do **not** treat inferred profiles as ground truth without validation against consent-based data.
- Do **not** keep raw bid + cookie datasets longer than the experiment protocol allows.

See [Troubleshooting.md](docs/Troubleshooting.md) for runtime errors and [Development.md](docs/Development.md) for how to improve the platform.

---

**Next**: [Configuration.md](docs/Configuration.md) for detailed parameter reference.
