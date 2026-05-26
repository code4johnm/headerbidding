# Configuration Reference

**HeaderBidding Research Platform**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-04

This document describes all configuration surfaces. **Default values are often unsafe for modern research use.**

---

## 1. Two Configuration Dictionaries

OpenWPM uses two separate dictionaries:

- **`manager_params`** – Crawl-wide (data directories, failure limits, output format, number of browsers).
- **`browser_params`** – Per-browser (instruments enabled, privacy extensions, profile behavior, headless, etc.). Passed as a list of length `num_browsers`.

Load defaults:

```python
from automation import TaskManager

manager_params, browser_params = TaskManager.load_default_params(num_browsers=3)
```

Files that define the shipped defaults:

- `automation/default_manager_params.json`
- `automation/default_browser_params.json`

TrackerProject overrides live in:

- `TrackerProject/src/config/training/{browser,manager}_params.json`
- `TrackerProject/src/config/testing/owpm_config/` and `pbjs_config/`

---

## 2. manager_params Reference

| Key | Type | Default | Security/Privacy Implication | Recommendation |
|-----|------|---------|------------------------------|----------------|
| `data_directory` | str | `~/openwpm/` | Root of all raw telemetry | Use absolute path under dedicated volume with 700 perms |
| `log_directory` | str | `~/openwpm/` | Centralized logs | Same as above; rotate aggressively |
| `output_format` | "local" \| "s3" | "local" | S3 requires long-lived creds in many legacy paths | Prefer local + manual sync; use short-lived assumed roles if S3 |
| `database_name` | str | `crawl-data.sqlite` | Primary structured output | Include experiment ID in name |
| `log_file` | str | `openwpm.log` | Aggregated structured logs | |
| `failure_limit` | int \| null | null (derived) | Too low = early termination on flaky sites; too high = runaway | Set explicitly (e.g. `num_browsers * 3`) |
| `testing` | bool | false | Disables some production guards | Never true in research runs |
| `num_browsers` | int | 1 | Resource & parallelism control | Start with 1–2; monitor memory |

**S3-specific** (when `output_format == "s3"`): additional keys for bucket, prefix, credentials (insecure in current code – externalize).

---

## 3. browser_params Reference (Per-Browser)

### 3.1 Instrumentation Flags (Highest Data Sensitivity)

| Key | Default | Effect | Risk Level |
|-----|---------|--------|------------|
| `http_instrument` | false | Captures every HTTP request/response + full headers + `post_body` + `req_call_stack` | **Critical** – POST bodies can contain auth tokens, PII |
| `js_instrument` | false | Instruments property gets/sets and method calls on sensitive objects | High – fingerprinting surface, tracking pixels, canvas, etc. |
| `cookie_instrument` | false | Logs `document.cookie` mutations and profile cookie dumps | High |
| `save_javascript` | false | Persists de-duplicated JS files | Medium |
| `save_all_content` | false | Saves full page content | High – can contain personal data |

**Strong recommendation**: Enable instruments one at a time during pilot experiments. Justify each in your research protocol.

### 3.2 Privacy Extension & Blocking Controls

| Key | Default | Effect |
|-----|---------|--------|
| `ublock-origin` | false | Loads bundled uBlock Origin 1.14 |
| `ghostery` | false | Loads Ghostery 7.3 |
| `disconnect` | false | Loads Disconnect |
| `https-everywhere` | false | Loads HTTPS Everywhere (2017 snapshot) |
| `tracking-protection` | false | Firefox tracking protection |
| `donottrack` | false | Sends DNT: 1 |

**Important**: TrackerProject experiments heavily customize these via modified `storage.js` files inside the extension directories. These custom block lists target specific ad entities (alphabet, pubmatic, etc.).

### 3.3 Browser Behavior & Fingerprinting Surface

| Key | Default | Notes |
|-----|---------|-------|
| `headless` | false | Headless Firefox is more fingerprintable in old versions |
| `bot_mitigation` | false | Basic human-like scrolling & timing (weak) |
| `disable_flash` | true | Good default |
| `controlled_scroll` | true | |
| `random_attributes` | false | Randomizes some attributes (anti-fingerprinting attempt) |
| `prefs` | {} | Arbitrary Firefox preferences – powerful but dangerous |

### 3.4 Profile Handling (Longitudinal Studies)

| Key | Purpose | Privacy Warning |
|-----|---------|-----------------|
| `profile_tar` | Load a pre-existing profile tarball | Can carry over real user cookies / logins |
| `profile_archive_dir` | Directory to save/load profiles between crawls | Enables stateful "personas" but creates massive privacy contamination risk if not cleaned |

**Never** reuse production browser profiles for measurement.

---

## 4. Header Bidding Layer Configuration

The HB layer does **not** use a single clean config file. It relies on:

- Command-line-ish arguments parsed in `doCrawl.py` (`--volume`, `--intent`, `--category`, `--trackers_blocked`, `--training_type`).
- Hardcoded paths inside `ScriptUtils/scriptUtils.py` and ML scripts.
- JSON state files (`trainingDone.json`, `testingDone.json`, `no_bid_sites.json`).

**Refactoring Required** (see Development & Security docs):
- Central `experiment.yaml` or `pydantic` model.
- Environment variable or config file for all result paths.
- Proper experiment registry instead of ad-hoc JSON.

---

## 5. Example Hardened Research Configuration

```python
manager_params, browser_params = TaskManager.load_default_params(2)

manager_params.update({
    "data_directory": "/secure/research/2026-hb-study-042/experiment-07",
    "log_directory": "/secure/research/2026-hb-study-042/logs",
    "database_name": "hb-crawl-exp07.sqlite",
    "failure_limit": 12,
    "num_browsers": 2,
})

for i in range(2):
    bp = browser_params[i]
    bp.update({
        "http_instrument": True,
        "js_instrument": True,
        "cookie_instrument": True,
        "ublock-origin": True,           # or a custom variant
        "headless": True,
        "bot_mitigation": True,
        "disable_flash": True,
        "save_all_content": False,       # explicitly disabled
        "post_body_capture": False,      # if such a knob existed / patch required
    })
```

---

## 6. Configuration Validation & Secrets

Current codebase performs almost no validation. Add your own:

- Schema validation (Pydantic or `jsonschema`).
- Reject any config containing obvious secrets or personal paths.
- Fail fast if `data_directory` is world-readable.

---

## 7. Related Files

- `automation/default_*.json`
- `TrackerProject/src/config/`
- `TrackerProject/src/AB_Testing/sites/*.json` (site lists)
- Extension `storage.js` files (custom block rules)

---

**Next**: [Development.md](docs/Development.md) for contributing improvements and modernization work.
