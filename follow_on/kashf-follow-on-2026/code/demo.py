#!/usr/bin/env python3
"""
One-command demo of the core contribution.

Run:
    python demo.py

This reproduces (on synthetic ground truth) the exact limitation described
in §4.4 of the 2020 PoPETs Kashf paper and shows that the new calibrated
method controls error rate while recovering substantially more real relationships.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kashf.simulator import generate_and_run
from kashf.inference import compare_methods
from kashf.metrics import fdr_aware_precision_recall

print("Generating small synthetic ecosystem (easy difficulty for speed)...")
G, df, harness = generate_and_run(difficulty="easy", n_trackers=18, n_advertisers=5, n_personas=800, seed=7)

true_direct = {(s, d) for s, d, _, _ in G.direct_edges if s.startswith("T") and d.startswith("A")}
advs = [f"A{i:02d}" for i in range(5)]

print("Running Kashf (2020) re-implementation and CausalKashf (calibrated cutoff)...")
comp = compare_methods(df, advs, target_fdr=0.10)

k_edges = set(comp["kashf_original"]["edges"])
c_edges = set(comp["causalkashf_calibrated"]["edges"])

k_m = fdr_aware_precision_recall(k_edges, true_direct)
c_m = fdr_aware_precision_recall(c_edges, true_direct)

print("\n=== Results on known ground truth ===")
print(f"Original Kashf (top-3):  precision={k_m['precision']:.3f}  recall={k_m['recall_direct']:.3f}  empirical_FDR={k_m['fdr']:.3f}")
print(f"CausalKashf (target 10% FDR): precision={c_m['precision']:.3f}  recall={c_m['recall_direct']:.3f}  empirical_FDR={c_m['fdr']:.3f}")
print(f"\nCausalKashf recovered {len(c_edges & true_direct)} true edges vs {len(k_edges & true_direct)} for the 2020 method")
print("\nThis is only possible because we have perfect ground truth from the simulator.")
print("On real web data the 2020 authors could never compute these numbers.")