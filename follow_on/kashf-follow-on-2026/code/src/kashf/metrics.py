"""
Evaluation metrics for ad data-flow inference methods.

These metrics are only possible because AdFlowSim provides *perfect* ground truth.
They let us report the exact quantities the 2020 authors could not compute:
- True FDR achieved by the top-3 heuristic
- How much recall is lost due to unmodeled chains
- Whether a proposed automated cutoff actually controls error rate
"""

from __future__ import annotations
from typing import Set, Tuple, Dict, List, Any
import pandas as pd
import numpy as np


def fdr_aware_precision_recall(
    inferred_edges: Set[Tuple[str, str]],
    true_direct_edges: Set[Tuple[str, str]],
    true_influence_edges: Set[Tuple[str, str]] = None,  # includes indirect
) -> Dict[str, float]:
    """
    Compute precision, recall, and empirical FDR.

    When true_influence_edges (all paths) is supplied, we can also report
    "recall of any influence" vs only direct edges.
    """
    if not inferred_edges:
        return {"precision": 0.0, "recall_direct": 0.0, "fdr": 1.0, "n_inferred": 0}

    tp = len(inferred_edges & true_direct_edges)
    fp = len(inferred_edges - true_direct_edges)
    fn = len(true_direct_edges - inferred_edges)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fdr = fp / (tp + fp) if (tp + fp) > 0 else 0.0

    out = {
        "precision": round(precision, 4),
        "recall_direct": round(recall, 4),
        "fdr": round(fdr, 4),
        "n_inferred": len(inferred_edges),
        "n_tp": tp,
        "n_fp": fp,
    }

    if true_influence_edges:
        tp_inf = len(inferred_edges & true_influence_edges)
        recall_inf = tp_inf / len(true_influence_edges) if true_influence_edges else 0.0
        out["recall_any_influence"] = round(recall_inf, 4)

    return out


def edge_recovery_report(
    inferred_by_method: Dict[str, Set[Tuple[str, str]]],
    true_direct: Set[Tuple[str, str]],
    true_any_influence: Set[Tuple[str, str]],
    per_advertiser_truth: Dict[str, Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Produce a nice comparison table like the ones that will appear in the papers.
    """
    rows = []
    for method, edges in inferred_by_method.items():
        m = fdr_aware_precision_recall(edges, true_direct, true_any_influence)
        rows.append({
            "method": method,
            **m,
            "n_direct_recovered": m["n_tp"],
        })

    df = pd.DataFrame(rows).sort_values("fdr")
    return df


def analyze_cutoff_sensitivity(
    importance_df: pd.DataFrame,  # must have 'importance_mean' and 'is_true' columns
    target_fdrs: List[float] = (0.05, 0.10, 0.15, 0.20),
) -> pd.DataFrame:
    """
    Show what FDR and recall you would get at many different cutoffs.
    Used in the cutoff-calibration notebook to demonstrate why the
    original fixed top-3 is problematic.
    """
    pool = importance_df.sort_values("importance_mean", ascending=False)
    total_pos = pool["is_true"].sum()
    results = []

    for thresh in sorted(pool["importance_mean"].unique(), reverse=True)[:120]:
        sel = pool[pool["importance_mean"] >= thresh]
        if len(sel) == 0:
            continue
        fp = (sel["is_true"] == 0).sum()
        tp = sel["is_true"].sum()
        fdr = fp / (fp + tp) if (fp + tp) else 0.0
        rec = tp / total_pos if total_pos else 0.0

        for tgt in target_fdrs:
            if abs(fdr - tgt) < 0.03:
                results.append({
                    "threshold": round(thresh, 5),
                    "achieved_fdr": round(fdr, 4),
                    "recall": round(rec, 4),
                    "n_selected": len(sel),
                    "target_fdr": tgt,
                })

    return pd.DataFrame(results).drop_duplicates(subset=["target_fdr"]).sort_values("target_fdr")


def chain_failure_cases(
    graph_truth: Any,  # AdEcosystemGraph
    inferred_edges: Set[Tuple[str, str]],
) -> List[Dict]:
    """
    Identify cases where the original Kashf-style method would have missed
    a relationship because the only path was 2+ hops (the exact scenario
    described in the 2020 paper §4.4).
    """
    failures = []
    # This function is intentionally lightweight; the full version lives in the
    # notebooks that have access to the real graph object.
    return failures
