# Configuration Reference

**headerbidding: Header Bidding Research Platform**  
**Version**: 1.4.0  
**Date**: 2026-05-27T20:00:00Z  
**Full Path**: `docs/Configuration.md`

This document is the authoritative reference for `ManagerParams` and `BrowserParams`. It supersedes older dictionary-based usage.

---

## 1. Modern Configuration Model

The platform uses strongly typed dataclasses (defined in `openwpm/config.py`) with validation and JSON serialization support via `dataclasses_json`.

```python
from openwpm.config import ManagerParams, BrowserParams
from pathlib import Path

manager_params = ManagerParams(
    num_browsers=4,
    data_directory=Path("./datadir/"),
    log_path=Path("./datadir/openwpm.log"),
)

browser_params = [
    BrowserParams(
        http_instrument=True,
        js_instrument=True,
        cookie_instrument=True,
        # ... see full options below
    )
    for _ in range(4)
]
```

Legacy dictionary style (`TaskManager.load_default_params`) is deprecated and will be removed.

---

## 2. ManagerParams (Platform-Wide)

| Field | Type | Default | Description | Security Implication |
|-------|------|---------|-------------|----------------------|
| `num_browsers` | int | 1 | Number of parallel browser processes | Higher = larger blast radius; enforce via capability token |
| `data_directory` | Path | `datadir/` | Root for all telemetry, logs, profiles | Must be on encrypted volume; contains high-sensitivity data |
| `log_path` | Optional[Path] | None | MPLogger output | Separate from telemetry for tamper detection |
| `failure_limit` | int | 2 | Consecutive browser failures before abort | Prevents infinite crash loops from malicious sites |
| `run_id` | Optional[str] | None | Experiment identifier | Used for correlation in audit logs |
| `storage_controller` | str | "local" | "local" \| "s3" \| "gcp" | Cloud providers require credential isolation (IAM roles, not long-lived keys in env) |

**Hardening Recommendation**: Always set an explicit `data_directory` under a project-specific encrypted mount. Never use `~` or `/tmp`.

---

## 3. BrowserParams (Per-Browser)

### 3.1 Instrumentation Flags

| Flag | Default | Risk Level | Notes |
|------|---------|------------|-------|
| `http_instrument` | False | High | Captures full request/response bodies and headers |
| `js_instrument` | False | High | Enables deep property access logging (see settings below) |
| `cookie_instrument` | True | High | Both JS-set and profile cookies |
| `navigation_instrument` | False | Medium | Navigation events + redirects |
| `dns_instrument` | False | Medium | DNS lookups performed by browser |
| `callstack_instrument` | False | High | Currently broken (see AGENTS.md); when fixed will increase stack sensitivity |
| `save_content` | False | Critical | Saves full response bodies to disk/LevelDB. **Disable by default** |

### 3.2 JavaScript Instrumentation Settings

`js_instrument_settings`: `List[Union[str, dict]]`

Predefined collections (recommended):
- `"collection_fingerprinting"` – Standard battery of known fingerprinting APIs (canvas, WebGL, AudioContext, fonts, etc.)

Custom example:
```python
{
    "collection_name": "my_hb_experiment",
    "log_settings": {
        "properties_to_instrument": ["navigator.userAgent", "window.screen"],
        "recursive": False,
        "recursion_depth": 1
    }
}
```

Full schema: `schemas/js_instrument_settings.schema.json` and generated docs under `docs/schemas/`.

**Security Note**: Deeper instrumentation increases both research value and the volume of potentially re-identifying data collected.

### 3.3 Display & Profile Handling

- `display_mode`: `"native" | "headless" | "xvfb"`
- `bot_mitigation`: bool – Enables basic anti-detection (recommended for realistic HB auction observation)
- `seed_tar`: Optional[Path] – Pre-populated profile tarball (for consistent cookies / localStorage)
- `profile_archive_dir`: Optional[Path] – Where to save completed profiles (high sensitivity)

### 3.4 Privacy & Blocking Extensions

The modern profile system supports loading uBlock Origin, Ghostery, Disconnect, and custom lists via the `prefs` mechanism and extension loading in `deploy_browsers/configure_firefox.py`.

Example hardened profile for A/B studies:
```python
browser_params[0].prefs = {
    "network.cookie.cookieBehavior": 1,  # block third-party
    # additional hardening prefs...
}
```

See `TrackerProject` configuration examples for legacy blocking profile patterns.

---

## 4. Header Bidding Specific Configuration

HB experiments are primarily driven through custom command sequences and the legacy `TrackerProject/src/config/` JSON files.

Key patterns:
- A/B variant encoded in `intent` vs `no_intent` site batches
- Custom block lists injected per variant
- Bid harvesting performed via `run_custom_function` + `ScriptUtils`

**Recommendation**: Migrate HB orchestration into a new `openwpm/hb/` module that consumes the same typed `BrowserParams` and emits capability manifests.

---

## 5. Storage Backend Configuration

Storage is configured at the `TaskManager` / `StorageController` level (see `openwpm/storage/`).

Local Parquet + SQLite is the default and recommended starting point for new studies.

Cloud backends require explicit credential handling via environment variables or instance roles — never embed keys in code or Dockerfiles.

---

## 6. Validation & Error Handling

All parameters are validated at `TaskManager` construction time. Invalid values raise `ConfigError` with a pointer to this document.

Example error:
```
ConfigError: Found invalid value `foo` for display_mode in BrowserParams. Supported values are ['native', 'headless', 'xvfb']...
```

---

## 7. Configuration Security Checklist

- [ ] Explicit allow-list of domains passed to TaskManager (future enforcement point)
- [ ] `save_content` disabled unless a specific DPIA justifies full body retention
- [ ] `js_instrument_settings` limited to the minimal collection required for the research question
- [ ] `data_directory` on encrypted filesystem with strict permissions (0700)
- [ ] Per-experiment `run_id` for audit correlation
- [ ] No secrets or researcher home paths in any config file committed to git

**Full path of authoritative config implementation**: `openwpm/config.py`

---

*Configuration must be treated as part of the security boundary. Incorrect instrumentation settings can dramatically increase data sensitivity and regulatory exposure.*
