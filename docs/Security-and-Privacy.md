# Security and Privacy

**HeaderBidding Research Platform – Security, Privacy & Compliance Guidance**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-05-27T15:30:00Z
**Classification**: Public (with controlled disclosure for security issues)

**Standards Alignment**: OWASP Top 10 (2021), OWASP ASVS 4.0, NIST Cybersecurity Framework (Identify/Protect/Detect/Respond/Recover), Secure Software Development Lifecycle (SSDL), IAB Tech Lab guidelines for measurement, GDPR/CCPA/ePrivacy research considerations.

---

## 1. Executive Risk Statement

The HeaderBidding platform is a **high-risk research tool** that:

- Executes arbitrary web content in instrumented browsers.
- Extracts and persists extremely sensitive data: full HTTP POST bodies, JavaScript execution traces, third-party cookies, and real-time bidding telemetry (including precise CPM values and bidder participation that can enable re-identification and interest profiling).
- Runs on a severely outdated browser stack (Firefox 52 ESR + deprecated Add-on SDK).

**Current overall security posture: POOR.**  
The platform in its present form violates multiple OWASP Top 10 categories and is unsuitable for use outside tightly controlled, low-volume academic environments without remediation.

**Mandatory Prerequisites Before Any Use**:
- Formal ethics/IRB approval and legal review.
- Isolated research infrastructure with no access to production networks or credentials.
- Data Protection Impact Assessment (DPIA) for any personal or pseudonymous data.
- Explicit, documented retention and deletion schedule.

---

## 2. Threat Model (STRIDE + Ad-Tech Specific)

### Primary Assets
1. Raw telemetry (HTTP/JS/cookies/bids) containing or derivable into PII or sensitive categories (health, finance, adult, political).
2. Inferred user interest profiles from the ML pipeline.
3. Publisher revenue signals (CPM distributions per site + blocking profile).
4. The researcher's local machine / research cluster (via browser 0-days or extension escape).
5. Reproducibility artifacts (crawl configs, block lists, custom uBlock rules).

### Threat Actors
- **External malicious sites** (drive-by, malvertising, exploit kits).
- **Third-party bidders / ad networks** (supply-side platforms observing measurement behavior).
- **Insider / researcher error** (accidental data exfiltration, over-collection).
- **Nation-state or sophisticated tracker** (fingerprinting the measurement infrastructure itself).
- **Data breach** after collection (bid landscapes + profile CSVs are high-value for de-anonymization).

### STRIDE Mapping (Selected High-Severity Items)

| Category | Risk Example in This Codebase | OWASP Top 10 / ASVS Mapping | Severity |
|----------|-------------------------------|-----------------------------|----------|
| **Spoofing** | Malicious site spoofs `pbjs` global or injects fake bids | A07:2021 – Identification and Authentication Failures | High |
| **Tampering** | Attacker modifies bid JSON or `testingDone.json` mutex files via shared FS | A08:2021 – Software and Data Integrity Failures | High |
| **Repudiation** | No signed/attested crawl logs or bid records; easy for researcher to fabricate results | ASVS 7.2.1 – Audit logging | Medium |
| **Information Disclosure** | Full POST bodies + bid CPMS + cookies written to disk/S3 without classification or encryption at rest | A02:2021 – Cryptographic Failures + A04:2021 – Insecure Design | **Critical** |
| **Denial of Service** | Runaway memory in old Firefox; unbounded queue in DataAggregator; malicious site causing infinite redirects | A10:2021 – Server-Side Request Forgery + Resource Exhaustion | Medium |
| **Elevation of Privilege** | Old geckodriver/Firefox sandbox escape; privileged extension escape | A01:2021 – Broken Access Control | **Critical** |

**Ad-Tech Specific Risks**:
- **Consent & Purpose Limitation**: Collecting bid data at scale without transparency signals or consent strings may violate ePrivacy Directive / GDPR Art. 5-6.
- **Special Category Data Inference**: Bid patterns on health/Adult/Finance verticals can infer protected attributes.
- **RTB Transparency Failures**: The platform itself becomes an opaque observer in the auction chain.
- **Downstream Misuse**: Bid datasets can be used for competitive intelligence or more precise targeting.

---

## 3. OWASP Top 10 (2021) – Current State Assessment

| # | Category | Status in Codebase | Evidence / Location |
|---|----------|--------------------|---------------------|
| A01 | Broken Access Control | Poor | File-based mutexes (`writing.json`) have no auth; any local process can tamper. No allow-list validation on sites. |
| A02 | Cryptographic Failures | Poor | No encryption at rest for SQLite/Parquet/JSON bid files. No hashing of sensitive identifiers. Hardcoded paths leak env. |
| A03 | Injection | Poor | `execute_script` runs researcher-controlled but page-influenced strings. Broad `except` swallowing. SQL via aggregators not parameterized in all paths (legacy LevelDB/plyvel usage). |
| A04 | Insecure Design | Critical | Architecture trusts page content (`pbjs` objects), uses JSON files for coordination, ships ancient vulnerable browser. |
| A05 | Security Misconfiguration | Critical | Default `browser_params` enable instruments with no redaction. Firefox 52 + no security headers enforcement on research infra. |
| A06 | Vulnerable & Outdated Components | **Critical** | Firefox 52 (hundreds of CVEs), Selenium <3.7, geckodriver 0.15, Add-on SDK (EOL 2017), Python 2 remnants. |
| A07 | Identification & Auth Failures | N/A (non-web app) | But relevant for any future web dashboard or S3 access (no assumed roles enforced in examples). |
| A08 | Software & Data Integrity Failures | Poor | No SBOM, no dependency pinning with hashes (`requirements.txt` uses unpinned ranges in places), no code signing. |
| A09 | Security Logging & Monitoring Failures | Poor | HBLogger is basic; no security events (failed commands, anomalous memory, bid anomalies) are specially logged or alerted. |
| A10 | Server-Side Request Forgery (SSRF) | Medium | Browser is an SSRF proxy by design. No outbound proxy enforcement, no destination allow-list in core. |

**Conclusion**: The platform currently fails or is at high risk for **at least 6 of the 10** OWASP categories in production-grade terms.

---

## 4. NIST Cybersecurity Framework Alignment

**Identify**:
- Asset inventory: incomplete (no automated discovery of installed extensions or custom block lists).
- Risk assessment: this document is the first comprehensive one.
- Data flow mapping: partial (see Architecture.md).

**Protect**:
- Access control: weak (local FS trust).
- Data security: absent (no classification, encryption, DLP).
- Protective technology: relies on outdated Firefox sandbox.

**Detect**:
- Anomaly detection: none (memory watchdog exists but no behavioral baselining of bid patterns or network).
- Logging: present but not security-focused.

**Respond / Recover**:
- No documented incident response plan for data breach of bid profiles.
- No automated backup + verified restore for research datasets.

**Recommendation**: Map future work to the NIST CSF Functions and create a living Risk Register.

---

## 5. Secure Software Development Lifecycle (SSDL) Gaps

Current state does **not** follow a modern SSDL:

- No threat modeling (first iteration is this document).
- No secure design review.
- Minimal static analysis (only basic flake8 on core; TrackerProject largely unchecked).
- No dependency vulnerability scanning in CI (none exists).
- No dynamic application security testing (DAST) harness for the crawler.
- No software bill of materials (SBOM) generation.
- Code review is informal.
- No security champions or dedicated security role.

**Required SSDL Artifacts to Produce**:
1. Threat model (STRIDE + data flow diagrams) – this doc + Architecture.md are starting point.
2. Security requirements backlog (mapped to ASVS Level 2+).
3. Automated SCA + SAST pipeline.
4. Container image scanning (Trivy/Grype) + signed images.
5. Data classification matrix for all collected fields (especially `post_body`, `javascript.value`, `cpm` + bidder combinations).

---

## 6. Privacy Engineering Considerations (GDPR / CCPA / ePrivacy)

**Lawful Basis**: Research under GDPR Art. 6(1)(f) or Art. 89 (research exemption) may apply, **but** requires balancing test and safeguards.

**High-Risk Processing**:
- Large scale.
- Systematic monitoring.
- Special categories potentially inferred.
- Automated decision-making / profiling (ML component).

**Required Mitigations** (minimum):
- Data minimization: instrument only what is strictly necessary for the research question.
- Pseudonymization / hashing of high-entropy identifiers (e.g., `adId`, certain cookie values) at ingestion.
- Differential privacy or k-anonymity on aggregated bid reports and profiles before publication.
- Strict purpose limitation: no reuse of datasets for training production bidding models.
- Right to erasure / data portability support plan (even for research data).
- DPIA published (redacted) alongside any public dataset release.
- Transparency: publish high-level methodology and data handling summary.

**uBlock / Tracker Blocking Lists**: These constitute security tooling. Tampering or distribution must be handled carefully to avoid supply-chain attacks on the research community.

---

## 7. Hardening Roadmap (Prioritized)

### Phase 0 – Immediate Containment (Do Before Any New Crawl)
- [ ] Run exclusively inside Docker/Podman with `--security-opt no-new-privileges` + seccomp + AppArmor.
- [ ] Replace all hardcoded `~/...` and `/mnt/hgfs/...` paths with environment variables + config files.
- [ ] Add site allow-list validation in `TrainingCrawl` and `getSitesToVisit`.
- [ ] Disable or heavily restrict `save_all_content`, `post_body` capture unless explicitly justified per experiment.
- [ ] Implement basic PII redaction (email, phone, national ID regexes) on all exported records before writing to disk/S3.

### Phase 1 – Browser & Instrumentation Modernization (Highest Impact)
- [ ] Migrate from Firefox 52 + Add-on SDK to current Firefox ESR + WebExtensions + CDP or Playwright.
- [ ] Replace `execute_script` bid harvesting with trusted CDP Runtime/Debugger instrumentation where possible.
- [ ] Remove or sandbox the privileged extension entirely.

### Phase 2 – Architecture & Data Protection
- [ ] Replace JSON mutex files with a proper task queue (Redis + RQ/Celery) + PostgreSQL state.
- [ ] Add field-level encryption for sensitive columns (`post_body`, high-entropy `value` fields, raw bid objects).
- [ ] Implement structured logging with security context (OpenTelemetry + ECS).
- [ ] Add automated retention enforcement + cryptographic shredding on deletion.
- [ ] Introduce SBOM generation (`cyclonedx-python`) and dependency pinning with `pip-tools` + hash verification.

### Phase 3 – Governance & Compliance
- [ ] Formal threat model document + annual review.
- [ ] Security requirements traceability matrix (ASVS).
- [ ] Penetration test of the research harness (focus on extension escape, data exfil paths).
- [ ] Publish Data Handling & Retention Policy + DPIA template.
- [ ] Add security.txt and vulnerability disclosure policy.

---

## 8. Incident Response & Breach Notification (Research Context)

1. **Detection**: Monitor for anomalous memory usage, unexpected bid volume spikes, or large outbound transfers from the research host.
2. **Containment**: Immediately isolate the affected container/VM; revoke any S3 credentials; snapshot disk for forensics.
3. **Assessment**: Classify whether raw PII or high-entropy bid profiles were exposed.
4. **Notification**: Follow institutional policy + applicable law (GDPR 72h for supervisory authority if personal data).
5. **Lessons Learned**: Update this document and the risk register.

**Never** attempt to "fix" a breach by silently deleting data without audit trail.

---

## 9. Vulnerability Disclosure

This repository follows **coordinated disclosure**.

- For security issues that do **not** involve active exploitation of the research platform itself, open a private GitHub Security Advisory or email the maintainers.
- For issues in the **bundled ancient browser / geckodriver / extension**, treat them as known (they are) and focus remediation on modernization rather than reporting to Mozilla.
- Do **not** publish exploit details or full bid datasets from vulnerable instances without redaction and responsible handling.

---

## 10. References

- OWASP Top 10 2021: https://owasp.org/Top10/
- OWASP Application Security Verification Standard (ASVS) 4.0
- NIST Cybersecurity Framework 2.0
- IAB Tech Lab: OpenRTB, AdCOM, Privacy & Data Use standards
- GDPR Articles 5, 6, 9, 25, 32, 89 + Recital 157 (research)
- "The Ad-Tech Surveillance Industrial Complex" and related academic literature on RTB privacy risks
- Mozilla WebExtensions & CDP documentation (modern replacement paths)

---

**This document must be reviewed and updated at least annually or after any significant architectural change or security incident.**

**Next Steps for Readers**: Proceed to [Deployment.md](docs/Deployment.md) for concrete hardened deployment patterns, then [Development.md](docs/Development.md) for secure coding practices required for contributions.
