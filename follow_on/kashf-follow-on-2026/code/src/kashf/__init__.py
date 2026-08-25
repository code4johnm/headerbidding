"""
Kashf Follow-On 2026: Tools and methods addressing limitations identified
in "Inferring Tracker-Advertiser Relationships in the Online Advertising
Ecosystem using Header Bidding" (Cook, Nithyanand, Shafiq, PoPETs 2020).

This package provides:
- AdFlowSim: high-fidelity synthetic ad ecosystem generator with ground truth
- Calibrated inference pipelines (uncertainty-aware feature importance + chain detection)
- Metrics for rigorous evaluation under known ground truth
- Reference baselines (Kashf-style and ATOM-style)

All artifacts directly target the limitations and future work stated in §4.4 of the original paper.
"""

__version__ = "0.1.0"
__paper__ = "popets-2020-0005"

from .baselines import run_atom_style_baseline, run_kashf_baseline
from .inference import CausalKashfInferencer, KashfStyleInferencer
from .metrics import edge_recovery_report, fdr_aware_precision_recall
from .simulator import EcosystemGenerator, InterventionHarness

__all__ = [
    "EcosystemGenerator",
    "InterventionHarness",
    "KashfStyleInferencer",
    "CausalKashfInferencer",
    "fdr_aware_precision_recall",
    "edge_recovery_report",
    "run_kashf_baseline",
    "run_atom_style_baseline",
]
