# Installation Guide

**HeaderBidding Research Platform**  
**Version**: 1.5.0  
**Date**: 2026-05-27T15:30:00Z

**WARNING (Historical)**: Older versions of this project deployed Firefox 52 ESR. The primary installation paths have been modernized (Firefox 150+ via `scripts/install-firefox.sh` + conda `environment.yaml`). Legacy scripts still exist for reference but should not be used for new work. See the updated `install.sh` and [docs/Security-Hardening.md](docs/Security-Hardening.md).

---

## 1. Supported Environments (Current State)

| Environment          | Status          | Notes |
|----------------------|-----------------|-------|
| Ubuntu 22.04+ / 24.04 | Recommended    | Use `environment.yaml` + `scripts/install-firefox.sh` |
| Docker (ubuntu:24.04) | Recommended    | Modernized Dockerfile (see root Dockerfile) |
| macOS                | Supported      | `scripts/install-firefox.sh` (cross-platform) |
| Python 3.12+         | Supported      | Primary path via conda `environment.yaml` |
| Firefox 150+         | Required       | Matches Extension manifest `strict_min_version` |

**Strong Recommendation**: Perform all work inside Docker or a dedicated VM. Never install the legacy browser stack on a daily driver machine.

---

## 2. Quick Docker Installation (Recommended Containment)

```bash
git clone <repo-url> headerbidding
cd headerbidding

# Build the research image (contains the vulnerable stack – isolate accordingly)
docker build -t headerbidding:legacy -f Dockerfile .

# Run with strong isolation
docker run --rm -it \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  --network research-net \
  -v $(pwd)/results:/opt/OpenWPM/results \
  headerbidding:legacy \
  python demo.py
```

See [Deployment.md](docs/Deployment.md) for production-grade container hardening and Kubernetes patterns.

---

## 3. Bare-Metal / VM Installation (Legacy Path)

```bash
git clone <repo-url>
cd headerbidding

# Review the script first – it will add Canonical partner repos and download Firefox 52
less install.sh

# Non-interactive (recommended)
./install.sh --no-flash
```

The script performs:

1. System package installation (build tools, LevelDB, libjpeg, etc.).
2. pip + `requirements.txt`.
3. Download of a specific ancient Firefox ESR tarball.
4. geckodriver 0.15.0 placement inside `firefox-bin/`.

**Post-install verification**:

```bash
python -c "from automation import TaskManager; print('Core import OK')"
python demo.py   # Should launch browsers and visit example sites (monitor with care)
```

### Development Dependencies

```bash
./install-dev.sh
pip install --user -r requirements-dev.txt
```

---

## 4. macOS Installation

Use `install-mac-dev.sh`. Expect additional manual steps for:

- Homebrew Python + LevelDB
- geckodriver (newer versions will not work with FF52)
- XQuartz or equivalent for display if not running headless

The project has not been actively maintained on macOS for header bidding workloads.

---

## 5. Post-Installation Configuration & Hardening (Mandatory)

After any install:

1. **Replace Hardcoded Paths** (TrackerProject layer)
   - Search entire codebase for `~/headerBidding` and `/mnt/hgfs`.
   - Introduce `HB_ROOT`, `RESULTS_DIR` environment variables or a `config/local.json`.

2. **Review & Lock Down `browser_params.json`** (see [Configuration.md](docs/Configuration.md))
   - Disable `save_all_content` unless required.
   - Consider disabling `post_body` capture for most experiments.

3. **Create Isolated Results Directory**
   ```bash
   mkdir -p results/{data,logs,bids_intent,bids_no_intent,profiles}
   chmod 700 results/
   ```

4. **Network Containment**
   - Run behind a research proxy or VPN that logs all egress.
   - Consider using `mitmproxy` or `squid` with allow-lists (advanced).

5. **Verify No Secrets in Git**
   ```bash
   git ls-files | xargs grep -l "password\|api_key\|AKIA\|/home/<researcher>"
   ```

---

## 6. Verification & Smoke Tests

```python
# Minimal smoke test (run inside isolated environment)
from automation import TaskManager, CommandSequence

manager_params, browser_params = TaskManager.load_default_params(1)
browser_params[0]['headless'] = True
browser_params[0]['http_instrument'] = True

manager = TaskManager.TaskManager(manager_params, browser_params)
cs = CommandSequence.CommandSequence("https://example.com")
cs.get(sleep=3)
manager.execute_command_sequence(cs)
manager.close()
print("Smoke test passed – check data_directory for crawl-data.sqlite")
```

For HB-specific smoke test, see `TrackerProject/src/crawling/doCrawl.py` with a single-site dry run (you will need to patch paths first).

---

## 7. Troubleshooting Installation

Common failures:

- **"geckodriver not found"** – The install script places it inside `firefox-bin/`. Ensure `PATH` includes it or that Selenium is pointed at the correct driver location.
- **LevelDB / plyvel errors** – Missing `libleveldb` dev packages; re-run package installation.
- **Firefox 52 fails to launch on newer kernels** – Expected. Use Docker with older base or modernize the stack.
- **Permission errors on results/** – Ensure the user running the Python process owns the results tree.

Full troubleshooting: [Troubleshooting.md](docs/Troubleshooting.md)

---

## 8. Uninstallation / Cleanup

```bash
# Remove legacy Firefox
rm -rf firefox-bin/

# Remove Python packages (careful – may affect system)
pip uninstall -r requirements.txt -y

# Remove research data (irreversible)
rm -rf results/ logs/ *.sqlite *.json
```

---

**Next Document**: [Usage-Guide.md](docs/Usage-Guide.md) – How to design and execute header bidding measurement experiments safely.
