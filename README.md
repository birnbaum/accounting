# Reconcilable User-facing Cloud Carbon Accounting

## Mission

Metrics that make carbon data auditable and comparable across organizations (top-down, billing-based, auditable, comparable) are not the same metrics that help individual teams reduce emissions (bottom-up, granular, real-time, scoped to a team's agency).

While these two signals can by design not be identical, our position is that they must be **reconcilable**. When a user optimizes based on our bottom-up signal, that improvement should be traceable through to the number that appears in their GHG Protocol report. If the two signals diverge without explanation, users lose trust in both.

We focus on **location-based accounting** (GHG Protocol Scope 2 Guidance). Market-based accounting (RECs, PPAs) is inherently decoupled from physical consumption and therefore not actionable for our purpose (e.g. a team's emissions can change without their behavior changing).

**This framework serves two goals:**

- **For users:** Report an SCI-based metric per workload that, when summed over the month, reconciles with the provider's GHG Protocol-reported total. Users get an actionable signal they can trust.
- **For the ecosystem:** By making the provider's methodology quality visible — which optimization levers are blocked, which are rewarded — create market pressure for providers to adopt more granular methodologies (e.g. hourly $`I`$) that open up new optimization levers like temporal shifting.


## Context: Top-Down vs. Bottom-Up

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.

**Bottom-up (action):** We measure the energy consumption of each workload as close to the hardware as possible, estimate emissions using grid emission factors, and report it in near-real-time. This gives teams a clear signal for optimization but it misses facility overhead, embodied carbon, shared infrastructure, and other components that the top-down number includes.

The gap between these two is the **reconciliation bridge** $`\hat{\Delta}`$: everything the bottom-up measurement misses. Making this bridge transparent, predictable, and shrinking over time is the core technical challenge.

## Notation

### Indices

- $`t`$ — time (continuous; power measured at ~seconds, $`I`$ available at 5-min to hourly resolution)
- $`r`$ — cloud region
- $`T`$ — reporting period (typically one calendar month — the granularity at which provider actuals arrive)

The SCI is a rate and can be computed at any granularity. The monthly boundary only matters for reconciliation — that's when provider actuals arrive and we can calibrate.

### Inputs (measured / known)

| Symbol | Description |
|--------|-------------|
| $`E(t,r)`$ | Energy per job/service in kWh (measured, Layer 1; SCI's $`E`$). Fine-grained (sub-hourly). |
| $`I(t,r)`$ | Grid carbon intensity in gCO₂eq/kWh (from Electricity Maps / IEA; SCI's $`I`$). Available at 5-min to hourly resolution, but must be matched to the provider's accounting resolution for reconciliation. |
| $`C_\text{reported}(T,r)`$ | Provider's top-down reported carbon for reporting period $`T`$ (arrives ~15–21 days after month-end). |

### Outputs

| Symbol | Description |
|--------|-------------|
| $`\text{SCI}_j(t,r) = (O_j + M_j) / R_j`$ | Real-time, per-workload carbon rate (what the user sees). |
| $`\hat{C}(T,r)`$ | Our estimate of $`C_\text{reported}(T,r)`$, available before actuals arrive. |

### The Core Equation

$$\int_T \sum_j \text{SCI}_j(t,r) \cdot R_j(t)\;dt \;+\; \hat{\Delta}(T,r) \;=\; \hat{C}(T,r) \;\approx\; C_\text{reported}(T,r)$$

Where:
- The integral sums all bottom-up SCI scores across jobs and time within reporting period $`T`$
- $`\hat{\Delta}(T,r)`$ is the **reconciliation bridge** — everything the bottom-up measurement misses (facility overhead, idle capacity, Scope 1, other Scope 3, allocation artifacts)

The model's job: estimate $`\hat{\Delta}`$ so that $`\hat{C}`$ predicts $`C_\text{reported}`$ before actuals arrive. The SCI scores themselves are available in real time at fine granularity; the reconciliation bridge is calibrated monthly when actuals arrive.

### Model Parameters (components of $`\hat{\Delta}`$)

| Parameter | Meaning |
|-----------|---------|
| $`\alpha_\text{PUE}(r,t)`$ | Facility/IT energy ratio (Power Usage Effectiveness) |
| $`E_\text{idle}(r,t)`$ | Idle/shared energy not captured by per-job measurement |
| $`M(r,t)`$ | Amortized embodied carbon of hardware and buildings |
| $`\alpha_{s1}(r)`$ | Scope 1 emissions ratio (diesel, refrigerants) |
| $`\alpha_{s3}(r)`$ | Other Scope 3 emissions ratio (FERA, transport, waste) |
| $`\beta_\text{alloc}(r)`$ | Allocation scaling factor (physical vs. usage-based) |

### SCI Reference

$`E`$, $`I`$, $`M`$, $`R`$ follow SCI (ISO/IEC 21031:2024) naming. See [`references/SCI.md`](references/SCI.md) for the full specification.

## Design: Three-Layer Architecture

### Layer 1 — Energy Measurement

Ground truth. Energy consumption at job/service level via CPU/GPU power modeling (utilization × TDP), hardware counters (RAPL, NVML), or direct metering. Provider-agnostic.

**Output:** $`E(t,r)`$ in kWh at sub-hourly granularity. Uncertainty ~2–5%.

### Layer 2 — Reconciliation Model

Estimates $`\hat{\Delta}(T,r)`$ — the reconciliation bridge. Given known inputs ($`E`$, $`I`$), the model treats everything else — PUE, idle allocation, embodied carbon, Scope 1, other Scope 3, customer allocation — as **parameters** with priors and uncertainty. Calibrated monthly when $`(C_\text{reported}, \int \text{SCI})`$ pairs arrive.

This is where the novel design work lives. See **Estimation Framework** below for the full model specification.

**Output:** $`\hat{C}(T,r)`$ in tCO₂e with posterior credible intervals, reconciled monthly against provider actuals.

### Layer 3 — User-Facing Signal

Users see $`\text{SCI}_j = (O_j + M_j) / R_j`$ per workload in real time — carbon per unit of work scoped to their team's agency. Roll-up into GHG Protocol reporting view shows absolute totals plus their allocated share of $`\hat{\Delta}`$, with full methodology transparency into how the bridge was allocated.

**Output:** Per-team dashboards showing both the action metric (optimize this) and the reporting metric (report this), with the reconciliation bridge between them. Each number carries uncertainty and fractional decomposition.

## Why the Framework Must Be Provider-Adaptive

Not all optimization levers are rewarded by all providers:

- **Temporal shifting** — only reconcilable if the provider uses sub-monthly emission factors (currently only GCP uses hourly factors internally; AWS and Azure use monthly averages).
- **Compute efficiency** — directly reconcilable on physical allocation providers (GCP, AWS foundational services); approximately reconcilable on Azure (usage-based, correlated but undisclosed derivation).
- **Spatial shifting** — reconcilable across all three providers (all use regional emission factors).

The framework must be **parametrized by a provider profile** encoding how each provider accounts for carbon.

When a provider adopts finer-grained methodology (e.g. hourly $`I`$), new optimization levers become reconcilable. Our framework makes this visible — showing users which optimizations are "blocked" by their provider's methodology creates demand for better accounting. This is the ecosystem pressure goal in action.

## Provider Profiles

The framework is parametrized by a **provider profile** encoding each provider's accounting methodology. Full schema definition, populated profiles for AWS/GCP/Azure, reconcilability analysis, and minimum viable profile requirements are in [`SCHEMA.md`](SCHEMA.md).

Key finding: **Not all optimization levers are equally reconcilable across providers**. GCP's physical allocation makes most energy-based optimizations directly reconcilable. AWS's hybrid approach is direct for foundational services, approximate for managed services. Azure's usage-based allocation correlates with physical usage but the undisclosed derivation limits confidence.

- **Universally safe:** Spatial shifting, eliminate idle resources, right-sizing.
- **Provider-dependent:** Compute efficiency, architecture choice (strongest on GCP and AWS foundational; approximate on Azure), temporal shifting (GCP).

## Estimation Framework

### Goal

Estimate $`\hat{\Delta}(T,r)`$ — the reconciliation bridge — in real time, before provider actuals arrive. The bottom-up SCI is computed in real time; the estimation framework's job is to estimate the bridge so that $`\hat{C}`$ predicts $`C_\text{reported}`$.

### $`\hat{\Delta}`$ Decomposition

The bridge decomposes into the components that the bottom-up SCI misses:

$$\hat{\Delta}(T,r) = \Delta_\text{PUE} + \Delta_\text{idle} + \Delta_\text{scope1} + \Delta_\text{embodied} + \Delta_\text{other-s3} + \Delta_\text{alloc}$$

Where:

- $`\Delta_\text{PUE}(T,r) = (\alpha_\text{PUE}(r,t) - 1) \cdot \int_T E(t,r)\,dt \cdot \bar{I}(T,r)`$ — facility overhead energy × carbon intensity
- $`\Delta_\text{idle}(T,r) = E_\text{idle}(r,t) \cdot \bar{I}(T,r)`$ — idle/shared capacity emissions
- $`\Delta_\text{scope1}(T,r) = \alpha_{s1}(r) \cdot E_\text{facility}(T,r)`$ — diesel, refrigerants
- $`\Delta_\text{embodied}(T,r) = M(r,T)`$ — amortized hardware/buildings
- $`\Delta_\text{other-s3}(T,r) = \alpha_{s3}(r) \cdot \int_T E(t,r)\,dt`$ — FERA, transport, waste
- $`\Delta_\text{alloc}(T,r)`$ — allocation adjustment ($`\beta_\text{alloc}`$)

Note: $`\bar{I}(T,r)`$ is $`I`$ averaged at the provider's accounting resolution (monthly for AWS/Azure, hourly for GCP). $`E_\text{facility} = E \cdot \alpha_\text{PUE} + E_\text{idle}`$ is the total facility energy.

### Parameter Table (parameters of $`\hat{\Delta}`$)

| Parameter | Meaning | Prior | Uncertainty | Cadence | Sensitivity |
|---|---|---|---|---|---|
| $`\alpha_\text{PUE}(r,t)`$ | Facility/IT energy ratio | ~1.1–1.3 (sustainability reports) | ±10–15% | Seasonal | High |
| $`E_\text{idle}(r,t)`$ | Idle/shared energy | ~15–30% of $`E`$ | ±20–40% | Monthly | Medium |
| $`M(r,t)`$ | Embodied carbon (SCI: $`M`$) | Provider LCA / SCHEMA.md | ±15–30% | Quarterly | Medium–High |
| $`\alpha_{s1}(r)`$ | Scope 1 ratio | ~0.01–0.03 | ±30–50% | Annual | Low |
| $`\alpha_{s3}(r)`$ | Other Scope 3 ratio | ~0.05–0.15 | ±20–35% | Annual | Low–Medium |
| $`\beta_\text{alloc}(r)`$ | Allocation scaling | Physical ~1.0; usage-based ~0.9–1.1 | ±5–30% | Monthly | High |

**Known inputs** (not fitted): $`E(t,r)`$ from Layer 1 measurement, $`I(t,r)`$ from Electricity Maps / IEA.

### Bayesian Inference

**Priors:** Log-normal for multiplicative parameters ($`\alpha_\text{PUE}`$, $`\beta_\text{alloc}`$); normal for additive parameters ($`E_\text{idle}`$, $`M`$).

**Likelihood:**

$$C_\text{reported}(T,r) \sim \mathcal{N}\big(\hat{C}(T,r;\,\boldsymbol{\theta}),\;\sigma^2_\text{obs}\big)$$

**Posterior:**

$$p(\boldsymbol{\theta} \mid \mathcal{D}) \propto \prod_{T} p\big(C_\text{reported}(T) \mid \boldsymbol{\theta}\big) \cdot p(\boldsymbol{\theta})$$

Updated monthly when $(E, C_\text{reported})$ pairs arrive.

**Cold start:** Months 1–3 prior-dominated (±30–50% CI). Months 6–12 posterior-driven.

**Diagnostics on $`\varepsilon = C_\text{reported} - \hat{C}`$:**
- Seasonal autocorrelation → $`\alpha_\text{PUE}`$ needs Fourier terms
- Utilization correlation → $`E_\text{idle}`$ mis-specified
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

1. **Identifiability:** With $`I`$ known, $`\alpha_\text{PUE}`$ and $`E_\text{idle}`$ are the main degrees of freedom in the energy domain. Are they separable from monthly $(E, C_\text{reported})$ pairs alone, or do we need side information (e.g. published PUE)?

2. **Non-stationarity:** Methodology changes create regime shifts. Change-point detection vs. short lookback window?

3. **Minimum viable data:** How many months of $(E, C_\text{reported})$ pairs before the model is usable per provider?

## Repository Structure

```
├── README.md                              # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md       # detailed provider methodology comparison
├── SCHEMA.md                              # provider profile schema, populated profiles, reconcilability analysis
├── references/SCI.md                       # Software Carbon Intensity standard
├── references/SCI_AI.md                   # SCI for AI standard
```
