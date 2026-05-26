# Deployment Guide

**HeaderBidding Research Platform**  
**Version**: 0.8.0-hb (research snapshot)  
**Date**: 2026-04

This guide describes how to run measurement workloads safely and repeatably. The current legacy stack makes "production" deployment inherently risky.

---

## 1. Deployment Tiers

| Tier | Isolation | Recommended For | Risk Level |
|------|-----------|------------------|------------|
| **Tier 0 – Local Dev** | Laptop + Docker | Prototyping only | Very High |
| **Tier 1 – Research VM** | Dedicated cloud VM, no inbound, strict egress | Pilot experiments | High |
| **Tier 2 – Hardened Research Cluster** | Kubernetes + network policies + dedicated storage | Production research runs | Medium (after Phase 1–2 hardening) |
| **Tier 3 – Modernized** | Current browser automation + proper orchestration | Long-term serious research | Target |

**Never** deploy the legacy version on any multi-tenant or internet-facing system.

---

## 2. Container Deployment (Current Best Practice)

### 2.1 Dockerfile Analysis

The provided `Dockerfile` and `Dockerfile-dev` copy the automation layer and run `install.sh`. They do **not** include TrackerProject by default and bake in the vulnerable Firefox 52.

**Improved pattern** (create `Dockerfile.hardened`):

```dockerfile
FROM ubuntu:18.04 AS builder
# ... (install build deps only)

FROM ubuntu:18.04
# Create non-root user
# Copy only what is needed
# Install security updates (as much as possible on old base)
# Copy research code
# Set strict umask, no shell history, etc.
USER research
ENTRYPOINT ["python", "-m", "hb_orchestrator"]
```

### 2.2 Runtime Flags (Mandatory)

```bash
docker run \
  --rm \
  --read-only \
  --security-opt no-new-privileges:true \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \   # only if truly needed
  --network=research-only \
  --pids-limit 200 \
  --memory 8g \
  --cpus 4 \
  -v /secure/research/results/2026-04-exp:/results:rw \
  -v /secure/research/config:/config:ro \
  -e HB_EXPERIMENT_ID=2026-04-exp-07 \
  -e RESULTS_ROOT=/results \
  headerbidding:legacy
```

---

## 3. Kubernetes / Orchestration Considerations

For serious scale:

- Use a dedicated node pool with taints.
- NetworkPolicy that denies all egress except to measurement targets + your result store.
- PersistentVolumeClaims with encryption at rest (LUKS or cloud KMS).
- Init containers that validate config (no hardcoded personal paths, no world-readable secrets).
- Sidecar for log shipping + security monitoring.
- CronJob or Argo Workflow for scheduled experiment batches.
- Never mount the Docker socket.

---

## 4. Secrets & Configuration Management

- Never bake S3 keys, researcher credentials, or block list signing keys into images.
- Use Kubernetes Secrets + SealedSecrets or external vault (HashiCorp, AWS Secrets Manager).
- Mount experiment definitions as ConfigMaps.
- All result paths must be driven by `HB_EXPERIMENT_ID` + `RESULTS_ROOT`.

---

## 5. Data Lifecycle in Deployment

1. **Ingestion** → Local encrypted volume or S3 with bucket policy + KMS + object lock.
2. **Processing** → Ephemeral analysis pods that receive only redacted/aggregated subsets.
3. **Archival** → Write-once object storage with retention tags.
4. **Deletion** → Cryptographic shred + object expiration + audit log entry.

Implement automated enforcement – do not rely on researchers remembering to `rm -rf`.

---

## 6. Monitoring & Alerting in Production Research Runs

- Crawl progress (sites completed / hour, bid yield rate).
- Resource saturation (memory pressure on old Firefox is the #1 cause of silent data loss).
- Security signals: unexpected outbound connections, large file writes, anomalous CPM distributions (possible site cloaking or data corruption).
- Cost tracking (especially cloud egress for S3 + browser instances).

---

## 7. Rollback & Reproducibility

Tag every experiment run with:

- Git SHA of the orchestrator
- Full `browser_params` + `manager_params` (persisted to DB)
- Container image digest
- Site list version / commit

This enables exact reproduction (within the limits of live web non-determinism).

---

## 8. Incident Response in Deployed Environments

See the IR section in [Security-and-Privacy.md](/mnt/5TB/git/headerbidding/docs/Security-and-Privacy.md). In deployment terms:

- Automated snapshot of the pod/VM disk on anomaly detection.
- Immediate network quarantine via security group / network policy change.
- Page the research data steward (not just the engineer who started the run).

---

**Related**: [Troubleshooting.md](/mnt/5TB/git/headerbidding/docs/Troubleshooting.md) for operational problems observed in real runs.
