# headerbidding: Header Bidding Research Platform

**Modernized OpenWPM-based framework for large-scale, ethical measurement of Header Bidding (HB), Real-Time Bidding (RTB), and Prebid.js auction dynamics.**

> **Documentation Set**: See the full [Documentation Set](#documentation-set) table below, including the complete index of all project documentation.



> **Version**: 1.4.0-hb (research snapshot)  
> **Last Updated**: 2026-05-27T20:00:00Z  
> **License**: Mozilla Public License 2.0 (MPL-2.0)  
> **Primary Standards Alignment**: OWASP Top 10 (2021), OWASP ASVS 4.0, NIST Cybersecurity Framework, ISO 27001 principles, Secure SDLC (SSDL), Zero Trust research workload practices.

---

## Critical Security & Responsible Use Warning

**This is a high-privilege research measurement platform, not a general-purpose tool or production system.**

The platform:

- Launches instrumented browsers that fetch and execute arbitrary third-party web content.
- Captures highly sensitive telemetry: full HTTP requests/responses (including bodies and referrers), detailed JavaScript property accesses and call stacks on sensitive APIs, cookies, DNS, navigation events, and real-time bidding telemetry (bidder participation, CPM values, ad unit dynamics capable of enabling cross-site interest profiling).
- Executes researcher-supplied JavaScript in page context and privileged browser chrome via a custom WebExtension with broad `<all_urls>` permissions and custom privileged experiment APIs (`sockets`, `profileDirIO`, `stackDump`).
- Supports A/B experimentation that can alter observed auction outcomes and publisher revenue signals.

**Mandatory Prerequisites (Non-Negotiable)**

Before any execution:

1. Obtain formal IRB/ethics board approval and legal review for the specific data collection and retention plan.
2. Deploy exclusively in isolated, hardened research environments (dedicated VMs, Kubernetes namespaces with NetworkPolicy, or air-gapped clusters). Never on multi-tenant or production-adjacent infrastructure.
3. Implement a Data Protection Impact Assessment (DPIA) and data classification scheme for all collected bid landscapes and derived profiles.
4. Enforce strict destination allow-lists, rate limiting, and crawl politeness policies. Never crawl production properties without explicit authorization.
5. Apply the hardening controls documented in [docs/Security-Hardening.md](docs/Security-Hardening.md) before first use.

**Known Critical Limitations**

- Legacy `TrackerProject/` layer contains absolute researcher-specific filesystem paths (e.g., `~/...`) and JSON-file mutex coordination with well-documented race conditions and data-loss risks.
- Dockerfiles and some install scripts reference outdated directory layouts (`automation/`) and ancient browser stacks in certain configurations.
- The privileged instrumentation extension (manifest v2, `unsafe-eval` CSP) runs with chrome-level privileges; a compromised extension or malicious site exploiting instrumentation hooks presents a realistic host-escalation vector.
- No built-in authentication, authorization, or encryption-at-rest for telemetry. The platform assumes a fully trusted local execution context.
- Pickle-based IPC for exception transport between browser manager processes (local only, but deserialization of untrusted data remains a latent risk if queues are externally influenced).

**Status**: Suitable only for controlled academic and internal research after substantial hardening and modernization. Not intended for operational, high-volume, or security-sensitive production measurement.

See [docs/Security-Hardening.md](docs/Security-Hardening.md) and [docs/SECURITY.md](docs/SECURITY.md) for the full threat model, OWASP/NIST mapping, and prioritized remediation roadmap.

---

## Overview

`headerbidding` is the active modernization effort for a specialized research fork of the [OpenWPM](https://github.com/openwpm/OpenWPM) web privacy measurement framework. It adds deep instrumentation and harvesting for header bidding / Prebid.js auction dynamics while preserving the core strengths of OpenWPM: parallel browser orchestration, comprehensive HTTP/JS/cookie telemetry, and multiple storage backends.

**Modern Core (Recommended)**:
- `openwpm/` – Python 3.10+ package (TaskManager, BrowserManager, command system, storage providers for SQLite/Parquet/S3/GCS/LevelDB).
- `Extension/` – TypeScript WebExtension (webpack-built) with background instruments and custom privileged Firefox experiment APIs.
- Modern CI (CodeQL, pre-commit, pytest matrix, conda caching), type checking (mypy), and container build workflows.

**Legacy Research Layer (Transitioning)**:
- `TrackerProject/` – HB-specific crawling orchestration, A/B testing across 17 IAB verticals, bid harvesting (`pbjs.getBidResponses()`), ML pipelines for interest profile inference from bid patterns, and custom HB logging.

The platform enables reproducible studies on bidder landscape concentration, privacy extension impact on eCPM/win rates, and the privacy risks of RTB telemetry leakage.

For the full Documentation Set (including detailed guides and the Documentation Index), see below.

---

## Key Features & Instrumentation

| Component                    | Capability                                                                 | Security Notes |
|------------------------------|----------------------------------------------------------------------------|----------------|
| **Toolchain & Installation** | Conda-based environment (`environment.yaml`), dedicated Firefox 150+ installer (`scripts/install-firefox.sh`), modern TypeScript WebExtension build | Prefers isolated conda envs; legacy system `apt` paths deprecated |
| Browser Orchestration        | N parallel isolated Firefox instances via Selenium + geckodriver; synchronized or sharded execution | Process + profile isolation; watchdog for crash recovery |
| HTTP Instrumentation         | Full requests, responses, redirects, POST bodies, headers, CSP, referrer, optional content + call stacks | High data sensitivity; bodies must be classified/redacted |
| JavaScript Instrumentation   | Configurable property gets/sets/calls on sensitive APIs (fingerprinting collections + custom); recursion depth control; full call stacks via privileged `stackDump` | `unsafe-eval` and broad permissions required; page context untrusted |
| Cookie & Navigation          | `document.cookie`, profile cookies, navigation events, DNS queries         | Cross-site tracking surface captured by design |
| Header Bidding Harvest       | Injected `ScriptUtils` extraction of `pbjs.getBidResponses()`, winning bids, CPM, timeToRespond, bidder, adUnit | Executes researcher JS in page; results written to researcher-controlled FS/JSON |
| Blocking & A/B Profiles      | uBlock Origin, Ghostery, Disconnect + custom entity lists for intent vs. no-intent experiments | Can materially affect observed publisher revenue |
| Storage & Export             | SQLite (primary), Apache Parquet (analytics-ready), S3/GCS, LevelDB unstructured | No encryption at rest in default configuration |
| ML / Profiling (Legacy)      | Bid feature extraction → synthetic user interest profiles → training pipelines | High re-identification risk; GDPR special-category inference possible |

Full instrumentation settings: [docs/Configuration.md](docs/Configuration.md) and `schemas/js_instrument_settings.schema.json`.

For the complete Documentation Set, see below.

---

## Quick Start (Modern API)

**Prerequisites (Recommended Path)**

- Ubuntu 22.04+ / macOS (recent)
- Conda (Miniforge recommended)
- Docker (optional but recommended for isolation)

```bash
git clone <repository-url> headerbidding
cd headerbidding

# Primary modern installation
conda env create -f environment.yaml
conda activate openwpm
./scripts/install-firefox.sh

# For development (TypeScript extension + testing tools)
./install-dev.sh          # Linux
# or
./install-mac-dev.sh      # macOS
```

> **Note**: The root `./install.sh` still exists for backward compatibility but the
> conda + `scripts/` path above is the current recommended toolchain.

**Minimal Modern Crawl Example**

```python
from pathlib import Path
from openwpm.config import ManagerParams, BrowserParams
from openwpm.task_manager import TaskManager
from openwpm.commands.browser_commands import GetCommand  # or CommandSequence wrapper

NUM_BROWSERS = 2

# Load hardened defaults (see docs/Configuration.md for all options)
manager_params = ManagerParams(
    num_browsers=NUM_BROWSERS,
    data_directory=Path("./datadir/"),
    log_path=Path("./datadir/"),
)

browser_params = [
    BrowserParams(
        http_instrument=True,
        js_instrument=True,
        js_instrument_settings=["collection_fingerprinting"],
        cookie_instrument=True,
        navigation_instrument=True,
        display_mode="headless",
        bot_mitigation=True,
        # ublock_origin=True,  # enable via profile configuration
    )
    for _ in range(NUM_BROWSERS)
]

# Create isolated data directory
manager_params.data_directory.mkdir(parents=True, exist_ok=True)

tm = TaskManager(manager_params, browser_params)

sites = ["https://example.com", "https://news.example.com"]

for site in sites:
    # Modern command sequencing (see openwpm/commands/)
    tm.execute_command_sequence(
        site,
        commands=[
            GetCommand(url=site, sleep=5, timeout=60),
            # Additional custom or built-in commands...
        ],
        index="**",  # synchronized across browsers
    )

tm.close()  # Graceful shutdown + storage flush
```

See `demo.py` (legacy style), `crawler.py`, `custom_command.py`, and [docs/Usage-Guide.md](docs/Usage-Guide.md) for additional patterns. Header-bidding-specific bid harvesting logic resides in `TrackerProject/src/ScriptUtils/scriptUtils.py` and related crawlers.

**Rebuild Extension After Changes**

```bash
./scripts/build-extension.sh
# or
cd Extension && npm run build
```

For the complete set of documentation (including detailed configuration, security, deployment, and troubleshooting guides), see the [Documentation Set](#documentation-set) section below.

---

## Architecture at a Glance

The system follows a multi-process Zero Trust-inspired research workload model:

- **TaskManager** (orchestrator): Command distribution, browser pool management, watchdog, failure budgets.
- **BrowserManager** (per-instance): Selenium lifecycle, profile creation, extension injection, command execution, exception IPC.
- **WebExtension** (privileged): Deep instrumentation via experiment APIs; bidirectional socket communication with Python side.
- **StorageController**: Isolated writer process for structured (Parquet/SQL) and unstructured (LevelDB) backends; cloud providers optional.
- **Legacy HB Layer**: `TrainingCrawl` / A/B state machines + ML pipelines operating on bid exports.

Detailed component responsibilities, data flows, security boundaries, and Mermaid diagrams: [docs/Architecture.md](docs/Architecture.md).

For the full Documentation Set, see below.

---



## Development & Testing

Follow [AGENTS.md](AGENTS.md) for day-to-day commands.

```bash
# Full test suite (multi-process, requires display or xvfb)
pytest -m "not slow" -n auto

# Pre-commit (lint, typecheck, formatting)
pre-commit run --all-files

# Extension only
cd Extension && npm run lint && npm run build
```

See [docs/Build-Process.md](docs/Build-Process.md) for supply-chain security requirements (pinning, CodeQL, SBOM).

---

## Contributing

All contributions **must** improve security posture, test coverage, or modernization progress. PRs that introduce features without corresponding hardening, documentation, or tests will be rejected.

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and [docs/Development.md](docs/Development.md).

---

## License & Acknowledgments

Mozilla Public License 2.0. See [LICENSE](LICENSE).

This platform is derived from OpenWPM, originally developed by the Princeton University Center for Information Technology Policy (CITP) and Mozilla. Header bidding research extensions were created to study the privacy, security, and economic properties of real-time advertising auctions.

**Maintained for research transparency, reproducibility, and responsible disclosure of ad-tech measurement risks. Not for operational or commercial use without major remediation.**

For questions on responsible use or the modernization program, open an issue with the `security` or `modernization` label.
## Documentation Set

This project maintains a comprehensive, professional documentation suite designed for security-conscious research use. The documents below represent the actively maintained core.

### Core Documentation

| Document | Location | Description |
|----------|----------|-------------|
| [README.md](README.md) | `README.md` | Project overview, security warnings, quick start, and high-level guidance. |
| [AGENTS.md](docs/AGENTS.md) | `docs/AGENTS.md` | Operational instructions for AI coding agents (build commands, testing, known issues). |
| [AI-Agent-Context.md](docs/AI-Agent-Context.md) | `docs/AI-Agent-Context.md` | Strict rules and context specifically for AI coding agents working on this codebase. |
| [version.md](docs/version.md) | `docs/version.md` | Versioning policy and fork change history. |

### Architecture & Design

| Document | Location | Description |
|----------|----------|-------------|
| [Architecture.md](docs/Architecture.md) | `docs/Architecture.md` | Primary architecture reference with Mermaid diagrams, trust boundaries, and data flows. |
| [Architecture-Internals.md](docs/Architecture-Internals.md) | `docs/Architecture-Internals.md` | Supplementary internal architecture details and diagrams. |
| [Platform-Architecture.md](docs/Platform-Architecture.md) | `docs/Platform-Architecture.md` | *Legacy* – Older platform architecture documentation. |

### Security & Governance

| Document | Location | Description |
|----------|----------|-------------|
| [Security-Hardening.md](docs/Security-Hardening.md) | `docs/Security-Hardening.md` | Comprehensive security guide (OWASP, NIST, Zero Trust, AI agent risks, hardening checklist). |
| [SECURITY.md](docs/SECURITY.md) | `docs/SECURITY.md` | Vulnerability disclosure policy and supported versions. |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | `docs/CONTRIBUTING.md` | Contribution guidelines with security and modernization requirements. |
| [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md) | `docs/CODE_OF_CONDUCT.md` | Project code of conduct. |
| [Security-and-Privacy.md](docs/Security-and-Privacy.md) | `docs/Security-and-Privacy.md` | *Legacy* – Earlier threat model and privacy analysis. |

### Guides & Operations

| Document | Location | Description |
|----------|----------|-------------|
| [Installation-Guide.md](docs/Installation-Guide.md) | `docs/Installation-Guide.md` | Installation instructions and supported environments. |
| [Build-Process.md](docs/Build-Process.md) | `docs/Build-Process.md` | Build process, supply chain security, and dependency management. |
| [Deployment.md](docs/Deployment.md) | `docs/Deployment.md` | Deployment patterns (local, container, Kubernetes, air-gapped). |
| [Configuration.md](docs/Configuration.md) | `docs/Configuration.md` | Complete reference for ManagerParams and BrowserParams. |
| [Troubleshooting.md](docs/Troubleshooting.md) | `docs/Troubleshooting.md` | Common issues and debugging guidance. |
| [Development.md](docs/Development.md) | `docs/Development.md` | Developer workflow and contribution process. |
| [Release-Checklist.md](docs/Release-Checklist.md) | `docs/Release-Checklist.md` | Release preparation checklist. |

### Usage & Research

| Document | Location | Description |
|----------|----------|-------------|
| [Usage-Guide.md](docs/Usage-Guide.md) | `docs/Usage-Guide.md` | Detailed usage patterns and header bidding research workflows. |
| [Using_OpenWPM.md](docs/Using_OpenWPM.md) | `docs/Using_OpenWPM.md` | *Legacy* – Guide to core OpenWPM functionality. |
| [Schema-Documentation.md](docs/Schema-Documentation.md) | `docs/Schema-Documentation.md` | Overview of platform data schemas. |

### Technical Reference

| Document | Location | Description |
|----------|----------|-------------|
| [JSON Schema Documentation](docs/schemas/README.md) | `docs/schemas/` | Auto-generated documentation for JavaScript instrumentation settings. |

Additional legacy and auto-generated content exists under `docs/`. The documents above represent the actively maintained core of the documentation set.
