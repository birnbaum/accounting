# Reconcilable User-facing Cloud Carbon Accounting

## Mission

Metrics that make cloud carbon data auditable and comparable across organizations are not the same metrics that help individual teams reduce emissions.

- **Top-down reporting** is billing-aligned, standardized, delayed, and anchored in provider data such as utility bills, diesel consumption, refrigerant losses, and embodied hardware/building emissions.
- **Bottom-up action metrics** are granular, near-real-time, and scoped to what a team can change: code efficiency, workload placement, resource sizing, and scheduling.

These two signals are not, and should not be, identical. Our claim is weaker and more practical: they must be **reconcilable**. If a team improves its bottom-up signal, that improvement should be traceable through to the cloud provider's reported number at the reporting boundary the provider actually exposes. If the two diverge without explanation, users lose trust in both.

We focus on **location-based accounting**. Market-based accounting is intentionally excluded from the action metric because it is decoupled from physical consumption and therefore weak as an operational signal.

This framework serves two goals:

- **For users:** provide an SCI-based action metric per workload and per provider-aligned service slice, then reconcile that signal to the provider's delayed GHG-style report.
- **For the ecosystem:** make provider methodology quality visible by showing which optimization levers are directly rewarded, only approximately rewarded, or structurally blocked by provider accounting choices.

## Context: Top-Down vs. Bottom-Up

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.

**Bottom-up (action):** We measure workload energy as close to the hardware as possible, combine it with location-based carbon intensity, and report an SCI-style signal in near real time. This gives teams an optimization signal they can act on, but by itself it does not fully capture facility overhead, idle/shared capacity, provider-specific allocation effects, or all Scope 1/3 components.

We call the gap between these two **reconciliation bridge**. That bridge has two distinct sources:

1. **Residual carbon inside a provider reporting slice** that the observable real-time metric does not directly capture.
2. **Boundary mismatch** between what we instrument and what the provider reports.

The main design problem is not to eliminate that bridge by definition, but to make it explicit, predictable, and small enough that users can understand how action-level improvements flow into reporting-level totals.

## Boundary Model

The boundary needs to be explicit.

- **Observable boundary:** the workloads and hardware reservations we can instrument in near real time.
- **Provider reporting boundary:** the finest slice at which the provider exposes carbon data to the customer.

The reconciliation unit is the **provider reporting slice**, not an abstract "job." In practice this means:

- **AWS:** `account × service × region × month`
- **GCP:** `project × SKU × region × month`
- **Azure:** `subscription × service_category × region × month`

Every measured workload event must map to one or more provider reporting slices. For distributed workloads, we split the workload across slices by observed resource share. This matters because reconciling at the finest provider-exposed slice reduces uncertainty: the bridge only needs to explain residuals inside a slice, not cross-service mixing introduced by aggregating too early.

If the observable boundary fully covers the provider reporting slice, the coverage-gap term should be near zero. If it does not, that gap must be made explicit rather than silently absorbed into "model error."

## Notation

### Indices

- $`i`$ — measured workload execution, component, or reservation
- $`b`$ — provider reporting slice
- $`t`$ — time within a reporting month
- $`T`$ — reporting month

### Inputs

| Symbol | Description |
|--------|-------------|
| $`E_i(t)`$ | Measured IT energy for observed workload $`i`$ in kWh. |
| $`I_b^\star(t)`$ | Provider-compatible location-based carbon intensity for slice $`b`$, matched to the provider's accounting resolution. |
| $`M_i^\text{obs}(T)`$ | Directly attributable embodied carbon share for observed workload $`i`$ over month $`T`$. |
| $`C_\text{reported}(b,T)`$ | Provider-reported carbon for slice $`b`$ and month $`T`$. |

### Outputs

| Symbol | Description |
|--------|-------------|
| $`\text{SCI}_i = (O_i + M_i^\text{obs}) / R_i`$ | Action metric for an observed workload on the observable boundary. |
| $`\text{SCI}_b(T) = C_\text{action}(b,T) / R_b(T)`$ | Provider-aligned service-slice SCI aggregated to the reporting slice. |
| $`\hat{C}(b,T)`$ | Our estimate of the provider-reported carbon before actuals arrive. |

$`R_b(T)`$ is only well-defined when the workloads rolled into slice $`b`$ share a common functional unit or have been normalized to one. Otherwise, the slice should be reported as an absolute carbon total plus its constituent workload SCI values.

### Core Equations

For each observed workload:

$$O_i(T) = \int_T E_i(t)\, I_{b(i)}^\star(t)\, dt$$

For each provider reporting slice:

$$C_\text{action}(b,T) = \sum_{i \mapsto b}\big(O_i(T) + M_i^\text{obs}(T)\big)$$

$$\hat{C}(b,T) = C_\text{action}(b,T) + \hat{\Delta}_\text{residual}(b,T) + \hat{\Delta}_\text{coverage}(b,T) \approx C_\text{reported}(b,T)$$

Where:

- $`C_\text{action}`$ is the observable SCI-style carbon total for the slice.
- $`\hat{\Delta}_\text{residual}`$ is residual carbon inside the slice that the observable metric does not directly capture.
- $`\hat{\Delta}_\text{coverage}`$ is the explicit boundary mismatch term for uninstrumented or unmappable activity.

This is the central formalization change: **we reconcile at the provider slice, and we keep residual effects separate from coverage gaps.**

### SCI Reference

We use SCI naming for $`E`$, $`I`$, $`M`$, and $`R`$; see [`references/SCI.md`](references/SCI.md). The user-facing metric is best described as an **SCI-based metric on the observable boundary**. In public cloud, teams usually cannot observe all supporting infrastructure in real time, so the raw action metric alone should not be presented as the provider's full reported footprint.

## Design: Three-Layer Architecture

### Layer 1 — Measurement and Mapping

Measure workload energy as close to the hardware as possible via power telemetry, hardware counters, or calibrated models, then map each measurement to a provider reporting slice.

This layer is responsible for:

- estimating $`E_i(t)`$
- computing $`O_i(T)`$
- assigning each observed workload to one or more provider slices
- recording where coverage is partial or ambiguous

Output: observable per-workload SCI values and slice-aligned action totals.

### Layer 2 — Reconciliation Model

Estimate the gap between the observable action total and the provider-reported total at the slice level.

This layer does **not** cleanly identify every latent component from monthly data alone. The monthly reported target mainly constrains the **total bridge**. The decomposition of that bridge into PUE, idle, residual embodied carbon, Scope 1, other Scope 3, and allocation artifacts is partly data-driven and partly prior-driven.

Output: $`\hat{C}(b,T)`$ with uncertainty intervals and a decomposition of the bridge annotated by confidence.

### Layer 3 — User-Facing Views

Users should see two linked but distinct views:

- **Action view:** per-workload or per-service SCI on the observable boundary
- **Reporting view:** provider-aligned slice totals plus allocated reconciliation bridge

This preserves agency without pretending the real-time metric already contains the full provider methodology.

## Why the Framework Must Be Provider-Adaptive

Not all optimization levers survive contact with provider accounting:

- **Temporal shifting** only reconciles if the provider uses sub-monthly emission factors.
- **Compute efficiency** reconciles most directly when allocation is physical.
- **Spatial shifting** is broadly reconcilable because all three providers use regional factors.

The framework therefore needs a **provider profile** that tells us:

- what the reporting slice is
- how emissions are allocated to that slice
- what temporal and spatial resolution the provider uses
- which residuals are likely to dominate the bridge

When a provider improves methodology, new optimization levers become reconcilable. Making that visible is part of the point.

## Provider Profiles

The provider profile schema lives in [`SCHEMA.md`](SCHEMA.md). It captures:

- provider-exposed reporting dimensions and recommended reconciliation unit
- allocation method and granularity
- temporal resolution of emission factors
- embodied-carbon treatment
- overhead and verification metadata

Key finding: **reconcilability is provider-specific.**

- **GCP:** strongest direct alignment for electricity-related signals because allocation is physical and granular.
- **AWS:** strong for foundational services, weaker where economic allocation is used.
- **Azure:** directionally aligned for many actions, but confidence is limited by usage-factor opacity and coarser service granularity.

## Estimation Framework

### Goal

Estimate the bridge at the provider reporting slice before provider actuals arrive:

$$\hat{\Delta}_\text{total}(b,T) = \hat{\Delta}_\text{residual}(b,T) + \hat{\Delta}_\text{coverage}(b,T)$$

### Residual Bridge Decomposition

We decompose the residual bridge into carbon terms:

$$\hat{\Delta}_\text{residual} = \Delta_\text{PUE} + \Delta_\text{idle} + \Delta_\text{scope1} + \Delta_\text{embodied,resid} + \Delta_\text{other-s3} + \Delta_\text{alloc}$$

Where:

- $`\Delta_\text{PUE}`$ — facility overhead not present in measured IT energy
- $`\Delta_\text{idle}`$ — idle/shared capacity not assigned by the observable boundary
- $`\Delta_\text{scope1}`$ — provider-allocated diesel and refrigerants
- $`\Delta_\text{embodied,resid}`$ — embodied carbon not directly attributable from observed reservations
- $`\Delta_\text{other-s3}`$ — other provider-allocated Scope 3 categories
- $`\Delta_\text{alloc}`$ — provider methodology effects that make the reported slice differ from a purely physical allocation

And:

- $`\hat{\Delta}_\text{coverage}`$ — explicit gap from uninstrumented or unmappable activity inside the provider slice

### Parameter Table

| Parameter | Meaning | Units / Role | Prior | Sensitivity |
|---|---|---|---|---|
| $`\alpha_\text{PUE}(b,T)`$ | Facility/IT energy ratio | Dimensionless; converts observed IT energy toward facility energy | ~1.1–1.3 | High |
| $`E_\text{idle}(b,T)`$ | Unobserved idle/shared energy | kWh not assigned to observed workloads | ~15–30% of observed IT energy | Medium |
| $`M_\text{resid}(b,T)`$ | Residual embodied carbon | tCO₂e not directly attributable from observed reservations | Provider LCA / profile-driven | Medium-High |
| $`\rho_{s1}(b,T)`$ | Scope 1 ratio | Dimensionless carbon uplift over facility-energy carbon | ~0.01–0.03 | Low |
| $`\rho_{s3}(b,T)`$ | Other Scope 3 ratio | Dimensionless carbon uplift over action carbon | ~0.05–0.15 | Low-Medium |
| $`\beta_\text{alloc}(b,T)`$ | Allocation adjustment | Dimensionless correction for provider allocation method | Physical ~1.0; wider on usage/economic methods | High |
| $`C_\text{cov}(b,T)`$ | Coverage-gap carbon | tCO₂e from uninstrumented or unmappable workload share | zero if slice fully covered | High |

### Bayesian Framing

At the slice level:

$$C_\text{reported}(b,T) \sim \mathcal{N}\big(C_\text{action}(b,T) + \hat{\Delta}_\text{total}(b,T;\boldsymbol{\theta}),\;\sigma^2_\text{obs}\big)$$

The important modeling point is:

- monthly data strongly constrains the **total bridge**
- the component breakdown is only partially identifiable
- side information such as published PUE, provider methodology changes, and service coverage assumptions are required for a credible decomposition

So the honest output is not "we inferred each latent component from data alone." The honest output is "we estimated the total bridge and apportioned it into components with stated prior strength and uncertainty."

### Output Format

```text
Provider slice: project=foo / sku=n2-standard-16 / region=europe-west4 / month=2026-02

Reported estimate: 12.3 tCO2e [10.8 - 14.1, 90% CI]
Observable action total: 8.7 tCO2e
Estimated total bridge: 3.6 tCO2e

Bridge component                         Estimate    Confidence
--------------------------------------------------------------
Facility overhead (PUE)                 1.2 tCO2e   medium
Idle/shared capacity                    0.8 tCO2e   low
Scope 1                                 0.1 tCO2e   low
Residual embodied carbon                0.9 tCO2e   medium
Other Scope 3                           0.3 tCO2e   low
Allocation adjustment                   0.1 tCO2e   low
Coverage gap                            0.2 tCO2e   high

Model maturity: 8 months
Last residual error: +0.3 tCO2e (2.4%)
```

## Open Design Questions

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific questions.

1. **Identifiability:** Which bridge components are estimable from monthly slice-level data, and which should be treated as provider-profile priors plus side information?
2. **Coverage accounting:** How do we estimate $`\hat{\Delta}_\text{coverage}`$ for partially instrumented slices without hiding it inside generic uncertainty?
3. **Non-stationarity:** How should methodology changes trigger profile version updates and regime shifts in the model?
4. **Minimum viable history:** How many months of slice-level pairs $`(C_\text{action}, C_\text{reported})`$ are needed before the bridge estimate is decision-useful for each provider?

## Repository Structure

```text
├── README.md                            # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md     # detailed provider methodology comparison
├── SCHEMA.md                            # provider profile schema and populated profiles
├── references/SCI.md                    # Software Carbon Intensity standard
├── references/SCI_AI.md                 # SCI for AI standard
```
