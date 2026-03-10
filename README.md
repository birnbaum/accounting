# Reconcilable User-facing Cloud Carbon Accounting

## Mission

Metrics that make carbon data auditable and comparable across organizations (top-down, billing-based, auditable, comparable) are not the same metrics that help individual teams reduce emissions (bottom-up, granular, real-time, scoped to a team's agency).

While these two signals can by design not be identical, our position is that they must be **reconcilable**. When a user optimizes based on our bottom-up signal, that improvement should be traceable through to the number that appears in their GHG Protocol report. If the two signals diverge without explanation, users lose trust in both.

We focus on **location-based accounting** (GHG Protocol Scope 2 Guidance). Market-based accounting (RECs, PPAs) is inherently decoupled from physical consumption and therefore not actionable for our purpose (e.g. a team's emissions can change without their behavior changing).


## Context: Top-Down vs. Bottom-Up

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.

**Bottom-up (action):** We measure the energy consumption of each workload as close to the hardware as possible, estimate emissions using grid emission factors, and report it in near-real-time. This gives teams a clear signal for optimization but it misses facility overhead, embodied carbon, shared infrastructure, and other components that the top-down number includes.

The gap between these two is the **overhead delta** $`\Delta`$: the difference between the sum of all bottom-up signals and the provider's top-down reported total. Making this delta transparent, predictable, and shrinking over time is the core technical challenge.

## Notation

We adopt variable names from the [SCI specification](references/SCI.md) (ISO/IEC 21031:2024) where possible and extend them for the reconciliation model. All quantities are indexed by month $`t`$ and cloud region $`r`$.

**SCI core variables:**

| Symbol | SCI meaning | Our usage |
|--------|------------|-----------|
| $`E`$ | Energy consumed by a software system (kWh) | $`E_\text{IT}(t,r)`$ — IT energy per job/service (measured). Our SCI boundary includes datacenter operations, so we model $`E_\text{facility} = E_\text{IT} \cdot \alpha_\text{PUE} + E_\text{idle}`$ as the SCI spec requires. |
| $`I`$ | Region-specific carbon intensity (gCO₂eq/kWh) | $`I(r,t)`$ — grid emission factor. Known input from Electricity Maps / IEA, matched to provider accounting resolution. |
| $`M`$ | Embodied emissions of hardware (gCO₂eq) | $`M(r,t)`$ — amortized hardware + buildings. Model parameter with prior (±15–30%), since provider LCA data is approximate. |
| $`O`$ | Operational emissions: $`O = E \cdot I`$ | $`O = E_\text{facility} \cdot I`$ — operational carbon including datacenter overhead |
| $`R`$ | Functional unit | Per request, per pipeline run, per training epoch, etc. |
| $`C`$ | Total carbon: $`C = (O + M) \text{ per } R`$ | $`\hat{C}(t,r)`$ — our full model estimate of the provider's reported carbon |

**Reconciliation model parameters** (beyond SCI):

| Symbol | Meaning |
|--------|---------|
| $`\alpha_\text{PUE}(r,t)`$ | Facility/IT energy ratio (Power Usage Effectiveness) |
| $`E_\text{idle}(r,t)`$ | Idle/shared energy not captured by per-job measurement |
| $`E_\text{facility}(r,t)`$ | Total facility energy: $`E_\text{IT} \cdot \alpha_\text{PUE} + E_\text{idle}`$ |
| $`\alpha_{s1}(r)`$ | Scope 1 emissions ratio (diesel, refrigerants) |
| $`\alpha_{s3}(r)`$ | Other Scope 3 emissions ratio (FERA, transport, waste) |
| $`\beta_\text{alloc}(r)`$ | Allocation scaling factor (physical vs. usage-based) |

**Our SCI boundary** includes datacenter operations (PUE, idle capacity), as the SCI spec requires when the boundary covers data center workloads. A straightforward SCI computation would yield $`\text{SCI} = (E_\text{facility} \cdot I + M) / R`$. The reconciliation model goes further: it adds Scope 1, other Scope 3, and an allocation adjustment to bridge from this bottom-up SCI to the provider's top-down reported total.

## Design: Three-Layer Architecture

### Layer 1 — Energy Measurement

Ground truth. Energy consumption at job/service level via CPU/GPU power modeling (utilization × TDP), hardware counters (RAPL, NVML), or direct metering. Provider-agnostic.

**Output:** $`E_\text{IT}(t,r)`$ in kWh, sub-hourly granularity. Uncertainty ~2–5%.

### Layer 2 — Reconciliation Model

Bayesian parametric model mapping $`E_\text{IT}`$ $`\to`$ $`\hat{C}_\text{reported}`$. Given known inputs ($`E_\text{IT}`$, $`I`$), the model treats everything else — PUE, idle allocation, embodied carbon, Scope 1, other Scope 3, customer allocation — as **parameters** with priors and uncertainty. Fitted monthly on provider actuals.

This is where the novel design work lives. See **Estimation Framework** below for the full model specification.

**Output:** $`\hat{C}(t,r)`$ in tCO₂e with posterior credible intervals, reconciled monthly against provider actuals.

### Layer 3 — User-Facing Signal

Users see an SCI-style rate metric — carbon per unit of work (per $`R`$) — scoped to their team's agency. Roll-up into GHG Protocol reporting view shows absolute totals plus allocated overhead share, with full methodology transparency.

**Output:** Per-team dashboards showing both the action metric (optimize this) and the reporting metric (report this), with the reconciliation bridge between them. Each number carries uncertainty and fractional decomposition.

## Why the Framework Must Be Provider-Adaptive

Not all optimization levers are rewarded by all providers:

- **Temporal shifting** — only reconcilable if the provider uses sub-monthly emission factors (currently only GCP uses hourly factors internally; AWS and Azure use monthly averages).
- **Compute efficiency** — directly reconcilable on physical allocation providers (GCP, AWS foundational services); approximately reconcilable on Azure (usage-based, correlated but undisclosed derivation).
- **Spatial shifting** — reconcilable across all three providers (all use regional emission factors).

The framework must be **parametrized by a provider profile** encoding how each provider accounts for carbon.

## Provider Profiles

The framework is parametrized by a **provider profile** encoding each provider's accounting methodology. Full schema definition, populated profiles for AWS/GCP/Azure, reconcilability analysis, and minimum viable profile requirements are in [`SCHEMA.md`](SCHEMA.md).

Key finding: **Not all optimization levers are equally reconcilable across providers**. GCP's physical allocation makes most energy-based optimizations directly reconcilable. AWS's hybrid approach is direct for foundational services, approximate for managed services. Azure's usage-based allocation correlates with physical usage but the undisclosed derivation limits confidence.

**Universally safe:** Spatial shifting, eliminate idle resources, right-sizing.
**Provider-dependent:** Compute efficiency, architecture choice (strongest on GCP and AWS foundational; approximate on Azure).
**Currently unavailable:** Temporal shifting (no provider exposes sub-monthly data to customers).

## Estimation Framework

### Goal

Estimate $`\hat{C}_\text{reported}`$ in real time from $`E_\text{IT}`$, before provider actuals arrive. The reconciliation bridge is predictive, not retrospective.

### Model Structure

**Energy domain** — the SCI boundary includes datacenter operations, so we expand $`E_\text{IT}`$ to facility-level energy:

$$E_\text{facility}(t,r) = E_\text{IT}(t,r) \cdot \alpha_\text{PUE}(r,t) + E_\text{idle}(r,t)$$

**Carbon conversion** — $`I(r,t)`$ is a known input (Electricity Maps / IEA), matched to the provider's accounting resolution:

$$O(t,r) = E_\text{facility}(t,r) \cdot I(r,t)$$

**Additional scopes:**

$$C_\text{scope1}(t,r) = \alpha_{s1}(r) \cdot E_\text{facility}(t,r)$$

$$C_\text{embodied}(t,r) = M(r,t)$$

$$C_\text{other-s3}(t,r) = \alpha_{s3}(r) \cdot E_\text{IT}(t,r)$$

**Full model:**

$$\hat{C}(t,r) = \beta_\text{alloc}(r) \cdot \Big[E_\text{facility} \cdot \big(I + \alpha_{s1}\big) + M + \alpha_{s3} \cdot E_\text{IT}\Big]$$

where $`E_\text{facility} = E_\text{IT} \cdot \alpha_\text{PUE} + E_\text{idle}`$ and $`I`$ is a known input. The model parameters $`\boldsymbol{\theta} = \{\alpha_\text{PUE}, E_\text{idle}, M, \alpha_{s1}, \alpha_{s3}, \beta_\text{alloc}\}`$ are fitted via Bayesian inference.

### Parameter Table

| Parameter | Meaning | Prior | Uncertainty | Cadence | Sensitivity |
|---|---|---|---|---|---|
| $`\alpha_\text{PUE}(r,t)`$ | Facility/IT energy ratio | ~1.1–1.3 (sustainability reports) | ±10–15% | Seasonal | High |
| $`E_\text{idle}(r,t)`$ | Idle/shared energy | ~15–30% of $`E_\text{IT}`$ | ±20–40% | Monthly | Medium |
| $`M(r,t)`$ | Embodied carbon (SCI: $`M`$) | Provider LCA / SCHEMA.md | ±15–30% | Quarterly | Medium–High |
| $`\alpha_{s1}(r)`$ | Scope 1 ratio | ~0.01–0.03 | ±30–50% | Annual | Low |
| $`\alpha_{s3}(r)`$ | Other Scope 3 ratio | ~0.05–0.15 | ±20–35% | Annual | Low–Medium |
| $`\beta_\text{alloc}(r)`$ | Allocation scaling | Physical ~1.0; usage-based ~0.9–1.1 | ±5–30% | Monthly | High |

**Known inputs** (not fitted): $`E_\text{IT}(t,r)`$ from Layer 1 measurement, $`I(r,t)`$ from Electricity Maps / IEA.

### Bayesian Inference

**Priors:** Log-normal for multiplicative parameters ($`\alpha_\text{PUE}`$, $`\beta_\text{alloc}`$); normal for additive parameters ($`E_\text{idle}`$, $`M`$).

**Likelihood:**

$$C_\text{reported}(t,r) \sim \mathcal{N}\big(\hat{C}(t,r;\,\boldsymbol{\theta}),\;\sigma^2_\text{obs}\big)$$

**Posterior:**

$$p(\boldsymbol{\theta} \mid \mathcal{D}) \propto \prod_{t} p\big(C_\text{reported}(t) \mid \boldsymbol{\theta}\big) \cdot p(\boldsymbol{\theta})$$

Updated monthly when $(E_\text{IT}, C_\text{reported})$ pairs arrive.

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

1. **Identifiability:** With $`I`$ known, $`\alpha_\text{PUE}`$ and $`E_\text{idle}`$ are the main degrees of freedom in the energy domain. Are they separable from monthly $(E_\text{IT}, C_\text{reported})$ pairs alone, or do we need side information (e.g. published PUE)?

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
