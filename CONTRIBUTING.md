# Contributing to HeaderBidding

**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-04

Thank you for your interest in improving research tooling for understanding the privacy, security, and economic properties of header bidding and real-time advertising.

---

## Code of Conduct

- Be respectful, collaborative, and precise.
- Security and ethics discussions take priority over feature velocity.
- Acknowledge that this platform collects extremely sensitive data; treat every proposed change with corresponding seriousness.

---

## How to Contribute

### 1. Start with an Issue

Before writing significant code:

- Open an issue labeled `modernization`, `security`, `hb-experiment`, `documentation`, or `bug`.
- For large efforts, link to or attach a short design note (architecture impact, threat model delta, data minimization analysis).
- Wait for maintainer feedback before investing large amounts of time.

### 2. Development Setup

See [docs/Development.md](docs/Development.md) and [docs/Installation-Guide.md](docs/Installation-Guide.md).

**Mandatory first step for any non-trivial contribution**: Eliminate or abstract at least one instance of the hardcoded researcher paths (`/home/johncook/headerBidding` or `/mnt/hgfs`).

### 3. Pull Request Checklist

- [ ] The change is accompanied by updates to the relevant document(s) in `docs/`.
- [ ] New code follows the style in `setup.cfg` (black, isort, flake8) and includes type hints.
- [ ] Security and privacy impact has been explicitly considered and documented in the PR description.
- [ ] No new hardcoded personal paths or secrets.
- [ ] Tests (even minimal smoke tests) are included or a clear explanation of why they are not feasible is provided.
- [ ] The PR does not increase data collection surface without a corresponding justification and minimization strategy.

### 4. Commit Hygiene

- Prefer small, reviewable PRs.
- Reference issues (`Closes #42`).
- Include before/after behavior for bug fixes.
- For security-relevant changes, follow the disclosure policy in [SECURITY.md](SECURITY.md).

---

## Areas Where Contributions Are Especially Valuable

1. **Path & Configuration Abstraction** – The highest-ROI, lowest-risk improvement.
2. **Modern Instrumentation Layer** – Prototypes that replace the Firefox 52 + extension with Playwright + CDP or current WebExtensions + BiDi.
3. **Robust Experiment Orchestration** – Replacing the JSON mutex anti-pattern with a real task queue + state store.
4. **Data Protection Primitives** – PII redaction, field encryption helpers, retention enforcement.
5. **Documentation & Threat Modeling** – Keeping the professional docs accurate and actionable.
6. **Testing Infrastructure** – Especially integration tests that can run in CI against a controlled fixture.

**Low-value contributions** (likely to be declined or heavily reworked):
- Adding more instruments or data collection points without minimization analysis.
- Cosmetic or "cleanup" changes that do not address the documented architectural and security debt.
- New ML models on top of the existing brittle data pipeline.

---

## Governance & Review

- Security and ethics-related PRs require explicit sign-off from at least one maintainer familiar with the threat model.
- Large modernization efforts may be developed on a branch or fork until they reach a mergeable state.
- Documentation PRs are held to the same standard as code.

---

## Recognition

Significant contributors will be acknowledged in a `CONTRIBUTORS` file or release notes. Academic users are encouraged to cite both the original OpenWPM work and any specific improvements they rely on.

---

## Questions?

Open a GitHub Discussion or issue with the `question` label. For sensitive topics, use the security reporting channel described in [SECURITY.md](SECURITY.md).

---

**We particularly welcome contributions that make this platform safer and more reproducible for future researchers studying the ad-tech ecosystem.**
