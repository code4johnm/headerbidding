# Troubleshooting Guide

**HeaderBidding Research Platform**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-04

---

## 1. Common Categories of Failure

1. **Legacy Browser / Driver Issues** (most frequent)
2. **Data Collection / Instrumentation Problems**
3. **HB Bid Harvesting & Coordination Failures** (TrackerProject specific)
4. **Resource Exhaustion & Stability**
5. **Path / Environment Problems** (hardcoded researcher paths)
6. **Data Corruption or Loss**

---

## 2. Legacy Browser & Selenium Issues

### Firefox 52 / geckodriver 0.15 refuses to start

- **Symptom**: `WebDriverException: Message: Process unexpectedly closed`
- **Cause**: Modern kernels, missing display, or library incompatibilities with 2017-era binaries.
- **Mitigation**:
  - Always run inside the provided Docker image on a reasonably compatible host.
  - For bare metal: ensure `xvfb` is installed and the `pyvirtualdisplay` wrapper is used.
  - Accept that some sites will simply not work; do not fight the ancient stack.

### "geckodriver not in PATH"

The install script installs it inside `firefox-bin/geckodriver`. Either:
- Add `firefox-bin` to PATH before launching Python, or
- Explicitly set `webdriver.firefox.driver` / pass the driver location when creating the Selenium instance (requires patching `selenium_firefox.py`).

---

## 3. Instrumentation & Data Problems

### No HTTP / JS / cookie records appearing

Check:
1. The browser actually reached the instrumented state (look for extension load messages in logs).
2. `browser_params` flags were correctly set **before** `TaskManager` instantiation.
3. The `DataAggregator` queue is not blocked (TaskManager will log when it exceeds 10k).
4. Disk space in `data_directory`.

### POST bodies or sensitive JS values missing

- Some captures are intentionally truncated or dropped under load in the old extension.
- Certain HTTPS / HSTS / certificate errors in the ancient browser cause silent channel failures.
- `is_third_party_channel` and `content_policy_type` filtering can hide expected records.

---

## 4. Header Bidding Specific Failures

### "No pbjs bids returned" or empty `output`

- The site does not run Prebid.js (or uses a different name / namespaced version).
- The auction is asynchronous and `getBidResponses()` was called before bids returned.
- Anti-bot / anti-automation measures on the page cleared or never populated `window.pbjs`.
- **Workaround**: Increase `sleep` after `get()`, add retry logic with exponential backoff, or inject mutation observers around the pbjs global.

### Race conditions / lost bid data / duplicate writes

This is **by design** in the current TrackerProject layer. The `writing.json`, `testingDone.json`, and `trainingDone.json` "mutex" files are classic TOCTOU bugs.

**Symptoms**:
- Some variants report far fewer bids than expected.
- `cat` of result files shows truncated or corrupted JSON.
- Multiple browsers writing simultaneously.

**Immediate Mitigation**:
- Run with `NUM_BROWSERS=1` for critical experiments.
- Add `flock` or `fcntl` file locking around all JSON read/write sections (Python `portalocker` or similar).
- Long-term: replace the entire coordination mechanism.

### Hardcoded path errors (`/home/johncook/headerBidding/...`)

The most visible symptom of the research prototype nature of the code.

**Fix pattern** (apply everywhere):

```python
import os
HB_ROOT = os.environ.get("HB_ROOT", "/secure/research/headerbidding")
results_dir = os.path.join(HB_ROOT, "results", experiment_id)
```

Do a full-repo search for the old paths before any production run.

---

## 5. Resource & Stability Issues

### Browser memory usage exceeds 1.5 GB limit

The watchdog in `TaskManager._manager_watchdog` will flag and request restart. Old Firefox + many instruments + long-running tabs = rapid bloat.

**Mitigations**:
- Reduce instruments enabled.
- More frequent browser restarts between sites (add explicit `close` + new `CommandSequence` patterns).
- Run fewer browsers per host.
- Increase `BROWSER_MEMORY_LIMIT` (with caution – increases OOM risk on the host).

### DataAggregator queue growing without bound

TaskManager intentionally blocks command submission when the aggregator is backlogged. This is protective, not a bug. Add more I/O throughput (faster disk, separate volume for SQLite vs Parquet) or reduce instrumentation verbosity.

---

## 6. Debugging Techniques

1. **Increase logging** – Set the MPLogger level lower; tail all files under `log_directory`.
2. **Single-browser, single-site repro** – Reduce to the absolute minimum before adding complexity.
3. **Run with visible browser** (`headless: false`) inside a VNC or noVNC container for interactive debugging (only in Tier 0/1).
4. **Custom instrumentation** – Temporarily add `console.log` wrappers via `run_custom_function` around `pbjs` calls and observe via the extension's logging channel.
5. **Database inspection** – Use `sqlite3` CLI or `pandas.read_sql` on the generated DB to verify records are landing.

---

## 7. Data Quality Red Flags

- Sudden drop in bid yield rate across many sites → possible blocking profile too aggressive or Prebid version change.
- CPM values that are exactly 0 or extremely high (e.g. > $50) for mainstream sites → likely test/debug creatives or data corruption.
- Mismatch between `crawl_history` success and actual HTTP records → navigation failures that were not properly reported.
- Duplicate `visit_id` or negative timestamps → clock skew or aggregator bugs under heavy load.

Always implement automated sanity checks in your analysis pipeline.

---

## 8. When to Give Up and Modernize Instead of Debug

If you are spending more than 30% of your research time fighting Firefox 52, geckodriver 0.15, or the JSON mutex system, stop. The correct fix is the modernization program outlined in the other documents.

Document the failure mode, then contribute a replacement component instead of another workaround.

---

**Still stuck?** Open a detailed issue with:
- Exact command / config used
- Relevant log excerpts (redacted)
- `git rev-parse HEAD`
- Host environment (Docker? kernel version?)
- Which troubleshooting section you already followed

---

## Document Maintenance

This guide should be expanded with every new class of failure encountered in real research runs. It is a living operational artifact.
