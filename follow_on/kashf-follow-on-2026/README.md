# Follow-on Research for PoPETs 2020-0005 (Kashf)

**Paper read:** "Inferring Tracker-Advertiser Relationships in the Online Advertising Ecosystem using Header Bidding"  
**Authors:** John Cook, Rishab Nithyanand, Zubair Shafiq  
**Venue:** Proceedings on Privacy Enhancing Technologies (PoPETs) 2020 (1):65–82

## What This Repository Contains

1. **Three detailed follow-on research paper proposals** (in `papers/`) that systematically address every limitation and future-work item stated in the original paper.

2. **Production-quality open-source research code** (`code/`) centered on **AdFlowSim** — a high-fidelity synthetic ad-ecosystem generator that provides *perfect ground truth*. This is the key missing piece that prevented the 2020 authors (and the 2022 ATOM follow-up) from rigorously measuring precision, recall, or false-discovery rates.

3. **Executable demonstrations** that let you immediately see the problems the original authors described and how the new methods improve upon them.

## Why This Work Was Necessary

The original paper was unusually forthright about its own limitations (§4.4 "Limitations"):

- **Explicit future work**: "investigate automated methods to determine the optimal cutoff point given a certain error tolerance."
- **Chain failure mode**: Detailed example of how tracker→tracker→advertiser paths cause the method to miss real relationships.
- **Validation problem**: All validation was manual and partial; true error rates were unknowable.

Six years later, no public artifact existed that let researchers *quantitatively* study these issues or compare new proposals against the original under controlled conditions.

## Quick Start

```bash
cd code
pip install -r requirements.txt
python demo.py                    # 30-second demo
python scripts/run_benchmark.py   # full head-to-head with numbers
```

See `code/README.md` for detailed usage and interpretation of the results.

## Papers

| File | Focus | Primary Limitations Addressed |
|------|-------|-------------------------------|
| `papers/01-CausalKashf-Data-Flow-Graphs.md` | New causal + calibrated inference method | Cutoff selection (future work), chain detection, indirect intermediaries, validation |
| `papers/02-Kashf-Post-Cookie-Signals.md` | Empirical characterization of 2026 observables | Evolution of the ecosystem beyond what HB bids could see in 2020 |
| `papers/03-AdFlowSim-Ground-Truth-Simulator.md` | The simulator + benchmark infrastructure itself | The meta-problem: lack of ground truth that made rigorous claims impossible |

## Relationship to Existing Work

- **Kashf (2020)** — The paper you are reading.
- **ATOM (PoPETs 2022)** — Excellent follow-up by one of the original co-authors that solved the "client-side HB visibility" problem by using ad creative content instead of bids. Our simulator and calibration machinery are designed to work *with* ATOM-style signals as well.
- This repository is **infrastructure + methodological improvement**, not a competing measurement study.

## License & Citation

Research use. When publishing work that uses the simulator or calibrated inference techniques, please cite the original Kashf paper and note that the evaluation was performed using the AdFlowSim ground-truth harness.

## Credits

This entire body of follow-on work was created in direct response to the intellectual honesty of the 2020 authors in clearly documenting where their method was known to be incomplete or unvalidated. That level of self-assessment is rare and extremely valuable to the research community.

---

**Status (April 2026):** All core simulator, inference, metrics, and demo code is complete and runnable. The three paper proposals are detailed enough to serve as the basis for actual submissions or grant proposals. The next natural steps are (a) richer outcome models in the simulator, (b) full causal structure learning implementation, and (c) a real 2026-era web measurement campaign using the new signals catalogued in paper #2.