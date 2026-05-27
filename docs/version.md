# OpenWPM-1776 Versioning

**Document Version:** 1.5  
**Base Upstream Version:** 0.34.0  
**Fork Name:** headerbidding (OpenWPM-1776)  
**Base Fork:** OpenWPM-1776 (https://github.com/code4johnm/OpenWPM-1776)  
**Last Updated:** 2026-05-27T15:30:00Z

---

## Overview

This document describes the versioning approach for **headerbidding**, a specialized research distribution **based on the [OpenWPM-1776](https://github.com/code4johnm/OpenWPM-1776) fork** of [OpenWPM](https://github.com/openwpm/OpenWPM).

headerbidding (OpenWPM-1776) is a maintained distribution focused on:
- High-quality, professional, and well-organized documentation following industry security and research standards (OWASP, NIST CSF, SSDL, Zero Trust).
- Documentation centralization, Mermaid diagram compatibility, and removal of machine-specific references.
- Practical modernization of installation and build processes.
- Operational excellence and security guidance for privacy measurement research.

## Base Version

This distribution (headerbidding) is based on the [OpenWPM-1776](https://github.com/code4johnm/OpenWPM-1776) fork of upstream OpenWPM **v0.34.0** (with all robustness fixes, documentation, and modernization from that base).

The current fork version is recorded in the root [VERSION](../VERSION) file (currently `1.4.0`).

## Fork Versioning Scheme

We follow a pragmatic hybrid versioning model:

- **Upstream alignment**: We track the upstream major.minor version (e.g., 0.34).
- **Fork patch / feature suffix**: When we make meaningful changes in this fork, we may append a local suffix in the form `0.34.0-1776.N` (where N is a sequential fork patch number) for releases or tagged builds.
- **Documentation-driven releases**: Because a large portion of the value in this fork currently comes from documentation and process improvements, documentation updates may trigger fork patch releases even without core code changes.

For day-to-day development, the root `VERSION` file continues to reflect the upstream base.

## Version History

This section provides a structured record of major changes and releases in the headerbidding (OpenWPM-1776) fork.

| Version | Date       | Description of Changes |
|---------|------------|------------------------|
| 1.5.0   | 2026-05-27 | **Base hb-update on OpenWPM-1776 + Reference & Dependency Updates**<br><br>• Established OpenWPM-1776 as the canonical base for the hb-update (headerbidding) distribution: synced core Extension instrumentation source (`js-instruments.ts` with defensive guards) from OpenWPM-1776 into hb-update to ensure identical foundation.<br>• Updated all OpenWPM dependency references: `package.json` and `Extension/package.json` repository URLs changed from `openwpm/OpenWPM` to `code4johnm/OpenWPM-1776` so that the hb-update repo's declared OpenWPM base/dependencies resolve from the OpenWPM-1776 fork.<br>• Updated prose references in README.md and `docs/version.md` (Overview, Base Version, Relationship to Upstream sections) to explicitly declare "based on the OpenWPM-1776 fork".<br>• Bumped root `VERSION` 1.4.0 → 1.5.0; synchronized Document Version, dates, Last Updated, and Fork/Base declarations across docs.<br>• Added this Version History entry documenting the basing step.<br>• Executed full "build, run, test, repeat" cycle (see /tmp/msg.txt for details): Extension npm build + lint, Python import smoke tests, `pytest -m pyonly` (repeated, all green). |
| 1.4.0   | 2026-05-27 | **Header Bidding Version Bump to 1.4.0 + Dev Cycle & Commit Message Hygiene**<br><br>• Bumped root `VERSION` from 1.3.0 → 1.4.0 and synchronized **Version**/**Document Version**/**Date**/**Last Updated** headers + version references across the full documentation suite (README.md, SECURITY.md, Build-Process.md, Architecture.md, Security-Hardening.md, Deployment.md, Configuration.md, CONTRIBUTING.md, Troubleshooting.md, AI-Agent-Context.md, and this file).<br>• Rolled back (git commit --amend) the previous commit message from long-form detailed text to the concise new "build, run, test, repeat." style message, aligning with the newly documented Iterative Development Cycle.<br>• Updated `/tmp/msg.txt` with the rolled-back short message and prepared version-bump commit narrative.<br>• Executed "build, run, test, repeat" cycle as primary workflow: baseline + post-edit verification via `python -m pytest -m pyonly` (all green), Extension npm build/lint attempts, and pre-commit hygiene checks.<br>• Added this Version History entry; reinforced that documentation + process improvements (including workflow discipline and version hygiene) are first-class triggers for fork version bumps. |
| 1.3.0   | 2026-05-26 | **Fork Identity Normalization: OpenWPM-MAGA → OpenWPM-1776**<br><br>• Updated *all* references from the legacy "OpenWPM-MAGA" fork name to the new "OpenWPM-1776" across documentation in both the OpenWPM-1776 and hb-update repositories.<br>• Updated titles, **Fork Name** declarations, "**Workspace:**" headers, body text, SECURITY.md, Security-and-Privacy.md, and `docs/version.md`.<br>• Updated fork versioning suffix examples (`maga.N` → `1776.N`) in both projects.<br>• Added this Version History entry and refreshed the Supported Versions table in SECURITY.md.<br>• Bumped documentation suite (including this file) and root `VERSION` to 1.3.0 for alignment. |
| 1.2.0   | 2026-04-26 | **Documentation Organization, Versioning & Rendering Polish**<br><br>**Documentation Index & Structure**<br>• Expanded the Documentation Index table in README.md to include nearly all current files in `docs/`, with clear, professional descriptions for each entry.<br>• Added missing documents such as `version.md`, `Architecture-Internals.md`, `Platform-Architecture.md`, `Release-Checklist.md`, `Schema-Documentation.md`, and `Using_OpenWPM.md`.<br>• Grouped schema-related files under a single "JSON Schema Documentation" entry for better readability.<br><br>**version.md Improvements**<br>• Added a clean "Major Accomplishments Summary (2026)" section at the top of the Major Changes area.<br>• Converted the change history into a proper, scannable Version History table.<br>• Significantly expanded and restructured the documentation of all recent work.<br><br>**Versioning**<br>• Bumped document versions to **1.2.0** consistently across the entire suite (README, Architecture, Security-Hardening, Build-Process, Deployment, Configuration, Troubleshooting, AI-Agent-Context, CONTRIBUTING, etc.).<br>• Bumped the root `VERSION` file from `0.8.0` → `1.2.0` to align with documentation versioning.<br><br>**Mermaid & Rendering**<br>• Final round of Mermaid diagram fixes in `docs/Architecture.md` for reliable GitHub rendering (removal of remaining `classDef`, inner `direction TB`, and any leftover `\n` characters).<br><br>**Path Cleanup**<br>• Performed final removal of the last absolute workspace path references from the Documentation Index.<br><br>**README Navigation Improvements**<br>• Added multiple "follow-on" references to the Documentation Set throughout key sections of README.md (Overview, Key Features & Instrumentation, Quick Start, Architecture at a Glance) to improve discoverability of the full documentation.<br>• Updated the top callout to better direct readers to the complete Documentation Set table. |
| 1.1.0   | 2026-04    | **Documentation Structure, Mermaid Fixes & Path Cleanup**<br><br>• Created the initial curated Documentation Index table in README.md.<br>• Performed the first major round of Mermaid diagram fixes in `docs/Architecture.md`:<br>  - Replaced the non-rendering `C4Context` diagram with standard Mermaid flowcharts.<br>  - Fixed `\n` line breaks in node labels (converted to `<br/>`).<br>  - Removed early `classDef` usage that was causing GitHub parse errors.<br>• Removed the majority of machine-specific absolute paths (`/mnt/5TB/git/hb-update/...`) from all documentation files.<br>• Bumped versions across the documentation suite to 1.1.0 and updated the Supported Versions table in `SECURITY.md`. |
| 1.0.0   | 2026-04    | **Initial Professional Documentation Suite & Foundational Modernization**<br><br>**Documentation Creation & Expansion**<br>• Complete rewrite of README.md with security-first design, modern quick start, toolchain information, and a high-level features table.<br>• Created several major new professional documents:<br>  - `Security-Hardening.md` (OWASP, NIST, Zero Trust, AI agent security, hardening checklist)<br>  - `AI-Agent-Context.md` (strict rules for AI coding agents)<br>  - `Build-Process.md`, `Deployment.md`, `Troubleshooting.md`, and others.<br>• Significantly expanded `docs/Architecture.md` with multiple detailed Mermaid diagrams, trust boundaries, and system context views.<br><br>**Documentation Organization**<br>• Centralized all top-level `.md` files into the `docs/` directory for better maintainability (`AGENTS.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CLAUDE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AI-Agent-Context.md`).<br><br>**Tooling & Script Modernization**<br>• Modernized `install.sh`, `install-dev.sh`, and `install-mac-dev.sh`.<br>• Deprecated and removed dangerous legacy Adobe Flash installation (Ubuntu 14.04 "trusty" repositories).<br>• Aligned installation with the modern conda environment + Firefox 150+ unbranded builds.<br><br>**Other Improvements**<br>• Project identity normalization: updated references from "hb-update" to "headerbidding" across documentation.<br>• Established consistent professional standards (version numbers, dates, security callouts, and cross-references) across all docs. |

| Planned | TBD        | **Future Enhancements**<br><br>• Further expansion or categorization of the Documentation Index (e.g., by topic or audience).<br>• Potential addition of more architecture diagrams or security-related visuals.<br>• Continued alignment between root `VERSION` and documentation releases.<br>• Possible deeper integration of security hardening tracking into the version history.<br>• Expand follow-on references and cross-links throughout the documentation. |

### Code Improvements and Bug Fixes (Historical)

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
4. Consider tagging with a fork-specific suffix (e.g., `v0.34.0-1776.1`).

Documentation and process improvements are considered first-class changes and may warrant a fork version bump on their own.

## Relationship to Upstream

headerbidding is directly based on the [OpenWPM-1776](https://github.com/code4johnm/OpenWPM-1776) fork (which itself tracks upstream OpenWPM v0.34.0 plus robustness and docs improvements). We aim to stay reasonably close to the OpenWPM-1776 base for core measurement functionality while diverging primarily in:
- Header bidding / Prebid.js auction telemetry and A/B instrumentation (TrackerProject layer)
- Documentation quality and completeness
- Selected reliability and robustness improvements
- Security and operational guidance tailored to privacy research use cases

Significant changes from OpenWPM-1776 or upstream should be evaluated for merge, with preference given to changes that do not regress the improvements made in this distribution.

---

*This document should be updated with every meaningful change or release originating from the headerbidding (OpenWPM-1776-based) distribution.*