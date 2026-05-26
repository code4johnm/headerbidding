# AI-Agent-Context.md

**hb-update: Header Bidding Research Platform**  
**Version**: 1.1.0  
**Date**: 2026-04-26  
**Purpose**: Primary machine-readable and human-readable context file for AI coding agents, LLMs, and autonomous research tools interacting with this repository.  
**Full Path**: `docs/AI-Agent-Context.md`

**This file takes precedence over AGENTS.md for all security, permission, and AI-agent-specific rules. AGENTS.md remains the operational command reference.**

---

## 1. Project Identity & Constraints

- **Name**: hb-update (Header Bidding Research Platform modernization of OpenWPM)
- **Core Nature**: High-privilege web measurement and ad-tech telemetry platform. Not a general web application, not an AI system itself.
- **Primary Risk**: The privileged Firefox WebExtension (`Extension/`) combined with the ability to execute arbitrary researcher or page-influenced JavaScript in a high-privilege context.
- **Current State**: Hybrid — modern `openwpm/` + TypeScript Extension core + legacy `TrackerProject/` with known liabilities.
- **AI Agent Mandate**: All work performed by AI agents must **reduce** overall security risk, improve auditability, or advance safe modernization. Agents must never increase the attack surface or data sensitivity.

---

## 2. Absolute Rules for AI Coding Agents (Never Violate)

1. **Never** add, modify, or suggest code that weakens the privileged extension permission model, removes `web-ext lint --privileged`, or adds new `experiment_apis` without explicit written justification in the PR and Security-Hardening.md.
2. **Never** introduce new uses of `pickle` for cross-process or network data (exception transport is the only current exception and must be replaced per roadmap).
3. **Never** hardcode researcher-specific absolute paths (especially anything resembling `/home/johncook` or personal home directories).
4. **Never** relax validation, allow-list enforcement, or redaction requirements around `execute_script`, `run_custom_function`, or bid harvesting logic.
5. **Never** modify `manifest.json` permissions or CSP without also updating Security-Hardening.md §3 and obtaining security reviewer sign-off in the PR.
6. **Never** commit changes that would cause an AI-orchestrated crawl to bypass intended destination controls or capability tokens (once implemented).
7. **Always** treat raw HTTP bodies, JS call stacks, and bid CPM data as highly sensitive. Any new code handling this data must include classification or redaction hooks.
8. **Always** run `pre-commit run --all-files` and relevant tests before proposing a final diff.
9. **Always** update this file (AI-Agent-Context.md), AGENTS.md, and the relevant `docs/` file when behavior, commands, or security assumptions change.
10. **Always** use clean repository-relative paths (e.g. `docs/Security-Hardening.md`, `README.md`, `openwpm/config.py`) when referencing files in documentation, code comments, or new documents. Never use machine-specific absolute paths.

---

## 3. Allowed vs. Forbidden Operations

### 3.1 Strongly Encouraged (High Value)

- Adding or improving typed dataclasses and validation in `openwpm/config.py`.
- Implementing capability token / allow-list enforcement at the TaskManager entry point.
- Building the redaction / classification pipeline for telemetry before storage or LLM handoff.
- Replacing legacy JSON mutex coordination with proper typed state machines.
- Adding structured security audit logging (see Security-Hardening.md §7).
- Modernizing Dockerfiles to non-root, pinned, multi-stage, attested builds.
- Generating and enforcing SBOMs in CI.
- Writing tests that specifically exercise security boundaries and failure modes (injection, path traversal, socket abuse, etc.).

### 3.2 Permitted with Documentation

- Changes to JS instrumentation settings or collections — must update schema docs and note data sensitivity impact.
- Work on `TrackerProject/` — only when the change reduces risk or clearly documents the migration path. New HB features belong in the modern core.
- Updates to privileged extension APIs — require corresponding updates to manifest justification, threat model, and hardening guide.

### 3.3 Strictly Forbidden Without Prior Security Review

- Broadening `<all_urls>`, `webRequestBlocking`, or any permission in the extension manifest.
- Adding new custom privileged experiment APIs.
- Using `eval`, `new Function`, or dynamic code generation outside the narrow, already-justified instrumentation paths.
- Changing subprocess invocation of geckodriver/Firefox without containment improvements.
- Disabling or weakening any pre-commit hook or CodeQL query.
- Introducing long-lived cloud credentials into Dockerfiles, scripts, or examples.

---

## 4. Security Context for AI Agents Using the Platform

When an external AI/LLM agent will orchestrate crawls using this platform (site selection, command generation, result interpretation):

- The AI agent **must** operate under an explicit capability token / signed task manifest (design to be implemented).
- All sites must come from a pre-approved, versioned allow-list. The AI may never generate raw URLs that bypass validation.
- Raw telemetry must **never** be fed directly to an LLM without passing through the redaction pipeline.
- Any generated JavaScript intended for `execute_script` must undergo static analysis + sandbox execution before being accepted.
- The AI agent itself must be treated as an untrusted actor from the perspective of the TaskManager.

See [docs/Security-Hardening.md](docs/Security-Hardening.md) §4 for the full AI orchestration security architecture.

---

## 5. File & Directory Guidance for Agents

**Modern Core (Primary Focus)**:
- `openwpm/` — Python orchestration, commands, storage, config
- `Extension/src/` — TypeScript instruments and background
- `Extension/bundled/privileged/` — Security-critical IPC and stack dump code
- `schemas/` — JSON schemas (keep in sync with code)
- `.github/workflows/` — CI security gates

**Legacy (Approach with Extreme Caution)**:
- `TrackerProject/` — Known issues (paths, races, old patterns). Document migration or risk reduction in every change.

**Documentation (Must Stay Consistent)**:
- `docs/Architecture.md`
- `docs/Security-Hardening.md`
- This file and `AGENTS.md`

**Never edit**:
- Test fixtures (`test/profile.tar.gz`) except via documented restore procedures.
- Pinned dependency files without using the official `repin.sh` workflow.

---

## 6. Testing & Verification Mandates for AI Changes

Before any AI-proposed change is considered complete:

1. All new or modified Python code must pass `mypy openwpm` (strict mode where not explicitly overridden).
2. All new or modified Extension code must pass `npm run lint` inside `Extension/`.
3. Relevant browser instrumentation tests (`pytest -k "js_instrument or http or cookie"`) must pass.
4. Any change touching data flows must include or update a test that validates schema, redaction, or logging behavior.
5. Documentation changes must pass `npm run lint_markdown` and link validation where applicable.

---

## 7. Context for Specific High-Risk Areas

**Privileged Extension**:
- Treat every line in `privileged/sockets/api.js`, `profileDirIO/`, and `stackDump/` as security-sensitive.
- The binary socket protocol is a trust boundary. Changes require protocol version bumps and tests.

**Data Handling**:
- Assume every record written to Parquet/SQLite/JSON may eventually be subject to regulatory or adversarial scrutiny.
- Prefer one-way hashing or structural metadata over raw values when the research question permits.

**AI Agent Integration Code** (future):
- Any new module under `openwpm/hb/` or `openwpm/agent/` must default to deny-all and require explicit capability presentation.

---

## 8. Self-Update & Consistency Rule

Any AI agent that modifies this repository **must** also propose updates to this `AI-Agent-Context.md` file reflecting new constraints, allowed operations, or architectural decisions. Failure to keep this file accurate is itself a policy violation.

---

## 9. Contact & Escalation for AI Agents

When an AI coding agent encounters ambiguity that touches security boundaries, privileged code, data sensitivity, or AI orchestration patterns, it must:

1. Stop and document the ambiguity.
2. Reference the exact lines/files in question.
3. Propose the most conservative (least-privilege, highest-audit) interpretation.
4. Ask the human maintainer for explicit guidance before proceeding.

**Preferred citation format in agent reasoning**: "Per AI-Agent-Context.md §2 rule #N and Security-Hardening.md §X..."

---

**This document is the single source of truth for AI agent behavior on this codebase. It is intentionally stricter than typical open-source contribution guides because of the intrinsic power and sensitivity of the platform.**

*End of AI-Agent-Context.md*
