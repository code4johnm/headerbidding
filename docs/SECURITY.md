# Security Policy

**hb-update: Header Bidding Research Platform (Modernized OpenWPM)**  
**Version**: 1.1.0  
**Date**: 2026-04-26  
**Last Reviewed**: 2026-04-26  
**Classification**: Public with controlled disclosure

**Standards Alignment**: This policy follows ISO 27001, NIST SP 800-53, and industry best practices for vulnerability disclosure in research tooling.

---

## 1. Supported Versions

| Version                  | Support Level                          | Notes |
|--------------------------|----------------------------------------|-------|
| 1.1.0 (current)          | Full security review + modernization   | Documentation centralization + path cleanup |
| 0.8.0-hb-update          | Security fixes only                    | Legacy research snapshot |
| Older / pre-modernization| Critical issues only                   | Strongly recommend migration |
| Legacy OpenWPM (Firefox 52) | None                                | Unpatchable vulnerabilities |

**Explicit Statement**: The platform intentionally bundles or historically referenced severely outdated browser components. The correct response to most legacy browser CVEs is **migration and containment**, not backporting patches.

---

## 2. Reporting a Vulnerability

### 2.1 Preferred Channels (in order)

1. **GitHub Private Security Advisory** (if the repository has the feature enabled) — best for coordinated handling.
2. **Email** to the current maintainers with subject prefix `[SECURITY] [hb-update]`.
3. **Encrypted email** (PGP key published in repository or institutional directory) for high-severity issues.

### 2.2 Required Information in Report

- Clear description of the weakness and realistic attack scenario.
- Steps to reproduce (redact any sensitive researcher data or internal site lists).
- Affected component (modern core `openwpm/`, privileged Extension, legacy `TrackerProject/`, build system, etc.).
- Potential impact on collected research data or host compromise.
- Suggested remediation or compensating control.
- Whether you are willing to be credited publicly.

### 2.3 Response Timeline

- Acknowledgment within 72 hours.
- Initial severity assessment and response plan within 7 days.
- Public disclosure timeline agreed with reporter (typically 90 days for high-severity issues, longer for complex architectural problems).

---

## 3. Severity Classification for This Platform

Because this is a research measurement tool with intrinsic high privileges, severity is assessed against **both technical exploitability and research data exposure**:

- **Critical**: Remote code execution via the privileged extension, unauthenticated exfiltration of raw telemetry, or compromise of the research host from a visited site.
- **High**: Integrity violation of bid data or crawl results (undetected tampering), large-scale leakage of unredacted HTTP bodies or JS stacks, bypass of intended allow-lists.
- **Medium**: Local information disclosure of researcher paths or config, resource exhaustion leading to data loss, weak but local-only deserialization issues.
- **Low**: Documentation inaccuracies, minor dependency findings without practical exploit in the research context.

Data sensitivity (bid landscapes that enable re-identification or revenue inference) can elevate an otherwise Medium technical finding to High or Critical.

---

## 4. Out-of-Scope

- Social engineering or physical attacks against researchers.
- Attacks that require prior code execution on the research host (the model assumes host compromise is game-over).
- Complaints about the existence of the legacy vulnerable stack (already documented and prioritized for removal).
- Theoretical issues in ancient bundled components without a novel, practical attack path against a properly contained research deployment.

---

## 5. Coordinated Disclosure & Researcher Responsibilities

- We will not publish exploit details until a reasonable mitigation or migration path exists.
- Reporters are expected to act in good faith and not exploit the issue against third parties or other researchers.
- Credit will be given in release notes and the changelog unless anonymity is requested.

---

## 6. Security.txt & Future Hosting

When this project is hosted with a public website, a `/.well-known/security.txt` will be published pointing to this policy and the reporting channels.

---

## 7. Relationship to Other Documents

- [docs/Security-Hardening.md](docs/Security-Hardening.md) – Technical controls and threat model implementation.
- [docs/Architecture.md](docs/Architecture.md) – Trust boundaries and data flows.
- [README.md](README.md) – High-level responsible use warning.

This policy is versioned. Material changes will be announced in the changelog and via GitHub release notes.

**Full path**: `docs/SECURITY.md`
