# Paper structure options (saved 2026-05-22)

Captured before §3 rework so the structural decision isn't lost.
The §3 rewrite of 2026-05-22 keeps the current paper structure (Option A / D-ish) and tightens §3 to one page without restructuring §4–§8.

## Context

The user raised a real concern after the §3 outline: the SOTA → metric → reality flow feels dispersed because providers are named in §3 (gaps) and re-visited in §5 (levers).
The Scaleway daily + actual-CPU finding may also shift which providers carry §5's empirical weight.
We agreed to proceed with §3 now under the current structure and revisit after the Scaleway investigation.

## Option A — Current structure (SOTA → metric → reality)

```
§1 Intro
§2 Background (SCI / GSF)
§3 SOTA in cloud carbon accounting     ← survey, taxonomy, the gap
§4 rSCI definition (residual decomposition)
§5 Reality check (lever × provider, Shapley figure)
§6 Discussion / §7 Related / §8 Conclusion
```

Why it feels dispersed: §3 names the providers and their pathologies; §5 returns to the same providers with a different lens.
Each §3 finding has a §5 echo, and the rSCI definition sits between them, breaking the empirical thread.

Best for: textbook scaffolding, standard reviewer expectations.
Worst for: vision-track punch on a 6-page paper.

## Option B — Metric-first (rSCI → providers under that lens)

```
§3 rSCI: the residual decomposition  ← metric upfront, abstractly
§4 What this looks like in practice  ← all provider work merges here, organized by rSCI components
§5 Implications / what's reconcilable today
```

Why it might fit: every provider claim is read *through* the rSCI lens.
AWS-foundational appears once, in the rSCI-component subsection where it actually matters.
The Scaleway daily + actual-CPU finding becomes the natural "what reconciliation could look like in the limit" example — a positive existence proof instead of just a list of gaps.

Risk: SoCC vision-track reviewers may want to see the gap before being convinced a new metric is needed.
Front-loading the metric assumes the reader trusts the framing.

## Option C — Reality-first (empirical lead, metric distilled)

```
§3 What customers can actually see  ← lead with levers/observations
§4 Why these patterns exist          ← taxonomy as explanation, not survey
§5 rSCI: a metric that holds the gap explicit  ← derived, not imposed
```

Why it might fit: each finding earns its place because it motivates the next move.
The metric is the conclusion of the survey, not a parallel artifact.

Risk: rSCI gets less standalone airtime — a reviewer asking "what is the contribution?" might miss it.

## Option D — Hybrid: tight §3 + tight §5, §4 as the bridge

```
§3 SOTA in 1 page             ← breadth-table + 4-axis figure + footnote-2 quote. No per-provider deep-dives.
§4 rSCI (residual bridge)     ← compact metric definition + why it's needed
§5 Reconcilability today      ← 1–2 case studies (Scaleway? Azure Frankfurt?), not a full lever × provider matrix
```

Why it might fit: same shape as A, but each section does one job and per-provider material concentrates in §5 around 1–2 deep cases.
§3 stops at "here's the shape of the field" and doesn't try to be exhaustive.

Best for: keeping the existing structure while ditching the dispersion.
Lowest rewrite cost from where the paper is now.

## Decision rule

Wait for Scaleway investigation, then choose between B and D.

- If Scaleway's daily + actual-CPU pipeline is a usable reconciliation testbed (load test moves the daily number; API yields programmatic access; per-VM signal is load-sensitive): **Option B** is the winner.
  Paper's punch becomes "here's a metric and a provider where it works today; here's why it doesn't yet work for the other 10."
- If Scaleway's daily data turns out cosmetic (daily dashboard but factors baked in monthly upstream, or Boavizta profile too coarse to reconcile against bottom-up): **Option D** is the safe path.
  Keep current structure but tighten §3 and pivot §5 to whichever case study survives.

## Questions to answer before the Option-B-vs-D call

1. Does Scaleway's daily number actually move when a VM goes from idle to busy?
2. Is the Boavizta consumption profile parameterized by real sampled CPU%, or by a billing-period average?
3. Can daily numbers be extracted programmatically via the API for a reconciliation experiment?
4. What's the smallest time-window where the Scaleway number is stable enough to be a reference?

If (1) and (2) come back "yes — load-sensitive", Option B wins.
If they come back "no", Option D, and we keep things close to the current frame.

## What this §3 rewrite assumes

The §3 rewrite of 2026-05-22 was done under Option D (current structure, tight §3, no restructuring §4–§8).
If the Scaleway investigation pushes the paper to Option B later, §3 becomes shorter still and most of its content shifts into the rSCI-lens version of §4.
The 4-axis figure and the tier-breadth narrative are structure-agnostic and survive either choice.
