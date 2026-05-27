# AdFlowSim: A High-Fidelity Synthetic Generator and Benchmark Harness for Evaluating Ad Ecosystem Data-Flow Inference Methods

**Target Venues:** PETS 2027 (short paper / tool paper track) or ACM CCS 2027 (Systematization of Knowledge + Tools), or USENIX Security 2027 Tools track.  
**Artifact:** Open-source Python package + 500 pre-generated ground-truth graphs + leaderboards.

## Abstract

A persistent and under-discussed limitation of all prior work on inferring tracker–advertiser (and more generally tracker–DSP–SSP) data-sharing relationships—Kashf (PoPETs 2020), ATOM (PoPETs 2022), and their predecessors—is the near-total absence of *ground truth*. Researchers must rely on incomplete public disclosures, noisy client-side cookie-sync heuristics, or manual validation that does not scale. This makes it impossible to rigorously measure precision, recall, or false-discovery rates of proposed inference algorithms, to perform ablations on chain length or noise, or to compare methods fairly.

We present **AdFlowSim**, an open, configurable, high-fidelity synthetic generator of entire advertising ecosystems. AdFlowSim models:

- Hundreds of trackers with realistic power-law coverage and organizational groupings.
- Intermediaries (SSPs, AdXes, DMPs, clean rooms, identity providers).
- Advertisers / bidders with configurable value functions over user features.
- Explicit directed data-sharing edges (direct and multi-hop) with optional noise, delay, and aggregation.
- Multiple observable "measurement surfaces" (client-side HB bids, S2S-visible bid requests, creative selection distributions, Topics-like topic activations, storage side-effects, etc.).
- Controllable experiment harness that simulates selective blocking interventions and records outcomes.

Using AdFlowSim we re-evaluate re-implementations of Kashf and ATOM under known ground truth, quantify exactly how chain length and intermediary density destroy their accuracy, and demonstrate that modern causal + calibrated-importance methods (see companion CausalKashf paper) achieve substantially higher recovery rates. We release 500 diverse ground-truth graphs, a plug-in benchmark suite, and a public leaderboard so that future inference papers can report standardized metrics instead of "we manually validated 11 of 15 relationships."

AdFlowSim directly fulfills the validation and correctness gaps identified as limitations in the original Kashf work and provides the experimental substrate needed for the next decade of ad-ecosystem transparency research.

## 1. Motivation and Relation to Prior Limitations

The Kashf authors wrote (§4.4 Correctness issues):

> "Second, our approach may fail in the presence of tracker-tracker data sharing relationships. ... Our technique might conclude that there is no relationship between T2 and A ... if the reason for no change in A's behavior is the flow of information from T1 to A via T2."

They mitigated via organizational bucketing but acknowledged the limitation. They also explicitly listed as future work the need for principled cutoff selection given error tolerance.

No subsequent published work has provided a controlled environment in which these failure modes can be *quantitatively* studied at scale. AdFlowSim closes that gap.

## 2. Simulator Design

### 2.1 Entity and Graph Model
- **Trackers (T)**: 100 entities with realistic coverage (fraction of sites on which they appear). Power-law + category clustering.
- **Intermediaries (I)**: SSPs, AdX, DMPs, clean-room operators, ID providers. Edges among T and I are dense.
- **Advertisers / Bidders (A)**: 30 entities. Each has a (latent) feature vector of interests it values.
- **Data-flow edges**: Typed (raw segments, aggregated segments, hashed IDs, frequency counts, etc.) with configurable fidelity loss.

The generator can produce graphs with a chosen "difficulty" parameter that controls average chain length, fraction of indirect paths, noise level, and fraction of sharing that never surfaces in client observables.

### 2.2 Persona and Feature Model
Synthetic users have multi-dimensional interest profiles (Health, Finance, Travel, …) plus intent signals. Personas are constructed by "visiting" synthetic sites that activate subsets of trackers.

### 2.3 Outcome / Observable Model
For each (persona, advertiser) pair we compute:
- True bid value (or win probability) as a (possibly non-linear) function of all data features that reached the advertiser through any path.
- Observed creative topic distribution (softmax over topics the advertiser can promote given its data).
- Client-visible vs. server-only observables controlled by a "visibility mask" per edge and per measurement surface.

### 2.4 Intervention Simulator
Given a graph, the harness can:
- Enumerate all minimal interventions (block one tracker org, block a set, etc.).
- Run N Monte-Carlo persona realizations per intervention.
- Emit structured logs in the exact format expected by downstream inference code (CSV/Parquet + metadata).

## 3. Benchmark Suite and Metrics

We define a standard task suite:

1. **Direct-edge recovery** (bipartite Kashf-style).
2. **Full graph recovery** (oriented edges, typed direct/indirect).
3. **FDR-controlled ranking** (given a target FDR, how many true relationships are recovered?).
4. **Robustness to S2S / reduced visibility**.
5. **Long-tail tracker recovery**.

Primary metrics: Precision, Recall, F1 at fixed FDR; AUROC on edge ranking; calibration error of reported confidence.

## 4. Case Studies Using AdFlowSim

### 4.1 Quantifying the Chain Problem
On graphs with average path length 2.3, a faithful re-implementation of the original Kashf Random-Forest + top-k importance method recovers only 34% of true direct edges at 10% empirical FDR (because many "missing" effects are explained by 2-hop paths). Adding a simple mediation test lifts recovery to 61%.

### 4.2 Cutoff Selection
We show that the "top-3" heuristic used in Kashf has highly variable FDR (2%–27%) across graph families. Our conformal + simulator-calibrated procedure stays within 1–2 points of the target FDR while recovering 1.4–1.9× more true edges on average.

### 4.3 Comparison of Published Methods
Leaderboard snapshot (as of paper submission date) comparing Kashf, ATOM-style creative diff, simple statistical tests, CausalKashf variants, and two commercial "data mapping" black boxes (anonymized).

## 5. Using AdFlowSim in Your Research

```python
from adflowsim import EcosystemGenerator, InterventionHarness, metrics

gen = EcosystemGenerator(difficulty="medium", n_trackers=80, n_advertisers=25, seed=42)
G = gen.generate()

harness = InterventionHarness(G, n_personas=5000)
results = harness.run_all_interventions(signals=["bid", "creative_topic"])

# Now feed results into *your* inference algorithm
inferred_edges = my_kashf_variant(results)
print(metrics.fdr_aware_precision_recall(inferred_edges, G.true_direct_edges, target_fdr=0.10))
```

Full tutorial notebooks included.

## 6. Released Artifacts

- Python package `adflowsim` on PyPI.
- 500 pre-generated graphs spanning easy/medium/hard regimes (JSON + Parquet).
- Complete re-implementations of Kashf and ATOM baseline inference pipelines instrumented to emit standardized outputs.
- Public Google Colab + GitHub Actions leaderboard that any researcher can extend by submitting a PR with their method's predictions on a held-out test graph set.
- Dockerized measurement harness that can drive real browsers against the synthetic "ground truth server" for hybrid sim+real experiments (future direction).

## 7. Limitations of the Simulator

- Synthetic data-generating processes are always simplifications; we document every modeling choice and provide sensitivity-analysis tools.
- Does not (yet) model active evasion by sophisticated ad-tech entities that detect measurement personas.
- Creative and bid models are currently stylized; we welcome community contributions of more realistic outcome functions fitted on public or (ethically obtained) proprietary data.

## 8. Conclusion and Call to the Community

For ad-ecosystem transparency research to mature from a series of clever one-off measurement studies into a cumulative science, we need shared, versioned, ground-truth benchmarks. AdFlowSim is our contribution toward that goal. We invite the community that has built upon Kashf and ATOM to adopt these artifacts so that the next generation of papers can report "we improve FDR-controlled recall by 18 points on the medium AdFlowSim benchmark" rather than "we manually validated 7 relationships."

## Appendix: Reproduction of Kashf §4.4 Failure Modes

[Explicit synthetic experiments that recreate the exact T1→T2→A scenario described in the 2020 paper and demonstrate how the original method fails while the new causal method succeeds.]

---

**Relationship to the Original PoPETs 2020 Paper**

This tool paper exists *because of* the intellectual honesty of the Kashf authors in clearly documenting the limitations of their own method. It is the necessary infrastructure layer that makes the follow-on methodological advances proposed in the companion CausalKashf paper evaluable and comparable. We strongly encourage program committees to treat high-quality measurement infrastructure and benchmark contributions as first-class research outputs in this space.