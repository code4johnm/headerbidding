"""
Reference implementations of the two main published methods so they can be
compared head-to-head against new techniques on identical synthetic data.

- run_kashf_baseline: the 2020 method (with the exact limitations)
- run_atom_style_baseline: simplified version of the 2022 ATOM creative-based approach
"""

from __future__ import annotations
import pandas as pd
from typing import Dict, Set, Tuple, List
from .inference import KashfStyleInferencer


def run_kashf_baseline(
    df: pd.DataFrame,
    advertiser_cols: List[str],
    top_k: int = 3,
) -> Dict:
    """Exact re-implementation of the original 2020 pipeline."""
    inf = KashfStyleInferencer(top_k=top_k)
    res = inf.fit(df, advertiser_cols)
    edges = inf.get_inferred_edges(res)
    return {
        "method": "kashf_2020_reimpl",
        "edges": edges,
        "per_advertiser": res,
        "k": top_k,
    }


def run_atom_style_baseline(
    df: pd.DataFrame,
    advertiser_cols: List[str],
    top_k: int = 3,
) -> Dict:
    """
    Highly simplified ATOM-style approach (2022).

    Real ATOM used statistical tests on differences in *delivered ad creative*
    distributions when a tracker is blocked vs. not blocked.

    Here we use the creative_score_* columns (count of matched high-value topics)
    as a proxy and apply a simple t-test / rank difference per (tracker, adv).
    """
    import numpy as np
    from scipy import stats

    tracker_cols = [c for c in df.columns if c.startswith("tracker_")]
    results = {}
    edges = set()

    for adv in advertiser_cols:
        creative_col = f"creative_score_{adv}"
        if creative_col not in df.columns:
            continue

        scores_with = []
        scores_without = []

        for tcol in tracker_cols:
            t = tcol.replace("tracker_", "")
            mask_present = df[tcol] == 1
            if mask_present.sum() < 30:
                continue

            with_t = df.loc[mask_present, creative_col]
            without_t = df.loc[~mask_present, creative_col]

            # Simple effect size (Cohen's d like)
            if len(with_t) > 5 and len(without_t) > 5:
                diff = with_t.mean() - without_t.mean()
                pooled_std = np.sqrt(
                    ((len(with_t)-1)*with_t.var() + (len(without_t)-1)*without_t.var()) /
                    (len(with_t) + len(without_t) - 2)
                )
                effect = diff / (pooled_std + 1e-9)

                # Record if effect is large
                if abs(effect) > 0.25:  # arbitrary but reasonable threshold
                    edges.add((t, adv))
                    scores_with.append((t, effect))

        results[adv] = {
            "strong_effects": sorted(scores_with, key=lambda x: -abs(x[1]))[:top_k],
        }

    return {
        "method": "atom_2022_simplified",
        "edges": edges,
        "per_advertiser": results,
    }


def run_all_baselines(
    df: pd.DataFrame,
    advertiser_cols: List[str],
) -> Dict[str, Dict]:
    return {
        "kashf": run_kashf_baseline(df, advertiser_cols),
        "atom_simplified": run_atom_style_baseline(df, advertiser_cols),
    }
