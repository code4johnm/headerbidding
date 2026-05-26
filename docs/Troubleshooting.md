# Troubleshooting Guide

**headerbidding: Header Bidding Research Platform**  
**Version**: 1.1.0  
**Date**: 2026-04-26  
**Full Path**: `docs/Troubleshooting.md`

---

## 1. Quick Diagnostic Commands

```bash
# Verify modern environment is active
conda activate openwpm
python -c "import openwpm; print(openwpm.__file__); import openwpm.config as c; print(c.__file__)"

# Run a minimal headless diagnostic
python demo.py --headless 2>&1 | tail -30

# Extension build health
cd Extension && npm run lint && npm run build

# Full pre-commit health
pre-commit run --all-files
```

---

## 2. Common Failure Categories & Remedies

### 2.1 Browser Launch / Selenium Failures

**Symptoms**: `WebDriverException`, geckodriver crashes, "connection refused" on Marionette port.

**Likely Causes**:
- Firefox binary not found or wrong architecture
- Profile directory permission or corruption issues
- Missing X server / xvfb when using `native` or `xvfb` display modes

**Remedies**:
```bash
# Re-run install targeting current layout
./install.sh --skip-create   # after fixing environment.yaml

# Force clean profile creation (modern path)
rm -rf datadir/profile_*

# Use xvfb-run wrapper on servers
xvfb-run -a python your_crawl.py
```

**Known Issue**: Legacy Dockerfiles and `install.sh` still contain references to old Firefox 52 ESR paths in some branches. Update to current Firefox + geckodriver.

### 2.2 Extension Socket / IPC Failures

**Symptoms**: Timeouts waiting for extension, "socket closed unexpectedly", no telemetry arriving in storage.

**Remedies**:
- Confirm the extension was rebuilt after any source change: `./scripts/build-extension.sh`
- Check for port conflicts on localhost sockets used by the privileged `sockets` experiment API.
- Inspect browser console logs (enable `browser_params[*].prefs["devtools.console.stdout.content"] = true` temporarily).
- Verify the binary protocol (length-prefixed) is not being interfered with by corporate proxies or antivirus.

### 2.3 JavaScript Instrumentation Problems

**Known Broken**: `callstack_instrument` currently raises `ConfigError` (see AGENTS.md and upstream #557).

**High Data Volume**: Very deep `js_instrument_settings` with high recursion can produce millions of records per site. Use the predefined `"collection_fingerprinting"` collection unless you have a specific narrow research question.

**Remedy for noisy instrumentation**:
```python
browser_params[0].js_instrument_settings = ["collection_fingerprinting"]
# Avoid custom recursive: True on broad objects
```

### 2.4 Legacy TrackerProject / HB Layer Issues

**Hardcoded Paths** (`/home/johncook/...` etc.):
- Search and replace all absolute paths with configurable values or `Path(__file__).parent` patterns.
- The files are listed in the earlier analysis scan.

**JSON Mutex Races** (`testingDone.json`, `writing.json`):
- These are known design flaws. Do not rely on them for new experiments.
- Migrate coordination into the modern TaskManager command model or a proper database/Redis backend.

**ML / Bid Collection Failures**:
- Often caused by changes in Prebid.js public API. Update the string-concat JS in `ScriptUtils` and re-validate against current Prebid versions on test pages.

### 2.5 Storage & Data Problems

- **Parquet / Arrow schema drift**: The two schema definitions (`parquet_schema.py` and `schema.sql`) must be kept in sync manually. Run the storage tests (`pytest test/storage/`) after any schema change.
- **Disk full**: Browser profiles + LevelDB + Parquet can grow extremely fast when `save_content` or deep JS instrumentation is enabled. Monitor with `du -sh datadir/`.

### 2.6 CI / Test Flakiness

- Tests are split into 7 groups because full browser instrumentation is slow and resource heavy.
- Use `-m "not slow"` for faster local iteration.
- xvfb is required in headless CI environments (already configured in `run-tests.yaml`).

---

## 3. Debugging the Privileged Extension

1. `cd Extension && web-ext run --verbose` (for manual inspection).
2. Enable `browser console` logging via Firefox prefs in the profile.
3. Use the `stackDump` and `profileDirIO` privileged APIs only through the provided wrappers—direct calls from content scripts are blocked by design.

---

## 4. When to Open an Issue

Include in every bug report:
- Exact git commit / tag
- `python --version` and `conda env export`
- Full `ManagerParams` / `BrowserParams` (redacted of secrets)
- Last 100 lines of the MPLogger output + any browser console errors
- Whether the run used the modern `openwpm.*` API or legacy `automation` / TrackerProject paths

Label security-related reports per [docs/SECURITY.md](docs/SECURITY.md).

---

## 5. Recovery Procedures

**Corrupted environment**:
```bash
conda deactivate
rm -rf $CONDA_PATH/envs/openwpm
./install.sh
```

**Suspected data integrity issue**:
- Stop all crawls
- Preserve the `datadir/` (tar + checksum)
- Wipe profiles and restart with fresh seed if needed
- Compare Parquet row counts against command log

---

**Most problems are caused by mixing legacy and modern code paths or by insufficient disk / memory for the configured instrumentation level.**

*Full path*: `docs/Troubleshooting.md`
