# Assurance documentation

Documentation for the header-bidding auction path and its OpenWPM-1776 measurement hook. This is an engineering record. It is not an authorization to operate, an assessment by NSA or CISA, or a completed NIST SP 800-53 control package.

## Contents

1. [Architecture](architecture.md)
2. [API reference](api.md)
3. [Configuration](configuration.md)
4. [Contributor guide](contributing.md)
5. [Threat model](threat-model.md)
6. [Control mapping](controls.md)
7. [Supply chain](supply-chain.md)
8. [Runbooks](runbooks.md)
9. [Vulnerability disclosure](disclosure.md)
10. [SBOM, CycloneDX](sbom.cdx.json)
11. [SBOM, SPDX](sbom.spdx.json)

The auction check is:

```bash
python3 -m pip install -r requirements-auction.txt
sh scripts/run-auction.sh
```

The browser crawl described in the repository README is a separate path and still needs the conda environment in `environment.yaml`.
