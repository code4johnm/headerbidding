# Contributing Guidelines

**headerbidding: Header Bidding Research Platform**  
**Version**: 1.4.0  
**Date**: 2026-05-27T15:30:00Z  
**Full Path**: `docs/CONTRIBUTING.md`

---

## 1. Mission & Contribution Philosophy

This project exists to enable **responsible, ethical, and reproducible web measurement research**, with a current emphasis on the privacy and economic properties of header bidding and real-time advertising auctions.

All contributions must demonstrably advance one or more of the following:

- Security posture and hardening (per [docs/Security-Hardening.md](docs/Security-Hardening.md))
- Code quality, test coverage, and type safety
- Modernization (removal of legacy `TrackerProject/` risks, Docker modernization, etc.)
- Documentation clarity and completeness
- Research utility without increasing data sensitivity or host risk

**PRs that add features without corresponding security, testing, or documentation improvements will be closed without merge.**

---

## 2. Code of Conduct

All participants are expected to follow the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (Contributor Covenant). Violations may result in removal from the project.

---

## 3. Getting Started

1. Read [AGENTS.md](AGENTS.md) for build, test, and lint commands.
2. Read [README.md](README.md) (especially the security warning).
3. Read [docs/Security-Hardening.md](docs/Security-Hardening.md) and [docs/Architecture.md](docs/Architecture.md).
4. Fork the repository and create a topic branch from `master`.

---

## 4. Development Process

### 4.1 Branching & Commits

- Use descriptive branch names: `feature/js-instr-redaction`, `fix/legacy-paths-tracker`, `docs/security-hardening-update`.
- Commit messages must follow Conventional Commits (enforced by `commitlint`).
- Every commit that touches production code must include or reference tests.

### 4.2 Pre-commit & CI Requirements

All PRs must pass:
- `pre-commit run --all-files`
- Full relevant test matrix (or the fast subset for documentation-only changes)
- CodeQL scan with no new high/critical findings introduced by the PR

### 4.3 Security-Sensitive Changes

Any change that touches the following requires explicit security reviewer sign-off:

- Privileged Extension code (`Extension/bundled/privileged/`, manifest, background instruments)
- `openwpm/browser_manager.py`, `socket_interface.py`, `task_manager.py`
- Profile creation / Firefox preference handling
- Storage or data export paths
- Dockerfiles, install scripts, or CI workflows
- Any new dependency or build tool

Add the label `security-review-required` when opening such PRs.

---

## 5. Documentation Standards

- All new or changed user-facing behavior requires updates to the relevant doc under `docs/`.
- Use full relative paths when referencing other documents (e.g., `docs/Security-Hardening.md`).
- Mermaid diagrams are the preferred format for architecture visuals; keep them in sync with code.
- Update [AI-Agent-Context.md](docs/AI-Agent-Context.md) when adding new rules or constraints for AI coding agents.

---

## 6. Legacy Code Policy

The `TrackerProject/` directory contains known security and maintainability liabilities (hardcoded paths, JSON mutexes, outdated Python patterns).

**New code must not be added to `TrackerProject/`**. All new header-bidding or A/B experimentation logic must be implemented against the modern `openwpm/` API and will eventually live under a clean `openwpm/hb/` package.

Legacy fixes are welcome only when they reduce risk or unblock migration.

---

## 7. Pull Request Checklist (Maintainer Use)

Before merge, a maintainer will verify:

- [ ] Security impact assessed and documented
- [ ] Tests added or existing coverage maintained
- [ ] Documentation updated (including this file and AGENTS.md if commands changed)
- [ ] No new high/critical CodeQL findings
- [ ] pre-commit clean
- [ ] Changelog entry added (for user-visible or security changes)
- [ ] For security-sensitive PRs: explicit sign-off from a security reviewer

---

## 8. Release Process

Releases follow the checklist in `docs/Release-Checklist.md` (existing) and require:

- Security & architecture review sign-off
- Updated hardening status in Security-Hardening.md
- SBOM and provenance artifacts (when tooling is complete)

---

## 9. Recognition

Significant contributors (especially those who deliver meaningful security or modernization improvements) will be acknowledged in the changelog and release notes.

---

**Thank you for helping make web measurement research safer and more rigorous.**

*Full path*: `docs/CONTRIBUTING.md`
