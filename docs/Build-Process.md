# Build Process & Supply Chain Security

**headerbidding: Header Bidding Research Platform**  
**Version**: 1.4.0  
**Date**: 2026-05-27T20:00:00Z  
**Standards**: SLSA-inspired, NIST SSDF, OWASP Dependency-Track principles, reproducible builds.

**Full Path**: `docs/Build-Process.md`

---

## 1. Overview

This document defines the authoritative, reproducible, and security-hardened build process for the platform. All official artifacts (conda environments, browser extension XPI, Docker images, test fixtures) **must** be produced via the procedures below.

The build system spans:
- Python/conda environment (modern `environment.yaml` + `scripts/repin.sh`)
- TypeScript WebExtension (`Extension/`)
- Firefox profile & geckodriver installation (via install scripts)
- Container images
- Documentation & schema rendering

---

## 2. Prerequisites for Reproducible Builds

- Ubuntu 22.04 LTS or macOS 14+ (build host)
- Conda (Miniforge recommended)
- Node.js >= 22 (for Extension, see `Extension/package.json` engines)
- Docker (for containerized builds)
- `pre-commit` installed

Never build on untrusted or multi-tenant hosts.

---

## 3. Python Environment & Dependency Pinning

**Primary Source of Truth**: `environment.yaml` (top level)

**Pinning & Update Process** (mandatory):

```bash
# 1. Make changes to unpinned specs if needed
$EDITOR scripts/environment-unpinned.yaml

# 2. Regenerate fully pinned environment (never edit environment.yaml manually)
./scripts/repin.sh

# 3. Commit both the unpinned source and the new pinned environment.yaml + lock artifacts
git add environment.yaml scripts/environment-unpinned*.yaml
```

**Security Requirements**:
- All packages must come from the official conda-forge channel.
- After repinning, run full test matrix before merging.
- Maintain an SBOM (CycloneDX) for the resolved environment (tooling to be added in Phase 1).

---

## 4. WebExtension Build (TypeScript)

**Location**: `Extension/`

**Commands** (from AGENTS.md and package.json):

```bash
cd Extension
npm ci                  # exact lockfile (package-lock.json)
npm run build           # tsc + webpack + web-ext build
# Produces: dist/openwpm-1.0.zip and openwpm.xpi (copied in postbuild)
```

**Security Controls** (enforced in CI):
- `npm run lint` includes `web-ext lint --privileged`
- ESLint with `@microsoft/eslint-plugin-sdl` and `eslint-plugin-mozilla`
- Prettier + TypeScript strict compilation
- No direct `eval` or `new Function` outside explicitly justified instrumentation code

**Output Artifact**: `openwpm.xpi` (signed via web-ext or manual AMO signing for distribution).

**Rebuild Trigger**: Any change under `Extension/src/` or `Extension/bundled/`.

---

## 5. Full Platform Installation

```bash
# Clean research workstation or CI
./install.sh                 # Creates "openwpm" conda env, installs Firefox, builds extension
./install-dev.sh             # Adds test & dev tooling

# Verify
conda activate openwpm
python -c "import openwpm; print(openwpm.__file__)"
python -m pytest --collect-only -q | head -5
```

The install scripts also handle geckodriver and legacy Firefox profile setup. They are being modernized (see gaps).

---

## 6. Container Builds

**Primary Dockerfiles**:
- `Dockerfile` – base runtime image
- `Dockerfile-dev` – adds tests & dev tools

**Current State**: References legacy `automation/` paths and requires updates for the modern layout (`openwpm/`, `Extension/`).

**Hardened Build Procedure (Target)**:

```bash
# Multi-stage, non-root, pinned base
docker build --target runtime -t headerbidding:0.8.0-hb --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) .

# Attestation (future)
cosign sign --yes headerbidding:0.8.0-hb
```

**Required Improvements** (see Security-Hardening.md):
- Remove `passwordless sudo`
- Use distroless or hardened base images where possible
- Run as non-root UID
- Multi-stage to discard build tools

See `.github/workflows/build-container.yaml` for the current container CI job.

---

## 7. CI / CD Security Pipeline (`.github/workflows/`)

| Workflow | Purpose | Security Features |
|----------|---------|-------------------|
| `run-tests.yaml` | Full pytest matrix + pre-commit + demo | Codecov upload (token required), junit summary, 7-way parallelization |
| `codeql-analysis.yml` | SAST (Python + JS/TS) | Runs on push/PR/schedule; results in GitHub Security tab |
| `build-container.yaml` | Docker image publication | Triggered on release/tags |

**Mandatory Gates** (enforced):
- pre-commit (black, isort, mypy, eslint, prettier, markdownlint)
- All tests green (including slow-marked where scheduled)
- CodeQL no new high/critical findings on PRs

**Supply Chain**:
- `actions/cache` for conda to reduce external fetches
- `actions/checkout@v4` (pinned)
- Dependabot recommended for all action pins

---

## 8. Documentation & Schema Rendering

```bash
# From root (requires Node deps)
npm run render_schema_docs   # Generates docs/schemas/*.md from schemas/*.json
npm run validate_markdown_links
npm run lint_markdown
```

These steps are part of the release checklist.

---

## 9. Artifact Inventory & Provenance (Target State)

| Artifact | Format | Signing / Attestation | Storage |
|----------|--------|-----------------------|---------|
| WebExtension XPI | `.xpi` | web-ext or AMO | GitHub Releases |
| Conda env spec | `environment.yaml` | Git commit + tag | Repository |
| Docker image | OCI | cosign (SLSA) | GHCR / internal registry |
| SBOM | CycloneDX JSON | Attached to image | Dependency-Track |
| Test results | JUnit XML + coverage | — | Codecov + artifacts |

Until SLSA provenance and image signing are implemented, all releases carry the explicit disclaimer in the README.

---

## 10. Known Build Gaps & Remediation

1. Dockerfiles reference obsolete `automation/` directory and old Ubuntu 18.04 base.
2. No automated SBOM generation in current CI.
3. `install.sh` still carries legacy Firefox 52 ESR paths in comments and some branches.
4. No reproducible build attestation or build-user isolation in container jobs.

These are tracked in the modernization roadmap (Security-Hardening.md §9).

---

**All builds must be traceable to a specific git commit and produce bit-for-bit identical artifacts on equivalent clean hosts.**

*End of Build Process document*
