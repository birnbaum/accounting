# Reconcilable User-facing Cloud Carbon Accounting

You are a researcher.

## Mission

Provide **actionable carbon signals** to cloud users that are **reconcilable** with their GHG Protocol-compliant reported carbon footprint.

Top-down reported footprints (auditable, comparable, delayed) and bottom-up measured signals (granular, real-time, actionable) serve different purposes with genuine trade-offs. They cannot be identical, but they must be **reconcilable**: optimizing on the bottom-up signal must trace through to the GHG Protocol number. We focus on **location-based accounting** (Scope 2 Guidance) — market-based instruments (RECs, PPAs) decouple carbon from physical consumption and are not actionable.

## Context: Top-Down vs. Bottom-Up

**Top-down (reporting):** Provider computes total monthly footprint from utility bills, diesel, refrigerant losses, and amortized embodied carbon, then allocates to customers. Auditable, comparable, delayed (~15–21 days). Tells you the size of the problem.

**Bottom-up (action):** We measure energy per workload near the hardware, estimate emissions via grid emission factors, report in near-real-time. Clear optimization signal, but captures only direct compute energy — missing facility overhead, embodied carbon, shared infrastructure.

The **overhead delta** — the gap between summed bottom-up signals and the provider's top-down total — is the core technical challenge.

## Design: Three-Layer Architecture

### Layer 1 — Energy Measurement

Ground truth. Energy consumption at job/service level via CPU/GPU power modeling (utilization × TDP), hardware counters (RAPL, NVML), or direct metering. Provider-agnostic.

**Output:** $E_\text{IT}(t,r)$ in kWh, sub-hourly granularity. Uncertainty ~2–5%.

### Layer 2 — Reconciliation Model

Bayesian parametric model mapping $E_\text{IT} \to \hat{C}_\text{reported}$. Every step after energy measurement — PUE, emission factor, idle allocation, Scope 1, embodied carbon, other Scope 3, customer allocation — is a **model parameter** with prior and uncertainty. Fitted monthly on provider actuals.

This is where the novel design work lives. See **Estimation Framework** below for the full model specification.

**Output:** $\hat{C}(t,r)$ in tCO₂e with posterior credible intervals, reconciled monthly against provider actuals.

### Layer 3 — User-Facing Signal

Users see an SCI-style rate metric — carbon per unit of work (per request, per pipeline run, per training epoch) — scoped to their team's agency. Roll-up into GHG Protocol reporting view shows absolute totals plus allocated overhead share, with full methodology transparency.

**Output:** Per-team dashboards showing both the action metric (optimize this) and the reporting metric (report this), with the reconciliation bridge between them. Each number carries uncertainty and fractional decomposition.

## Why the Framework Must Be Provider-Adaptive

Not all optimization levers are rewarded by all providers:

- **Temporal shifting** — only reconcilable if the provider uses sub-monthly emission factors (currently only GCP uses hourly factors internally; AWS and Azure use monthly averages).
- **Compute efficiency** — directly reconcilable on physical allocation providers (GCP, AWS foundational services); approximately reconcilable on Azure (usage-based, correlated but undisclosed derivation).
- **Spatial shifting** — reconcilable across all three providers (all use regional emission factors).

The framework must be **parametrized by a provider profile** encoding how each provider accounts for carbon.

## The Provider Profile Schema

The framework is parametrized by a **provider profile** encoding each provider's accounting methodology. Full schema definition, populated profiles for AWS/GCP/Azure, reconcilability analysis, and minimum viable profile requirements are in [`SCHEMA.md`](SCHEMA.md).

Key finding: GCP's physical allocation makes most energy-based optimizations directly reconcilable. AWS's hybrid approach is direct for foundational services, approximate for managed services. Azure's usage-based allocation correlates with physical usage but the undisclosed derivation limits confidence.

**Universally safe:** Spatial shifting, eliminate idle resources, right-sizing.
**Provider-dependent:** Compute efficiency, architecture choice (strongest on GCP and AWS foundational; approximate on Azure).
**Currently unavailable:** Temporal shifting (no provider exposes sub-monthly data to customers).

## Estimation Framework

### Goal

Estimate $\hat{C}_\text{reported}$ in real time from $E_\text{IT}$, before provider actuals arrive. The reconciliation bridge is predictive, not retrospective.

### Model Structure

**Energy domain** — apply PUE before carbon conversion:

$$E_\text{facility}(t,r) = E_\text{IT}(t,r) \cdot \alpha_\text{PUE}(r,t) + E_\text{idle}(r,t)$$

**Carbon conversion** — $\text{EF}$ is a model parameter with prior (from Electricity Maps / IEA), not a known constant:

$$C_\text{scope2}(t,r) = E_\text{facility}(t,r) \cdot \text{EF}(r,t)$$

**Additional scopes:**

$$C_\text{scope1}(t,r) = \alpha_{s1}(r) \cdot E_\text{facility}(t,r)$$

$$C_\text{embodied}(t,r) = \beta_\text{emb}(r,t)$$

$$C_\text{other-s3}(t,r) = \alpha_{s3}(r) \cdot E_\text{IT}(t,r)$$

**Full model:**

$$\hat{C}(t,r) = \beta_\text{alloc}(r) \cdot \Big[\big(E_\text{IT} \cdot \alpha_\text{PUE} + E_\text{idle}\big) \cdot \big(\text{EF} + \alpha_{s1}\big) + \beta_\text{emb} + \alpha_{s3} \cdot E_\text{IT}\Big]$$

### Parameter Table

| Parameter | Meaning | Prior | Uncertainty | Cadence | Sensitivity |
|---|---|---|---|---|---|
| $\alpha_\text{PUE}(r,t)$ | Facility/IT energy ratio | ~1.1–1.3 (sustainability reports) | ±10–15% | Seasonal | High |
| $\text{EF}(r,t)$ | Grid carbon intensity | Electricity Maps / IEA | ±5–15% | Monthly–annual | High |
| $E_\text{idle}(r,t)$ | Idle/shared energy | ~15–30% of $E_\text{IT}$ | ±20–40% | Monthly | Medium |
| $\alpha_{s1}(r)$ | Scope 1 ratio | ~0.01–0.03 | ±30–50% | Annual | Low |
| $\beta_\text{emb}(r,t)$ | Embodied carbon baseline | Provider LCA / SCHEMA.md | ±15–30% | Quarterly | Medium–High |
| $\alpha_{s3}(r)$ | Other Scope 3 ratio | ~0.05–0.15 | ±20–35% | Annual | Low–Medium |
| $\beta_\text{alloc}(r)$ | Allocation scaling | Physical ~1.0; usage-based ~0.9–1.1 | ±5–30% | Monthly | High |

### Bayesian Inference

**Priors:** Log-normal for multiplicative parameters ($\alpha_\text{PUE}$, $\text{EF}$, $\beta_\text{alloc}$); normal for additive parameters ($E_\text{idle}$, $\beta_\text{emb}$).

**Likelihood:**

$$C_\text{reported}(t,r) \sim \mathcal{N}\big(\hat{C}(t,r;\,\boldsymbol{\theta}),\;\sigma^2_\text{obs}\big)$$

**Posterior:**

$$p(\boldsymbol{\theta} \mid \mathcal{D}) \propto \prod_{t} p\big(C_\text{reported}(t) \mid \boldsymbol{\theta}\big) \cdot p(\boldsymbol{\theta})$$

Updated monthly when $(E_\text{IT}, C_\text{reported})$ pairs arrive.

**Cold start:** Months 1–3 prior-dominated (±30–50% CI). Months 6–12 posterior-driven.

**Diagnostics on $\varepsilon = C_\text{reported} - \hat{C}$:**
- Seasonal autocorrelation → $\alpha_\text{PUE}$ needs Fourier terms
- Utilization correlation → $E_\text{idle}$ mis-specified
- Step change → methodology update (check provider profile version)

### Output Format

```
Estimated footprint: 12.3 tCO₂e [10.8 — 14.1, 90% CI]

Component                               Estimate    σ       Share
────────────────────────────────────────────────────────────────
IT energy (measured)                    4.96 tCO₂e  ±5%      40%
Facility overhead (PUE)                 1.24 tCO₂e  ±12%     10%
Idle/shared capacity                    1.85 tCO₂e  ±25%     15%
Scope 1                                 0.12 tCO₂e  ±35%      1%
Embodied carbon                         2.96 tCO₂e  ±18%     24%
Other Scope 3                           0.74 tCO₂e  ±25%      6%
Allocation adjustment                   0.49 tCO₂e  ±30%      4%

Model maturity: 8 months. Last ε: +0.3 tCO₂e (2.4%).
```

## Open Design Questions

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific open questions.

1. **Identifiability:** $\alpha_\text{PUE}$ and $\text{EF}$ are multiplicatively coupled. Separable from monthly data alone, or need side information (published PUE)?

2. **Non-stationarity:** Methodology changes create regime shifts. Change-point detection vs. short lookback window?

3. **Minimum viable data:** How many months of $(E_\text{IT}, C_\text{reported})$ pairs before the model is usable per provider?

## Repository Structure

```
├── README.md                              # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md       # detailed provider methodology comparison
├── SCHEMA.md                              # provider profile schema, populated profiles, reconcilability analysis
├── references/SCI.md                       # Software Carbon Intensity standard
├── references/SCI_AI.md                   # SCI for AI standard
```
