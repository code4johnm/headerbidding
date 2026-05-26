# OpenWPM-MAGA Versioning

**Document Version:** 1.2  
**Base Upstream Version:** 0.34.0  
**Fork Name:** headerbidding (OpenWPM-MAGA)  
**Last Updated:** 2026-04-26

---

## Overview

This document describes the versioning approach for the **OpenWPM-MAGA** fork of [OpenWPM](https://github.com/openwpm/OpenWPM).

headerbidding (OpenWPM-MAGA) is a maintained distribution focused on:
- High-quality, professional, and well-organized documentation following industry security and research standards (OWASP, NIST CSF, SSDL, Zero Trust).
- Documentation centralization, Mermaid diagram compatibility, and removal of machine-specific references.
- Practical modernization of installation and build processes.
- Operational excellence and security guidance for privacy measurement research.

## Base Version

This fork is based on upstream OpenWPM **v0.34.0**.

The canonical upstream version is recorded in the root [VERSION](../VERSION) file.

## Fork Versioning Scheme

We follow a pragmatic hybrid versioning model:

- **Upstream alignment**: We track the upstream major.minor version (e.g., 0.34).
- **Fork patch / feature suffix**: When we make meaningful changes in this fork, we may append a local suffix in the form `0.34.0-maga.N` (where N is a sequential fork patch number) for releases or tagged builds.
- **Documentation-driven releases**: Because a large portion of the value in this fork currently comes from documentation and process improvements, documentation updates may trigger fork patch releases even without core code changes.

For day-to-day development, the root `VERSION` file continues to reflect the upstream base.

## Major Changes in the OpenWPM-MAGA Fork

### Documentation Overhaul and Organization (Major Focus)

A comprehensive documentation modernization and organization effort was completed:

**Documentation Structure Improvements**
- All top-level `.md` documentation files (except README.md) were moved into `docs/` for better organization and maintainability (`AGENTS.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CLAUDE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AI-Agent-Context.md`).
- A curated **Documentation Index** table was added to README.md listing all major documents with name, location, and description columns.
- All machine-specific absolute paths (`/mnt/5TB/git/hb-update/...`) were removed from documentation and replaced with clean relative paths.

**Documentation Quality & Rendering Fixes**
- Major improvements to Mermaid diagrams in `docs/Architecture.md`:
  - Replaced non-rendering `C4Context` syntax with standard Mermaid flowcharts.
  - Fixed `\n` line breaks (replaced with `<br/>`).
  - Removed `classDef` styling and inner `direction` directives that caused GitHub rendering failures.
- Added a proper text-based legend for trust levels in architecture diagrams.
- Bumped document versions across the suite to 1.2.0.

**New and Significantly Updated Documents**
- `docs/Security-Hardening.md` — New comprehensive guide covering OWASP Top 10, NIST CSF, Zero Trust for research workloads, privileged extension security, AI agent integration risks, and a prioritized hardening checklist.
- `docs/AI-Agent-Context.md` — New strict rule set and context file for AI coding agents.
- `docs/Build-Process.md`, `docs/Deployment.md`, `docs/Troubleshooting.md` — New or heavily expanded operational guides.
- `README.md` — Complete rewrite with modern quick start, toolchain information, and security warnings.
- `docs/Architecture.md` — Significantly expanded with multiple diagrams and trust boundary analysis.
- `docs/SECURITY.md` and `docs/CONTRIBUTING.md` — Updated and moved into docs/.

**Install Script & Toolchain Modernization**
- Removed dangerous legacy Adobe Flash installation logic (Ubuntu 14.04 "trusty" repositories).
- Modernized `install.sh`, `install-dev.sh`, and `install-mac-dev.sh` to prefer the conda + `scripts/install-firefox.sh` path.
- Updated documentation and scripts to target current Firefox (150+) instead of legacy Firefox 52.

**Project Identity Normalization**
- Internal references updated from "hb-update" to "headerbidding" for consistency with the project's canonical name while preserving local directory structure.

All documentation now follows consistent professional standards with version numbers, dates, security considerations, and cross-references.

### Code Improvements and Bug Fixes

The following targeted improvements have been applied on top of upstream v0.34.0:

| Area | Change | Related Upstream Issue |
|------|--------|------------------------|
| JavaScript Instrumentation | Added defensive `try/catch` guards around `eval(item.object)` and `Object.getPropertyNames(object)` inside `instrumentJS()` and `instrumentObject()`. Failing targets in custom or large instrumentation collections no longer abort processing of the entire collection. | [#1171](https://github.com/openwpm/OpenWPM/issues/1171) |
| Configuration Validation | Removed dead/unreachable code paths and improved the error message for the long-broken `callstack_instrument` flag. | [#557](https://github.com/openwpm/OpenWPM/issues/557) and follow-ups |
| Test Reliability | `test_cache_hits_recorded` now uses a per-test `?cachebust=` query parameter on the first visit to prevent stale HTTP cache entries (from the shared test server's long `max-age` headers) from polluting first-load assertions. The second visit still exercises real browser caching behavior. | [#1162](https://github.com/openwpm/OpenWPM/issues/1162) |

These changes are documented in the [CHANGELOG.md](../CHANGELOG.md) under the "Unreleased" section.

### Other Fork Characteristics

- **Documentation as a first-class deliverable**: The majority of meaningful work in this fork has been in creating and maintaining high-quality, secure, auditable documentation (including architecture diagrams, security hardening guides, AI agent context files, and operational playbooks).
- Strong focus on documentation organization, including centralizing files under `docs/`, creating a Documentation Index, removing machine-specific paths, and ensuring diagrams render correctly on GitHub.
- Practical modernization of installation and build tooling (removal of Flash support, preference for conda + modern Firefox installer).
- All documentation follows a consistent professional style with version/date stamps, security considerations, and cross-references.

## Future Versioning

When preparing a release or significant update from this fork:

1. Update the root `VERSION` file if a new fork patch version is being cut.
2. Add a dated entry under the appropriate section in `CHANGELOG.md`.
3. Update this `docs/version.md` file with a summary of new changes (especially documentation, security, and toolchain work).
4. Consider tagging with a fork-specific suffix (e.g., `v0.34.0-maga.1`).

Documentation and process improvements are considered first-class changes and may warrant a fork version bump on their own.

## Relationship to Upstream

We aim to stay reasonably close to upstream OpenWPM for core measurement functionality while diverging primarily in:
- Documentation quality and completeness
- Selected reliability and robustness improvements
- Security and operational guidance tailored to privacy research use cases

Significant upstream changes should be evaluated for merge, with preference given to changes that do not regress the improvements made in this fork.

---

*This document should be updated with every meaningful change or release originating from the OpenWPM-MAGA fork.*