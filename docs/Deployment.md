# Deployment Guide

**headerbidding: Header Bidding Research Platform**  
**Version**: 1.3.0  
**Date**: 2026-05-27T02:47:30Z  
**Full Path**: `docs/Deployment.md`

---

## 1. Deployment Principles

All deployments **must** follow Zero Trust and least-privilege principles as defined in [Security-Hardening.md](docs/Security-Hardening.md).

**Never** deploy this platform on:
- Personal developer laptops with production credentials
- Multi-tenant shared infrastructure without strong namespace isolation
- Public cloud VMs with default egress

**Recommended Tiers**:
1. **Development** – Local hardened workstation or dev cluster namespace
2. **Research Production** – Dedicated Kubernetes cluster or air-gapped hardware with egress proxy
3. **High-Sensitivity / Regulatory** – Air-gapped with measured boot and confidential computing

---

## 2. Local Hardened Workstation

### Minimum Controls
- Full-disk encryption (LUKS/FileVault)
- Dedicated non-root user (`researcher`)
- `data_directory` on a separate encrypted volume or LUKS container
- Egress forced through a local allow-list proxy (e.g., mitmproxy with block list or tinyproxy)
- Browser launched in `xvfb` or headless mode for most runs

### Quick Commands
```bash
# Recommended local invocation
mkdir -p /secure/research/hb-2026-Q2/datadir
chmod 0700 /secure/research/hb-2026-Q2/datadir

python -m openwpm.task_manager ...  # or via your experiment script
```

---

## 3. Docker Deployment (Current & Target)

**Current Dockerfiles** (`Dockerfile`, `Dockerfile-dev`) are legacy and reference the old `automation/` layout. They must be updated before trusted use.

**Target Hardened Dockerfile Pattern** (to be implemented):

```dockerfile
# syntax=docker/dockerfile:1.7
FROM ubuntu:22.04 AS base

# Create non-root user early
RUN useradd -m -u 10001 -s /bin/bash researcher && \
    mkdir -p /opt/headerbidding && chown researcher:researcher /opt/headerbidding

WORKDIR /opt/headerbidding
USER researcher

# Copy only what is needed (after modernized install)
COPY --chown=researcher:researcher openwpm/ openwpm/
COPY --chown=researcher:researcher Extension/ Extension/
# ... minimal set

# Install with --no-root escalation
RUN ./scripts/install-modern.sh --non-interactive

# Drop all capabilities
USER 10001
```

Run with:
```bash
docker run --rm \
  --security-opt no-new-privileges:true \
  --cap-drop=ALL \
  --network=research-net \
  -v /secure/research/datadir:/datadir:ro \
  headerbidding:0.8.0-hb \
  python -m your_experiment --headless
```

---

## 4. Kubernetes Deployment (Recommended)

### Namespace Isolation
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hb-research
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

### NetworkPolicy (Mandatory)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hb-egress-only
  namespace: hb-research
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: research-proxy
    ports:
    - protocol: TCP
      port: 8080   # proxy
  - to:
    - namespaceSelector:
        matchLabels:
          name: storage
    ports:
    - protocol: TCP
      port: 443
```

### TaskManager Job Example (Skeleton)
- One Job per experiment
- `securityContext.runAsNonRoot: true`
- `readOnlyRootFilesystem: true` (with emptyDir for scratch)
- Resource limits (memory especially important due to browser bloat)
- Init container to inject signed allow-list and capability token

---

## 5. Air-Gapped & High-Security Deployments

1. Export signed allow-list JSON and site seeds via one-way diode or signed USB.
2. Import only redacted aggregate results.
3. No S3/GCS; all storage on encrypted local volumes or approved offline NAS.
4. Measured boot / TPM attestation of the research image.
5. Physical or virtual air-gap with strict change control.

---

## 6. Egress Proxy (Non-Negotiable in All Networked Deployments)

The platform **must** be deployed behind an allow-listing, logging proxy.

Recommended implementations:
- mitmproxy in upstream mode with custom block script
- Squid with url_rewrite_program + logging
- Cloudflare Gateway or corporate secure web gateway (for institutional use)

All browser traffic (including the privileged extension sockets if they ever leave localhost) must be forced through this proxy via PAC or container network rules.

---

## 7. Monitoring & Observability in Production Research

- Prometheus + Grafana for browser process resource usage
- Centralized logging of the structured security events defined in Security-Hardening.md §7
- Automatic alerting on memory anomalies, unexpected external domains, or watchdog restarts

---

## 8. Rollback & Reprovisioning

Research environments must be treated as ephemeral. After any suspected incident or at the end of a major study:
1. Terminate all browser processes
2. Wipe `data_directory` (secure delete if required by DPIA)
3. Reprovision from a known-good, version-pinned image or git commit + `install.sh`
4. Rotate any cloud credentials used

---

**Deployment without the controls in Security-Hardening.md §5 is a policy violation.**

*Full path*: `docs/Deployment.md`
