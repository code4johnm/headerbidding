# Security Hardening Guide

**headerbidding: Header Bidding Research Platform**  
**Document Version**: 1.3.0  
**Date**: 2026-05-27T02:47:30Z  
**Classification**: Public (controlled disclosure for sensitive implementation details)  
**Standards**: OWASP Top 10 (2021), OWASP ASVS 4.0 (target Level 2), OWASP Top 10 for LLM Applications (where AI orchestration is used), NIST Cybersecurity Framework v1.1, ISO 27001:2022 control mapping, Secure Software Development Lifecycle (SSDL), Zero Trust Architecture principles (NIST SP 800-207 adapted for research workloads).

**Authors / Reviewers**: Platform Maintainers (Security & Research Engineering)  
**Review Cadence**: Quarterly or upon any material architecture change.

---

## 1. Executive Summary & Current Security Posture

The headerbidding platform is a **high-privilege, high-sensitivity research instrument**. It intentionally operates with elevated browser privileges to achieve measurement goals that standard web crawlers cannot. This design creates an intrinsic tension between research utility and security.

**Current Posture Assessment (2026-04)**: **High Risk – Suitable only for hardened, isolated research deployments after implementing controls in this document.**

**Primary Attack Surfaces** (ranked by exposure):

1. **Privileged WebExtension** (`Extension/`) – Broad permissions + custom experiment APIs (`sockets`, `profileDirIO`, `stackDump`) running in Firefox chrome context with `unsafe-eval`.
2. **Legacy TrackerProject coordination layer** – File-based JSON mutexes, absolute researcher paths, Python 2/3 hybrid code with insufficient input validation on bid data and site lists.
3. **Data plane** – Unencrypted sensitive telemetry (full HTTP bodies, JS stacks, precise CPM + bidder participation) written to local FS or cloud object storage.
4. **Browser launch surface** – Subprocess invocation of geckodriver/Firefox, profile management, pickle-based IPC for exceptions.
5. **AI/Agent orchestration surface** (emerging) – If external LLM agents or autonomous crawlers drive site selection or command sequences, this introduces prompt injection, goal misalignment, and data exfiltration risks.

**Key Improvements Delivered by This Modernization Snapshot**:
- Migration of core to current OpenWPM layout (`openwpm/` + TypeScript `Extension/`) with mypy, pre-commit, CodeQL, and modern dependency tooling.
- Replacement of deprecated Add-on SDK patterns with WebExtension manifest v2 + experiment APIs (still privileged but better isolated than ancient XPCOM).
- Addition of this dedicated hardening guide and [docs/AI-Agent-Context.md](docs/AI-Agent-Context.md).
- CI security scanning (CodeQL) and coverage reporting.

**Remaining Critical Gaps** (must be addressed before production-scale or multi-researcher use):
- No encryption at rest or field-level redaction for telemetry.
- Legacy TrackerProject paths and race-prone coordination.
- Outdated Dockerfiles and install scripts.
- Absence of capability-based or allow-list enforcement at the TaskManager boundary.
- Insufficient security-focused audit logging and anomaly detection.
- No SBOM or reproducible build attestation.

---

## 2. Standards Alignment

### 2.1 OWASP Top 10 (2021) – Hardening Status & Requirements

| Category | Current State | Required Hardening Controls | Priority | Verification |
|----------|---------------|-----------------------------|----------|--------------|
| A01:2021 Broken Access Control | Poor | Enforce site allow-lists at TaskManager; capability tokens for AI agents; no unauthenticated IPC or FS coordination | P0 | pytest + manual review |
| A02:2021 Cryptographic Failures | Critical | Encrypt sensitive Parquet/SQLite at rest (age or LUKS); hash or redact high-entropy identifiers; TLS everywhere for S3/GCS | P0 | config validation + integration tests |
| A03:2021 Injection | Medium | Replace broad `execute_script` patterns with strict templates; parameterize all storage writes; validate all injected JS | P1 | SAST + fuzzing of bid harvesters |
| A04:2021 Insecure Design | High | Move to capability-based command model; data classification labels on all records; eliminate JSON mutex files | P0 | Architecture review |
| A05:2021 Security Misconfiguration | High | Default `BrowserParams` must be least-privilege; harden Firefox prefs; remove `unsafe-eval` where feasible or document residual risk | P1 | Pre-commit + CI gate |
| A06:2021 Vulnerable Components | Critical | Pin all deps with hashes; generate SBOM (CycloneDX); schedule Firefox/geckodriver upgrades; deprecate legacy TrackerProject | P0 | `scripts/repin.sh` + dependabot + CodeQL |
| A07:2021 Identification Failures | N/A (local) | Add strong identity for any future dashboard or multi-tenant deployment | P2 | — |
| A08:2021 Data Integrity | High | Sign crawl manifests and result sets; use content-addressable storage for artifacts; reject unsigned bid JSON | P1 | New signing module |
| A09:2021 Security Logging | Poor | Implement structured security event logging (see §7); forward to SIEM or local auditd | P0 | Logging PR + tests |
| A10:2021 SSRF | Medium (by design) | Mandatory egress proxy with allow-list + rate limits; DNS sinkholing for research | P0 | NetworkPolicy + proxy deployment guide |

### 2.2 NIST Cybersecurity Framework – Target Implementation

**Identify (ID)**:
- Automated asset inventory of installed extensions, block lists, and custom JS instruments (new `inventory.py` tool required).
- Data flow diagrams with sensitivity labels (see Architecture.md).

**Protect (PR)**:
- Least-privilege browser profiles per experiment (no persistent state unless explicitly required).
- Network segmentation (research VLAN or Kubernetes NetworkPolicy denying all egress except approved measurement destinations and storage endpoints).
- Supply chain: signed commits, pinned environments, reproducible Docker builds with attestation.

**Detect (DE)**:
- Behavioral baselining of crawl resource usage and bid pattern anomalies (early indicator of site fingerprinting the crawler or data poisoning).
- Mandatory security event logging for all `execute_command_sequence`, profile creation, and extension socket connections.

**Respond (RS) & Recover (RC)**:
- Documented incident playbook for suspected browser 0-day or data exfiltration (see §9).
- Automated profile and data directory wiping on detected anomalies.

### 2.3 Zero Trust for Research Workloads

Apply "never trust, always verify" even on localhost research machines:

- Every browser instance is a separate trust boundary.
- All commands from AI agents or human researchers must be authorized against an explicit allow-list + purpose tag.
- All data leaving the measurement boundary must pass a redaction / classification filter before storage or LLM consumption.
- Continuous verification: watchdog + resource limits + network policy enforcement.

---

## 3. Privileged Extension Permission Model (Core Security Boundary)

The instrumentation extension is the most security-critical component.

### 3.1 Manifest Permissions (Extension/bundled/manifest.json)

- `"<all_urls>"`, `webRequest`, `webRequestBlocking`, `webNavigation`, `cookies`, `dns`, `tabs`, `storage`, `management`, `downloads`, `mozillaAddons`.
- Custom `experiment_apis` (privileged scopes `addon_parent`):
  - `sockets`: Raw nsIServerSocket / binary protocol for low-latency bidirectional IPC with Python `socket_interface.py`. Bypasses some content security restrictions.
  - `profileDirIO`: Direct read/write access to the Firefox profile directory from chrome context.
  - `stackDump`: Access to JS engine call stack for accurate instrumentation of property accesses (used by javascript-instrument).

**Risks**:
- A single compromised content script or background page can open sockets to localhost or exfiltrate profile data.
- `unsafe-eval` in CSP is currently required for dynamic instrumentation hooks.
- `webRequestBlocking` allows the extension to observe and potentially modify all traffic.

### 3.2 Hardening Requirements for the Extension

1. **Short-term**:
   - Keep `web-ext lint --privileged` mandatory in CI (already present).
   - Add runtime guardrails in background scripts to reject connections from unexpected origins.
   - Document every privileged API call site with justification.

2. **Medium-term**:
   - Evaluate migration to Manifest V3 + `declarativeNetRequest` where blocking is needed.
   - Replace custom sockets with a more constrained WebSocket or native messaging channel if performance permits.
   - Implement stack trace redaction options (strip file:// and chrome:// frames before storage).

3. **Long-term**:
   - Explore Firefox's `proxy` API + isolated content processes for stronger containment.
   - Consider separate "measurement" vs "orchestration" extensions.

See [Extension/src/background/](Extension/src/background/) and `privileged/` for implementation.

---

## 4. AI Agent & Autonomous Orchestration Security

When external AI systems (LLMs, reinforcement learning crawlers, autonomous research agents) drive the platform, new risks from the OWASP Top 10 for LLM Applications become relevant.

### 4.1 Recommended Integration Architecture (Zero Trust)

```
AI Agent (LLM Planner / RL Policy)
    │ (capability token + signed task manifest)
    ▼
TaskManager (enforcement point)
    │ validate allow-list + purpose tag + budget
    ▼
Per-Browser Sandbox (least-privilege BrowserParams + network egress proxy)
    │
    ▼
Redaction / Classification Pipeline
    │ (remove PII, hash identifiers, drop sensitive categories)
    ▼
Storage + Optional LLM Summary Generator (read-only, sandboxed)
```

### 4.2 Mandatory Controls for AI-Driven Crawls

- **Capability Tokens**: Every command sequence submitted by an agent must carry a short-lived, signed JWT or Macaroon describing:
  - Allowed sites (glob or regex allow-list)
  - Maximum number of browsers and duration
  - Enabled instruments (no `save_content: true` unless explicitly justified)
  - Purpose tag (e.g., "hb-bidder-landscape-2026-Q2")
- **Human-in-the-Loop Gate**: High-value or out-of-allow-list sites require explicit approval before navigation.
- **Output Sanitization**: All records destined for downstream LLM consumption must pass a redaction stage (strip raw bodies by default; provide only structural metadata + one-way hashes of sensitive fields).
- **Audit Trail**: Every agent-issued command, browser launch, and data write must emit a structured security event (see §7).
- **Resource & Blast Radius Limits**: Per-agent quotas + automatic termination on anomalous memory/CPU or unexpected external domains.
- **Prompt / Goal Injection Defense**: If the agent uses natural language site selection, the planner prompt must be treated as untrusted input and validated against the allow-list before any browser is launched.

**Never** allow an LLM to directly generate JavaScript that will be passed to `run_custom_function` or `execute_script` without static analysis and sandbox execution first.

---

## 5. Concrete Hardening Checklist (Prioritized)

### Phase 0 – Immediate (Before Any New Research Run)

- [ ] Replace all absolute paths in `TrackerProject/` with relative or configurable paths. Remove or sandbox the legacy layer.
- [ ] Deploy an egress HTTP/SOCKS proxy with explicit destination allow-list + logging (e.g., mitmproxy or tinyproxy in allow-list mode).
- [ ] Enable full-disk encryption or per-dataset LUKS volumes for `datadir/`.
- [ ] Run all crawls inside a dedicated VM or Kubernetes namespace with `seccomp`, `apparmor`, and `NetworkPolicy` denying all egress except proxy + storage.
- [ ] Set `browser_params[*].save_content = False` by default; enable only for allow-listed MIME types with size caps.

### Phase 1 – Foundational (1–2 Sprints)

- [ ] Implement structured security audit logging (Python `logging` + JSON + correlation IDs).
- [ ] Add `ManagerParams` validation that rejects configurations without an explicit `allowed_domains` list.
- [ ] Generate and enforce SBOM (CycloneDX) in CI; fail on known vulnerable components above threshold.
- [ ] Update Dockerfiles to current Ubuntu LTS, non-root user, pinned base images, and multi-stage builds. Remove passwordless sudo.
- [ ] Replace pickle exception transport with a safer schema (e.g., msgpack + explicit allow-list of exception types).

### Phase 2 – Advanced Containment

- [ ] Capability-based command authorization layer in TaskManager.
- [ ] Data classification labels + automatic redaction pipeline (prototype using `presidio` or custom rules for email/UUID/IBAN in HTTP bodies and JS arguments).
- [ ] Firefox profile content signing or measured boot of the extension bundle.
- [ ] Optional: integrate with confidential computing (SEV-SNP or Nitro) for high-sensitivity bid profile studies.

### Phase 3 – Long-term Modernization

- [ ] Full deprecation of `TrackerProject/` in favor of a clean, typed Python module under `openwpm/hb/`.
- [ ] Manifest V3 migration or WebDriver BiDi + Chrome DevTools Protocol alternative for future browser support.
- [ ] Formal verification or model-based testing of the command → data flow for the highest-risk instruments.

---

## 6. Supply Chain & Build Security

- All Python dependencies are managed via `environment.yaml` + `scripts/repin.sh`. Never edit pinned files manually.
- Node dependencies in `Extension/package.json` use resolutions for known vulnerable sub-deps.
- CI runs CodeQL on every push/PR (see `.github/workflows/codeql-analysis.yml`).
- Pre-commit hooks enforce formatting, lint, and some secret scanning.
- **Required Additions** (add to backlog):
  - SLSA provenance for release artifacts.
  - Dependabot + automated PRs for lockfile updates with security review gate.
  - Cosign signatures on published Docker images.

See [docs/Build-Process.md](docs/Build-Process.md) for the full reproducible build procedure.

---

## 7. Security Audit Logging Requirements

Every security-relevant event **must** produce a structured log entry (JSON) with at minimum:

- `timestamp`, `event_type`, `severity`, `correlation_id`
- `actor` (human researcher, AI agent token ID, or "system")
- `action` (e.g., "browser.launch", "command.execute", "data.write", "extension.socket.open")
- `resource` (site URL or domain, profile path, storage backend)
- `outcome` (success/failure + error classification)
- `context` (BrowserId, command sequence hash, instrument flags)

Recommended events (non-exhaustive):
- TaskManager startup / shutdown with config digest
- BrowserManager process spawn + profile creation
- All `execute_command_sequence` (with command list hash)
- Extension socket connection established/closed
- Any navigation to a domain outside the current allow-list (even if blocked)
- Profile archive or data export operations
- Watchdog-triggered restarts or memory limit breaches
- Legacy JSON mutex file writes (temporary until removed)

Logs must be written to a separate append-only location or forwarded via syslog/Fluent Bit. Default retention: 90 days or project-specific DPIA requirement, whichever is longer.

---

## 8. Incident Response for Research Platforms

1. **Detection**: Watchdog, resource monitor, or manual review flags anomaly.
2. **Containment**: Immediate termination of affected browser processes + network isolation of the research VM.
3. **Forensic Collection**: Snapshot `datadir/`, browser profile, extension console logs, and all audit logs (preserve correlation IDs).
4. **Assessment**: Determine whether raw telemetry or derived profiles were exfiltrated or tampered.
5. **Notification**: Follow institutional data-breach protocol + notify any affected third parties if bid landscapes contain sensitive publisher data.
6. **Recovery**: Wipe and reprovision the research environment from known-good images. Rotate any S3/GCS credentials used.
7. **Post-Incident**: Update allow-lists, add new detection rules, and produce a redacted lessons-learned note for the research team.

A template playbook must be stored in `docs/incident-response.md` (to be created).

---

## 9. Security Gap Summary & Modernization Priorities

| Gap | Impact | Effort | Target Quarter |
|-----|--------|--------|----------------|
| Hardcoded paths + JSON mutexes in TrackerProject | Data loss, integrity, reproducibility | Medium | Q2 2026 |
| No encryption-at-rest or redaction | High (regulatory + re-id) | High | Q2 2026 |
| Legacy Dockerfiles & install scripts | Supply chain & container escape | Low | Q2 2026 |
| Insufficient security audit logging | Detection & forensics | Medium | Q3 2026 |
| No capability / allow-list enforcement at TaskManager | AI agent blast radius | High | Q3 2026 |
| Pickle IPC for errors | Latent deserialization | Low | Q2 2026 |
| Manifest V2 + unsafe-eval | Extension escape | High | 2026 H2 |
| Absence of SBOM + signed builds | Supply chain | Medium | Q2 2026 |

All P0 items above must be resolved or explicitly risk-accepted (with compensating controls) before the platform is used for any study that collects data on real users or production publisher properties.

---

## 10. References & Further Reading

- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [OWASP ASVS 4.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [NIST SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- OpenWPM upstream security documentation
- Existing project [docs/Security-and-Privacy.md](docs/Security-and-Privacy.md) (complementary threat model)

**Document Control**: This file is the authoritative hardening specification. All code changes, configuration defaults, and deployment patterns must be traceable to controls listed herein. Updates require security reviewer sign-off.

---

*End of Security Hardening Guide*
