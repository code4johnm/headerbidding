# Development Guide

**HeaderBidding Research Platform**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-05-27T15:30:00Z

**Goal**: Improve the platform toward modern, secure, reproducible research tooling while preserving the unique header bidding measurement capabilities.

---

## 1. Development Philosophy

1. **Security First** – Every change must be evaluated against the threat model in [Security-and-Privacy.md](docs/Security-and-Privacy.md).
2. **Honesty About Debt** – Do not paper over the fact that the browser stack is ancient. Modernization is the primary technical goal.
3. **Reproducibility** – Experiments must be fully defined in code + config + site lists + random seeds (where applicable).
4. **Data Minimization** – Default to collecting less, not more.

---

## 2. Project Layout for Contributors

```
automation/          # Treat as a library; minimize changes here if possible
TrackerProject/src/  # The research-specific layer – this is where most HB work happens
docs/                # All professional documentation (you are here)
```

Avoid putting new logic in the root except for demos and orchestration entrypoints.

---

## 3. Setting Up a Development Environment

1. Follow [Installation-Guide.md](docs/Installation-Guide.md) inside a dedicated VM or container.
2. Install dev tools:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install   # if you add a config
   ```
3. **Critical First Task**: Create `config/local.env` (gitignored) and a path abstraction module that replaces all hardcoded `~/headerBidding` strings.

---

## 4. Coding Standards

- Python 3 only for new code (drop Python 2 compatibility).
- Use `black`, `isort`, `flake8` (existing `setup.cfg` targets).
- Add type hints on all new public functions (`from __future__ import annotations`).
- Every new experiment script must have a corresponding small test that runs in headless mode against `example.com` or a fixture.
- All paths must come from configuration, never be hardcoded.

**Commit Message Convention** (example):

```
feat(hb): add pydantic experiment config model

- Replaces ad-hoc JSON mutex files for state
- Includes validation and path sanitization
- Refs: #42 (modernization epic)
```

---

## 5. Testing Strategy

Current state: Very few automated tests for the HB layer.

**Minimum New Standard**:
- Unit tests for pure functions (bid parsing, profile feature extraction).
- Integration tests that launch 1 headless browser, visit a known site with synthetic Prebid, and assert bid records are captured.
- Property-based or fuzz tests on site list loading and command sequences.

Use `pytest` + the existing test infrastructure in `automation/`.

---

## 6. Modernization Priorities (Ranked)

1. **Path Abstraction & Config Centralization** (highest leverage, lowest risk).
2. **Replace JSON file coordination** with Redis/Postgres task queue + proper state machine.
3. **Browser Stack Upgrade** (largest effort): move instrumentation to Playwright + CDP or current Firefox + WebExtension + BiDi.
4. **Data Protection Layer**: PII redaction pipeline, field-level encryption helpers, Parquet encryption.
5. **Observability**: OpenTelemetry instrumentation for crawl progress, queue depths, bid yield rates.
6. **Packaging**: Proper `pyproject.toml`, console scripts for `hb-crawl`, `hb-analyze`.
7. **CI/CD**: GitHub Actions with container image builds, Trivy scanning, and smoke tests (even against legacy stack initially).

---

## 7. Working with the Instrumentation Extension

The Firefox extension in `automation/Extension/firefox/` is the most powerful (and dangerous) data collection component. Changes here require:

- Deep understanding of legacy Add-on SDK + XPCOM.
- Manual testing inside the old Firefox (very painful).
- Strong justification – most new measurement needs should be prototyped via `run_custom_function` + page `execute_script` first.

Long-term: this extension should be retired in favor of trusted browser automation protocols.

---

## 8. Documentation Requirements

Any PR that adds or changes user-facing behavior **must** update the relevant file in `docs/`.

- New instrument flag → Configuration.md
- New HB experiment pattern → Usage-Guide.md + Architecture.md
- Security-relevant change → Security-and-Privacy.md

---

## 9. Contribution Process

1. Open an issue with label `modernization`, `hb-experiment`, `security`, or `bug`.
2. For large changes, write a short design note (1–2 pages) and link it.
3. Ensure all new code passes linting and the smoke test suite.
4. Update this Development Guide if you introduce new workflows or tooling.

**Do not submit** purely additive features that increase attack surface or data collection without corresponding hardening or tests.

---

## 10. Useful Debugging Techniques

- `KEEPOPEN=1 python ...` style patterns (adapt from old OpenWPM test helpers) to keep the browser alive after a command sequence.
- Enable verbose Selenium + geckodriver logging.
- Use `browser_params[i]['prefs']` to set `devtools.debugger.remote-enabled` etc. for manual inspection (inside isolated env only).
- For HB bid debugging: inject a console.log wrapper around `pbjs.getBidResponses` and watch the browser console via the extension logging.

---

**See also**: [Deployment.md](docs/Deployment.md) for how research runs should be executed in production-like environments.
