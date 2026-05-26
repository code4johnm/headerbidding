# Security Policy

**HeaderBidding Research Platform**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-04  
**Last Reviewed**: 2026-04

---

## Supported Versions

Because this is a research snapshot with a deliberately archived legacy browser stack, only the following receive any attention:

| Version | Supported | Notes |
|---------|-----------|-------|
| 0.8.0-hb (current research snapshot) | Security fixes only via modernization PRs | Primary focus is **replacement**, not patching Firefox 52 |
| Older OpenWPM forks | No | |

**Important**: The bundled Firefox 52 ESR, geckodriver 0.15, and Add-on SDK extension contain hundreds of known, unpatched vulnerabilities. These are **accepted known risks** of the current artifact. The correct response is architectural modernization, not CVSS scoring of the 2017-era components.

---

## Reporting a Vulnerability

### For Issues in the Research Harness (Python orchestration, data handling, coordination logic, documentation)

- **Preferred**: Open a private GitHub Security Advisory (if the repository has the feature enabled) or email the current maintainers with subject prefix `[SECURITY]`.
- Include:
  - Clear description of the weakness and potential impact.
  - Steps to reproduce (redacted if necessary).
  - Suggested remediation or hardening.
  - Whether the issue is in legacy OpenWPM core or TrackerProject HB layer.

### For Issues in the Bundled Browser / Driver / Extension

These components are intentionally ancient. Report only if you discover a **new** 0-day that affects the specific old versions in a novel way that could be exploited against research deployments. In most cases, simply document the exposure and focus effort on the modernization roadmap in [docs/Security-and-Privacy.md](docs/Security-and-Privacy.md).

**Do not** publish exploit code or detailed reproduction steps for browser vulnerabilities publicly until the research community has had reasonable time to migrate.

---

## Coordinated Disclosure Expectations

- We will acknowledge receipt within 72 hours.
- We will work with reporters on a mutually agreeable timeline for public disclosure.
- Credit will be given unless the reporter requests anonymity.
- Because the primary risk is the **research data itself** (bid profiles, cookies, HTTP bodies), any vulnerability that could lead to large-scale exfiltration of measurement datasets will be treated as **Critical** even if the technical CVSS score on the browser is "only" High.

---

## Out-of-Scope

- Social engineering of researchers.
- Physical attacks on research hardware.
- Attacks that require the attacker to already have code execution on the research machine (the entire threat model assumes the host is trusted).
- Complaints about the existence of the legacy vulnerable stack (we already know).

---

## Security.txt

When this project is hosted on a public repository with a website, a `/.well-known/security.txt` will be published pointing back to this policy and the vulnerability reporting channel.

---

**This policy itself is versioned and should be updated whenever the disclosure process or supported version policy changes.**
