# Kashf in the Post-Privacy-Sandbox World: New Observable Signals for Server-Side Data Flow Inference After the Decline of Third-Party Cookies

**Target:** PETS 2027 (or IMC / WWW 2027 measurement track)  
**Status:** Research proposal + early measurement results

## Abstract

The deprecation (and subsequent partial rollback and ultimate abandonment) of third-party cookies in Chrome, combined with the limited adoption and later retirement of Privacy Sandbox proposals (Topics, Protected Audience API, etc.) by late 2025, has fundamentally altered the observable side-channels available for inferring tracker–advertiser data sharing. Header-bidding bid values (Kashf) and even personalized creative content (ATOM) are now mediated by complex first-party data graphs, consented clean-room joins, and alternative identity providers (UID2, RampID, ID5, etc.).

In this paper we conduct the first large-scale empirical study of what *remains* observable to a determined client-side or lightly instrumented server-side observer in 2026, and we design and evaluate new inference techniques that exploit:

- Residual leakage from Topics API and other experimental signals still deployed on a subset of sites.
- Creative selection and frequency capping signals visible through ad rendering differences and `navigator.storage` / partitioned storage interactions.
- Bid-stream differences in the remaining client-side Prebid deployments and hybrid S2S+client setups.
- "Data clean room echo" effects: when the same impression is won by multiple related advertisers through different paths, subtle differences in delivered creatives or landing-page parameters can reveal upstream data availability.
- Publisher-side first-party data activation signals (Seller-Defined Audiences, etc.) that sometimes leak whether a tracker-supplied segment was activated.

Using an updated measurement platform built on Playwright with modern stealth and Tranco-based persona construction, we construct 8,000 controlled personas, selectively expose or withhold the top 40 tracking organizations, and collect multi-signal outcomes across 40 high-traffic HB or programmatic sites. We recover 29 high-confidence direct and indirect tracker–advertiser relationships, many of which involve new intermediary clean-room and identity providers absent from 2020-era studies. We also quantify the decay in signal strength relative to the 2020 Kashf and 2022 ATOM results and identify which classes of data-sharing relationships have become effectively invisible to client-side or near-client measurement.

Our findings have immediate implications for the design of next-generation transparency tools, regulatory audit methods under evolving state privacy laws, and the research community's understanding of the limits of measurement in a first-party-dominated web.

## 1. Introduction

[Background on cookie deprecation timeline 2020–2025, Privacy Sandbox trajectory and abandonment, rise of clean rooms and alternative IDs. Why inference of data sharing remains critical: CCPA/CPRA "Do Not Sell/Share" obligations, GDPR Art. 30 records of processing, effectiveness of consent banners, etc.]

The original Kashf paper (2020) already foresaw the shift to server-side: "As server-side data sharing—which can be inferred by Kashf—becomes more prevalent, it is unclear whether the current generation of client-side blocking tools would continue to remain effective."

Six years later we can answer part of that question empirically and identify the *new* observable artifacts that have taken the place of legacy cookie syncing and client-side HB bids.

## 2. Evolution of Observable Artifacts (2020 → 2026)

| Era | Primary Signal Used by Inference Work | Visibility | Major Confounders |
|-----|---------------------------------------|------------|-------------------|
| 2016–2020 (Bashir, Kashf) | Retargeting creatives; HB bids (client Prebid) | High for participating entities | Waterfall dynamics, encryption (RTB) |
| 2020–2023 (ATOM era) | Personalized ad creative semantics | Medium | S2S HB removes bid visibility |
| 2024–2026 (this work) | Creative + Topics leakage + storage partitioning side-effects + clean-room echo + SDA activation | Low–Medium, highly fragmented | First-party graphs, consented joins, alt-ID envelopes, contextual + FPD fusion |

## 3. Measurement Methodology

### 3.1 Updated Persona and Crawling Infrastructure
- Tranco top-1M list (Dec 2025 snapshot) for site selection and category sampling.
- 40 "persona sites" + 4 high-intent transaction sites (updated from hotels.com etc. to current equivalents).
- Playwright + @sparticuz/chromium + puppeteer-extra-stealth + custom fingerprint randomization.
- Deterministic 90+ minute dwell after persona construction before measurement (as in original).
- Modular "Signal Extractor" interface so new observables can be added without rewriting the harness.

### 3.2 Selective Tracker Exposure
- Updated block lists for top-40 organizations (EasyList + EasyPrivacy + Disconnect + manual curation for new trackers and CDNs that carry tracking).
- Organizational bucketing extended with WHOIS + certificate transparency + public subsidiary data.
- Support for "partial blocking" experiments (block only specific endpoints of a tracker org to probe internal data routing).

### 3.3 Multi-Signal Collection
Detailed description of each new signal and its collection method.

## 4. Results

### 4.1 Signal Strength Decay
Quantitative comparison: fraction of advertisers for which tracker presence remains a statistically significant predictor of any observable outcome, 2020 vs 2026.

### 4.2 Recovered Relationships
- Overlap with the 15 relationships reported in the original Kashf Table 9.
- New relationships involving clean-room operators and alternative ID providers.
- Evidence of 2- and 3-hop indirect flows that would have been invisible or misattributed under Kashf/ATOM assumptions.

### 4.3 Invisible Relationships
Case studies of high-confidence externally known data sharing (from SEC filings, privacy policy cross-references, or CMP vendor announcements) that produce *no detectable change* in any client-visible signal under our interventions. These represent the new frontier where only server-side or insider access can provide transparency.

## 5. Implications for Privacy Research and Regulation

- Design recommendations for future "transparency by design" APIs or mandatory disclosure mechanisms.
- Updated threat model for tracker-blocking and consent-tooling authors.
- Concrete guidance for regulators performing technical audits under laws that grant a "right to know" with whom data is shared.

## 6. Open Science

We release:
- The full updated crawling and signal-extraction framework (successor to the original Kashf OpenWPM instrumentation).
- Sanitized, aggregated measurement datasets.
- Trained models and importance rankings for the 2026 measurement epoch.
- A living "observable signal registry" that the community can extend as new side-channels appear or disappear.

## 7. Limitations and Future Work

- Heavier reliance on ad creative analysis raises potential legal/ToS issues on some sites (we discuss our ethical review and rate-limiting).
- Some new signals are noisy or only present on a small fraction of impressions.
- The very success of first-party + clean-room strategies may mean that the most sensitive sharing is now the least measurable from the outside.

## References

[Original Kashf, ATOM, recent papers on Privacy Sandbox measurement and abandonment, clean room measurement studies, alternative ID papers, etc.]

---

**Direct Linkage to 2020 Limitations**

This paper primarily addresses:
- The *implicit* limitation that the inference technique is tightly coupled to a particular snapshot of client-visible artifacts (HB bids in 2020).
- The explicit concern about the long-term viability of client-side techniques as server-side practices (and now first-party/clean-room practices) advance.
- Provides the empirical "six years later" follow-up that the original authors could not have performed.

It also feeds improved signal definitions back into the CausalKashf framework proposed in the companion paper.