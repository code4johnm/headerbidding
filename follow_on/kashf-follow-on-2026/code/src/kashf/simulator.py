"""
AdFlowSim - Synthetic Ground-Truth Generator for Ad Data-Flow Inference Research

This module directly addresses two core limitations identified in the 2020 PoPETs Kashf paper (§4.4):

1. Correctness issues with tracker-tracker chains: "our approach may fail in the presence of
   tracker-tracker data sharing relationships" (T1 -> T2 -> A example given explicitly).
2. Lack of any ground truth for validation and cutoff calibration. The authors stated as
   future work: "investigate automated methods to determine the optimal cutoff point given
   a certain error tolerance."

AdFlowSim generates complete causal graphs with KNOWN edges (direct + indirect), runs
synthetic interventions that mimic persona + selective blocking experiments, and produces
observable outcomes (bids, creatives, etc.) whose generative process is fully known.

Researchers can therefore compute *exact* precision, recall, and FDR for any inference
method — something impossible on real web data.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from collections import defaultdict
import json
import random


@dataclass
class AdEcosystemGraph:
    """A complete synthetic ad ecosystem with ground-truth data flows."""
    # Nodes
    trackers: List[str]                    # e.g., "DoubleVerify", "Alphabet", ...
    intermediaries: List[str]              # SSPs, AdX, DMPs, clean rooms, ID providers
    advertisers: List[str]                 # DSPs / bidders / advertisers

    # Ground-truth directed edges (data sharing)
    # Format: (source, target, edge_type, fidelity) where fidelity in [0,1] = how much info preserved
    direct_edges: List[Tuple[str, str, str, float]]

    # Derived: full transitive closure for simulation (who can ultimately influence whom)
    influence_paths: Dict[str, List[List[str]]]  # advertiser -> list of paths that reach it

    # Tracker coverage (fraction of "sites" on which each tracker appears)
    tracker_coverage: Dict[str, float]

    # Organizational grouping (for testing the crude mitigation used in original Kashf)
    org_groups: Dict[str, str]               # entity -> org (e.g., "doubleclick.net" -> "Alphabet")

    # Metadata + simulation parameters (needed by harness)
    difficulty: str
    seed: int
    n_trackers: int
    n_advertisers: int
    noise_level: float = 0.18  # default for medium; overridden at generation time


@dataclass
class InterventionResult:
    """Result of one controlled intervention experiment."""
    persona_id: int
    blocked_trackers: Set[str]             # the orgs we blocked during persona construction
    advertiser_bids: Dict[str, float]      # advertiser -> observed (synthetic) bid
    creative_topics: Dict[str, List[str]]  # advertiser -> list of topics in delivered creatives
    # Future: other signals (Topics leakage, storage side effects, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EcosystemGenerator:
    """
    Generates realistic synthetic ad ecosystems with configurable difficulty.

    The generative process is designed to reproduce the failure modes described in
    the original Kashf paper while remaining simple enough to be fully inspectable.
    """

    def __init__(
        self,
        difficulty: str = "medium",
        n_trackers: int = 40,
        n_intermediaries: int = 12,
        n_advertisers: int = 12,
        seed: int = 42,
        power_law_alpha: float = 1.8,
    ):
        self.difficulty = difficulty
        self.n_trackers = n_trackers
        self.n_intermediaries = n_intermediaries
        self.n_advertisers = n_advertisers
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        random.seed(seed)

        # Difficulty parameters (control chain length, noise, indirect fraction)
        if difficulty == "easy":
            self.avg_chain_len = 1.1
            self.indirect_fraction = 0.15
            self.noise_level = 0.08
            self.tracker_coverage_skew = 2.2
        elif difficulty == "medium":
            self.avg_chain_len = 1.8
            self.indirect_fraction = 0.35
            self.noise_level = 0.18
            self.tracker_coverage_skew = 1.7
        else:  # hard
            self.avg_chain_len = 2.6
            self.indirect_fraction = 0.55
            self.noise_level = 0.32
            self.tracker_coverage_skew = 1.4

        self.power_law_alpha = power_law_alpha

    def generate(self) -> AdEcosystemGraph:
        """Generate a complete ecosystem with known ground truth."""
        # 1. Name the entities
        trackers = [f"T{i:02d}" for i in range(self.n_trackers)]
        intermediaries = [f"I{i:02d}" for i in range(self.n_intermediaries)]
        advertisers = [f"A{i:02d}" for i in range(self.n_advertisers)]

        # 2. Organizational grouping (crude mitigation from original paper)
        org_groups = {}
        org_names = ["BigTech", "AdTech1", "AdTech2", "Measurement", "Identity", "Retail"]
        for i, t in enumerate(trackers):
            org_groups[t] = org_names[i % len(org_names)]
        for i, a in enumerate(advertisers):
            org_groups[a] = org_names[(i + 2) % len(org_names)]
        for i, inter in enumerate(intermediaries):
            org_groups[inter] = org_names[(i + 4) % len(org_names)]

        # 3. Realistic tracker coverage (power-law like real web)
        ranks = np.arange(1, self.n_trackers + 1)
        coverage = 1.0 / (ranks ** (1.0 / self.tracker_coverage_skew))
        coverage = coverage / coverage.max() * 0.65 + 0.02  # 2%-67% range
        tracker_coverage = {t: float(c) for t, c in zip(trackers, coverage)}

        # 4. Build direct data-sharing edges (the ground truth we want to recover)
        direct_edges: List[Tuple[str, str, str, float]] = []

        # 4a. Tracker -> Tracker (the dangerous chains)
        n_tt = int(self.n_trackers * 0.8 * (0.3 if self.difficulty == "easy" else 0.6))
        for _ in range(n_tt):
            src = random.choice(trackers)
            dst = random.choice([t for t in trackers if t != src])
            fidelity = 0.65 + self.rng.uniform(-0.15, 0.25)
            direct_edges.append((src, dst, "tracker_tracker", float(np.clip(fidelity, 0.3, 0.95))))

        # 4b. Tracker -> Intermediary (very common)
        for t in trackers[: int(self.n_trackers * 0.7)]:
            for inter in random.sample(intermediaries, k=min(2, len(intermediaries))):
                if self.rng.random() < 0.55:
                    fid = 0.75 + self.rng.uniform(-0.1, 0.2)
                    direct_edges.append((t, inter, "tracker_inter", float(np.clip(fid, 0.4, 0.98))))

        # 4c. Intermediary -> Advertiser (the classic server-side path)
        for inter in intermediaries:
            for a in random.sample(advertisers, k=min(3, len(advertisers))):
                if self.rng.random() < 0.45:
                    fid = 0.70 + self.rng.uniform(-0.12, 0.22)
                    direct_edges.append((inter, a, "inter_advertiser", float(np.clip(fid, 0.35, 0.97))))

        # 4d. Direct Tracker -> Advertiser (client-side cookie sync style or strong partnerships)
        n_direct = int(self.n_trackers * 0.4 * (0.6 if self.difficulty == "easy" else 0.9))
        for _ in range(n_direct):
            t = random.choice(trackers)
            a = random.choice(advertisers)
            if not any(e[0] == t and e[1] == a for e in direct_edges):
                fid = 0.80 + self.rng.uniform(-0.08, 0.15)
                direct_edges.append((t, a, "direct_ta", float(np.clip(fid, 0.55, 0.99))))

        # 5. Compute influence paths for every advertiser (transitive closure + path enumeration)
        # This is the "ground truth" of who can affect whom
        influence_paths: Dict[str, List[List[str]]] = {a: [] for a in advertisers}

        # Build adjacency
        adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for src, dst, etype, fid in direct_edges:
            adj[src].append((dst, fid))

        def dfs_paths(current: str, target: str, path: List[str], visited: Set[str], max_depth: int = 5):
            if len(path) > max_depth:
                return
            if current == target and len(path) > 1:
                influence_paths[target].append(path[:])
                return
            for neigh, _ in adj.get(current, []):
                if neigh not in visited:
                    visited.add(neigh)
                    dfs_paths(neigh, target, path + [neigh], visited, max_depth)
                    visited.remove(neigh)

        for a in advertisers:
            # Direct
            for t in trackers:
                if any(e[0] == t and e[1] == a for e in direct_edges):
                    influence_paths[a].append([t, a])
            # Via intermediaries and chains
            visited = set([a])
            dfs_paths(a, a, [a], visited)

        # Dedup paths
        for a in advertisers:
            seen = set()
            uniq = []
            for p in influence_paths[a]:
                key = tuple(p)
                if key not in seen:
                    seen.add(key)
                    uniq.append(p)
            influence_paths[a] = uniq

        # 6. Inject some pure indirect-only relationships (the exact failure mode from the paper)
        # We deliberately create cases where blocking an upstream tracker has an effect
        # even though there is no *direct* edge to the advertiser.
        if self.difficulty != "easy":
            for a in advertisers[: max(2, self.n_advertisers // 3)]:
                upstream = random.choice(trackers)
                mid = random.choice([t for t in trackers if t != upstream] + intermediaries)
                # Ensure path upstream -> mid -> ... -> a exists indirectly
                if not any(e[0] == upstream and e[1] == a for e in direct_edges):
                    # Add the mid->a if needed to create the chain
                    if not any(e[0] == mid and e[1] == a for e in direct_edges):
                        direct_edges.append((mid, a, "indirect_setup", 0.6 + self.rng.uniform(0, 0.2)))
                    if not any(e[0] == upstream and e[1] == mid for e in direct_edges):
                        direct_edges.append((upstream, mid, "indirect_setup", 0.65 + self.rng.uniform(0, 0.15)))

        graph = AdEcosystemGraph(
            trackers=trackers,
            intermediaries=intermediaries,
            advertisers=advertisers,
            direct_edges=direct_edges,
            influence_paths=influence_paths,
            tracker_coverage=tracker_coverage,
            org_groups=org_groups,
            difficulty=self.difficulty,
            seed=self.seed,
            n_trackers=self.n_trackers,
            n_advertisers=self.n_advertisers,
            noise_level=self.noise_level,
        )
        return graph

    def get_true_direct_edges(self, graph: AdEcosystemGraph) -> Set[Tuple[str, str]]:
        """Return the set of (source, target) direct edges (for evaluation)."""
        return {(src, dst) for src, dst, _, _ in graph.direct_edges}

    def get_true_influencers(self, graph: AdEcosystemGraph, advertiser: str, max_hops: int = 4) -> Set[str]:
        """All trackers that can ultimately influence this advertiser (any path length)."""
        influencers = set()
        for path in graph.influence_paths.get(advertiser, []):
            for node in path[:-1]:  # exclude the advertiser itself
                if node.startswith("T"):
                    influencers.add(node)
        return influencers


class InterventionHarness:
    """
    Runs controlled "persona + blocking" experiments on a synthetic graph.

    This mirrors the measurement methodology of the original Kashf paper
    (construct persona by visiting sites while blocking certain trackers,
     then measure bids on a measurement site).
    """

    def __init__(self, graph: AdEcosystemGraph, seed: int = 123):
        self.graph = graph
        self.rng = np.random.default_rng(seed)

        # Precompute for speed
        self.adj: Dict[str, List[Tuple[str, float, str]]] = defaultdict(list)
        for src, dst, etype, fid in graph.direct_edges:
            self.adj[src].append((dst, fid, etype))

        # Simple topic model (16 categories like the original paper)
        self.topics = [
            "Adult", "Arts", "Business", "Computers", "Games", "Health",
            "Home", "Kids", "News", "Recreation", "Reference", "Science",
            "Shopping", "Society", "Sports", "Regional"
        ]

    def _propagate_features(
        self,
        activated_trackers: Set[str],
        blocked: Set[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Simulate data flow from activated trackers through the graph,
        respecting blocks. Returns per-advertiser received feature strength.
        """
        # Each tracker that is active and not blocked injects a feature vector
        # (simplified: one scalar "interest strength" per topic for demo purposes)
        received: Dict[str, Dict[str, float]] = {a: defaultdict(float) for a in self.graph.advertisers}

        # For each activated tracker, propagate along all paths
        for t in activated_trackers:
            if t in blocked:
                continue
            # BFS with fidelity decay
            queue = [(t, 1.0, 0)]  # node, current_fidelity, hops
            visited = set()
            while queue:
                node, fid, hops = queue.pop(0)
                if node in visited or hops > 5:
                    continue
                visited.add(node)
                for neigh, edge_fid, etype in self.adj.get(node, []):
                    new_fid = fid * edge_fid * (0.92 ** hops)  # decay with hops
                    if new_fid < 0.05:
                        continue
                    if neigh.startswith("A"):  # reached an advertiser
                        # The advertiser receives a noisy version of the tracker's "data"
                        strength = new_fid * (0.7 + 0.6 * self.rng.random())
                        # Distribute across a few topics (simplified)
                        for topic in random.sample(self.topics, 3):
                            received[neigh][topic] += strength * (0.6 + 0.8 * self.rng.random())
                    else:
                        queue.append((neigh, new_fid, hops + 1))
        return received

    def _bid_function(
        self,
        advertiser: str,
        received_features: Dict[str, float],
        persona_topics: List[str],
        intent: bool = False
    ) -> float:
        """
        Advertiser's (synthetic) bid value given the data it received.
        This is the observable outcome we try to predict from tracker presence.
        """
        # Base bid + value from matched interests + noise
        base = 0.18 + 0.07 * self.rng.random()
        match_bonus = 0.0
        for topic in persona_topics:
            match_bonus += 0.09 * received_features.get(topic, 0.0)

        intent_bonus = 0.22 if intent else 0.0
        noise = self.rng.normal(0, self.graph.noise_level * 0.6)

        bid = base + match_bonus + intent_bonus + noise
        # Heavy tail like real bids; occasional very high value users
        if self.rng.random() < 0.03:
            bid *= 3.8
        return float(max(0.0, bid))

    def _creative_topics(
        self,
        advertiser: str,
        received_features: Dict[str, float],
        persona_topics: List[str]
    ) -> List[str]:
        """Which ad topics the advertiser chooses to show given its data."""
        scores = {}
        for topic in self.topics:
            scores[topic] = 0.3 * received_features.get(topic, 0.0)
            if topic in persona_topics:
                scores[topic] += 0.9
        # Pick top 2-4
        sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        chosen = [t for t, s in sorted_topics[:4] if s > 0.25]
        if not chosen:
            chosen = random.sample(self.topics, 2)
        return chosen

    def run_single_intervention(
        self,
        persona_id: int,
        blocked_trackers: Set[str],
        persona_topics: List[str],
        intent: bool = False,
        n_repeats: int = 1
    ) -> List[InterventionResult]:
        """
        Run one controlled experiment: a persona with certain trackers blocked
        visits a page; we record what each advertiser "sees" (bids + creatives).
        """
        results = []
        activated = {t for t in self.graph.trackers
                     if self.rng.random() < self.graph.tracker_coverage.get(t, 0.1)}

        received = self._propagate_features(activated, blocked_trackers)

        for _ in range(n_repeats):
            bids = {}
            creatives = {}
            for a in self.graph.advertisers:
                bids[a] = self._bid_function(a, received[a], persona_topics, intent)
                creatives[a] = self._creative_topics(a, received[a], persona_topics)

            res = InterventionResult(
                persona_id=persona_id,
                blocked_trackers=blocked_trackers.copy(),
                advertiser_bids=bids,
                creative_topics=creatives,
                metadata={
                    "intent": intent,
                    "activated_trackers": len(activated),
                    "difficulty": self.graph.difficulty,
                }
            )
            results.append(res)
        return results

    def run_full_experiment_suite(
        self,
        n_personas: int = 2000,
        block_rate: float = 0.25,
        include_intent: bool = True,
        seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        The main entry point used by inference code.

        Returns a DataFrame in the format expected by Kashf-style and CausalKashf
        inference pipelines:
            persona_id | blocked_Txx | bid_A00 | bid_A01 | ... | creative_topics_A00 | ...
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        records = []
        all_trackers = self.graph.trackers

        for pid in range(n_personas):
            # Sample persona topics (like original paper's 16 categories)
            n_topics = random.randint(1, 4)
            persona_topics = random.sample(self.topics, n_topics)
            intent = include_intent and (random.random() < 0.35)

            # Randomly decide which tracker orgs to "block" for this persona
            # (In real Kashf this was done by blocking their domains during crawl)
            blocked = set(random.sample(all_trackers, k=int(len(all_trackers) * block_rate)))

            # One "measurement" visit (in real work this was one HB-enabled site)
            res_list = self.run_single_intervention(pid, blocked, persona_topics, intent, n_repeats=1)
            res = res_list[0]

            row = {
                "persona_id": pid,
                "intent": int(intent),
                "n_persona_topics": len(persona_topics),
            }
            # Tracker presence features (1 = not blocked = "present" for the persona)
            for t in all_trackers:
                row[f"tracker_{t}"] = 0 if t in blocked else 1

            # Outcomes per advertiser
            for a in self.graph.advertisers:
                row[f"bid_{a}"] = res.advertiser_bids[a]
                # Simple encoding of creatives: count how many high-value topics matched
                row[f"creative_score_{a}"] = len(set(res.creative_topics[a]) & set(persona_topics))

            records.append(row)

        return pd.DataFrame(records)

    def get_ground_truth_for_advertiser(self, advertiser: str) -> Dict[str, Any]:
        """Return perfect ground truth for evaluation."""
        direct = {(src, dst) for src, dst, _, _ in self.graph.direct_edges if dst == advertiser}
        influencers = set()
        for path in self.graph.influence_paths.get(advertiser, []):
            for node in path[:-1]:
                if node.startswith("T"):
                    influencers.add(node)
        return {
            "advertiser": advertiser,
            "direct_tracker_sources": [e[0] for e in direct if e[0].startswith("T")],
            "all_influencing_trackers": sorted(influencers),
            "n_direct": len([e for e in direct if e[0].startswith("T")]),
            "n_paths": len(self.graph.influence_paths.get(advertiser, [])),
        }


# Convenience helper used by notebooks
def generate_and_run(
    difficulty: str = "medium",
    n_trackers: int = 30,
    n_advertisers: int = 8,
    n_personas: int = 1500,
    seed: int = 42,
) -> Tuple[AdEcosystemGraph, pd.DataFrame, InterventionHarness]:
    """One-liner for notebooks and quick experiments."""
    gen = EcosystemGenerator(difficulty=difficulty, n_trackers=n_trackers,
                             n_advertisers=n_advertisers, seed=seed)
    G = gen.generate()
    harness = InterventionHarness(G, seed=seed + 1)
    df = harness.run_full_experiment_suite(n_personas=n_personas, seed=seed + 2)
    return G, df, harness