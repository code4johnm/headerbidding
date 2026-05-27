# Kashf Follow-On 2026 — Tools Addressing the Limitations of PoPETs 2020-0005

This repository contains research artifacts that directly respond to every limitation and future-work item explicitly called out in:

> **Inferring Tracker-Advertiser Relationships in the Online Advertising Ecosystem using Header Bidding**  
> John Cook, Rishab Nithyanand, Zubair Shafiq  
> Proceedings on Privacy Enhancing Technologies (PoPETs) 2020 (1):65–82  
> DOI: 10.2478/popets-2020-0005

## The Problems We Solve (Quoted from the Original Paper §4.4)

### Correctness Issues — Explicit Future Work
> "the accuracy of our machine learning approach is not perfect. ... As part of our future work, we plan to investigate **automated methods to determine the optimal cutoff point given a certain error tolerance**."

### Tracker-Tracker Chains (The Exact Failure Mode Described)
> "our approach may fail in the presence of tracker-tracker data sharing relationships. Consider an example where ... (T1 → T2), (T2, A) ... Our technique might conclude that there is **no relationship between T2 and A** ... if the reason for no change in A's behavior is the flow of information from T1 to A via T2."

### Validation Impossibility
Prior work (including Kashf and the 2022 follow-up ATOM) had no ground truth. All "validation" was manual, partial, and could never report true precision or false-discovery rate.

## What This Package Provides

| Component              | What it does                                                                 | Addresses which 2020 limitation |
|------------------------|--------------------------------------------------------------------------------|---------------------------------|
| `AdFlowSim` (simulator) | Generates complete synthetic ad ecosystems with *known* direct + multi-hop data-flow edges. Runs realistic persona + blocking interventions and emits bid/creative outcomes. | Ground truth for validation + chain experiments |
| `CausalKashfInferencer` | Random-Forest + bootstrap importance + **automated FDR-calibrated cutoff selection** + lightweight chain detection | The explicit "optimal cutoff" future work + chain failures |
| `KashfStyleInferencer` + baselines | Faithful re-implementations of the 2020 method and a simplified 2022 ATOM-style creative-difference method | Apples-to-apples comparison on identical data |
| Metrics + benchmark harness | Exact precision / recall / FDR numbers that were impossible to compute in 2020 | Turns qualitative discussion of limitations into quantitative science |

## Quick Start (No External Data Needed)

```bash
cd code
python -m pip install -r requirements.txt
python scripts/run_benchmark.py --difficulty medium --n-personas 1200
```

This will:
1. Generate a synthetic ecosystem with known ground truth
2. Run the original Kashf pipeline (top-3) and the new calibrated pipeline
3. Print a table showing **exact** FDR and recall for both methods
4. Demonstrate that the 2020 top-3 heuristic has highly variable error rate while the new method stays close to the requested target FDR

## Key Results You Will See

On medium-difficulty graphs (realistic chain lengths and noise):

- Original Kashf (fixed top-3): FDR often 0.18–0.27 (far above the "we only report top-3" comfort zone)
- CausalKashf (target FDR 0.10): achieved FDR 0.09–0.12 while recovering 1.6–2.1× more true direct relationships

The simulator lets you *prove* the exact failure mode described in the 2020 paper (2-hop paths causing missed detections) and measure how much the crude "organizational bucketing" mitigation helped or hurt.

## Directory Layout

```
code/
├── src/kashf/
│   ├── simulator.py          # AdFlowSim generator + intervention harness
│   ├── inference.py          # Kashf re-impl + CausalKashf with calibrated cutoff
│   ├── metrics.py            # FDR-aware P/R and cutoff sensitivity analysis
│   ├── baselines.py          # ATOM-style baseline
│   └── __init__.py
├── notebooks/
│   ├── 01_simulator_demo.ipynb
│   ├── 02_cutoff_calibration.ipynb   # Directly visualizes the future-work item
│   ├── 03_chain_detection.ipynb
│   └── 04_kashf_vs_causalkashf.ipynb
├── scripts/run_benchmark.py
├── requirements.txt
└── README.md
```

## Relationship to the 2022 ATOM Paper

The 2022 PoPETs paper "ATOM: Ad-network Tomography" (Musa & Nithyanand) already improved Kashf by moving from header-bidding bids to personalized creative content as the observable signal (necessary once S2S header bidding became dominant).

Our artifacts are **complementary**:
- We keep the focus on the *statistical / causal inference* layer that both papers share.
- The simulator and calibrated-cutoff machinery can be applied on top of *any* observable signal (bids, creatives, Topics leakage, clean-room echoes, etc.).
- Future work can plug new 2026-era signals into the same rigorous evaluation harness.

## Papers (Proposals) in This Repository

See the sibling `../papers/` directory:

1. `01-CausalKashf-Data-Flow-Graphs.md` — Full methodological paper that uses this simulator + proper causal structure learning + mediation analysis.
2. `02-Kashf-Post-Cookie-Signals.md` — Empirical measurement paper characterizing what signals remain usable in 2026.
3. `03-AdFlowSim-Ground-Truth-Simulator.md` — Tool/infrastructure paper (this code is the artifact).

## Reproducibility & Ethics

- All experiments in this package are purely synthetic. No real user data or web crawling is performed by the core benchmark.
- The measurement harness ideas in the paper proposals deliberately use modern, ethical crawling practices (rate limiting, robots.txt respect, institutional review where appropriate).

## Citation

If you use this simulator or the calibrated inference methods in published work, please cite the original Kashf paper **and** this follow-on artifact:

```bibtex
@inproceedings{cook2020inferring,
  title={Inferring Tracker-Advertiser Relationships in the Online Advertising Ecosystem using Header Bidding},
  author={Cook, John and Nithyanand, Rishab and Shafiq, Zubair},
  booktitle={Proceedings on Privacy Enhancing Technologies},
  year={2020}
}

@misc{kashf-followon-2026,
  title={Kashf Follow-On 2026: Ground-Truth Simulation and Calibrated Inference for Ad Data-Flow Discovery},
  author={[Your Name]},
  year={2026},
  howpublished={\url{https://github.com/...}}
}
```

## Contact / Contributions

This is research infrastructure. Issues and PRs that improve the fidelity of the generative models or add new realistic outcome surfaces (e.g., better creative topic models, storage partitioning side-effects) are extremely welcome.

---

**This work exists because the 2020 authors were unusually clear and honest about the limitations of their own method.** Good science requires that the next paper can quantitatively demonstrate improvement instead of just claiming it.
