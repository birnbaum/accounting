# Reconcilable User-facing Cloud Carbon Accounting

## Mission

Metrics that make cloud carbon data auditable and comparable across organizations are not the same metrics that help individual teams reduce emissions.
For context:

**Bottom-up (action):** We measure workload energy as close to the hardware as possible, combine it with location-based carbon intensity, and report an SCI-style signal in near real time. This gives teams an optimization signal they can act on, but by itself it does not fully capture facility overhead, idle/shared capacity, provider-specific allocation effects, or all Scope 1/3 components.

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.



These two signals are not, and should not be, identical. **But they must be reconcilable**: If a team improves its bottom-up signal, that improvement should be traceable through to the cloud provider's reported number at the reporting boundary the provider actually exposes. If the two diverge without explanation, users lose trust in both.

### Why optimizing for imperfect cloud carbon accounting methodologies?
 
In practice, cloud customers' Scope 3 GHG accounting happens through the numbers providers report. Those numbers are imperfect and provider methodologies remain heterogeneous. Better disclosure, stricter boundaries, and more unified reporting standards are still needed. But even under imperfect reporting, users need a framework that maps real-time operational action to the provider-reported number that currently governs reporting practice. A useful side effect is that this mapping makes weaknesses in provider methodologies more visible rather than hiding them behind a single delayed total.

This framework serves two goals:

- **For users:** provide an SCI-based action metric per workload and per provider-aligned service slice, then reconcile that signal to the provider's delayed GHG-style report.
- **For the ecosystem:** make provider methodology quality visible by showing which optimization levers are directly rewarded, only approximately rewarded, or structurally blocked by provider accounting choices.

We focus on **location-based accounting**. Market-based accounting is intentionally excluded from the action metric because it is decoupled from physical consumption and therefore weak as an operational signal.

## Problem Framing

Given:
- **Action metric:** a bottom-up, SCI-style metric on the observable boundary that teams can optimize in real time.
- **Reporting metric:** the top-down, provider-reported carbon for Scope 3 accounting that is delayed by weeks.

> How do we map action metrics onto reporting metrics while being explicit about the sources and uncertainty of the gap?


### Boundary Model

We differentiate between:

- **Observable boundary:** a workloads' hardware reservations/utilization that we can use to compute the action metric.
- **Provider reporting boundary:** the finest slice at which the provider exposes the reporting metric.

The reconciliation unit is the provider's **reporting slice**, e.g.:

- **AWS:** `account × service × region × month`
- **GCP:** `project × SKU × region × month`
- **Azure:** `subscription × service_category × region × month`

Every measured workload event must map to one or more reporting slices. 

### Reconciliation Bridge

We call the gap between the top-down and bottom-up metric **reconciliation bridge**.
It has two distinct sources:

1. **Residual carbon inside the observable boundary**: even with perfect workload telemetry, the top-down metric includes carbon you cannot observe bottom-up: facility overhead (PUE), idle infrastructure, embodied carbon from hardware you do not own, and non-energy emissions such as diesel backup generation or refrigerant losses.
2. **Boundary mismatch**: A provider may bundle supporting services — storage I/O, managed networking, control-plane operations — into the same reporting slice that you are only partially observing. Even if measurements are precise, a structural gap remains wherever the two boundaries do not coincide.
   - *Example: you instrument all EC2 instances in `eu-central-1` perfectly, but the provider's `Compute` slice for that account and region also includes EBS volume activity and NAT Gateway traffic that you have not instrumented. Your action total covers only a subset of what that number reflects.*

The goal is not to eliminate that bridge by definition, but to make it **explicit, predictable, and small enough** that users can understand how improving the action metric maps to improving the reporting metric.
The primary goal is a calibrated month-end prediction at the reporting slice.

### Assumptions

For now (!), we assume
- **no boundary mismatch**: the observable boundary covers all activity in the reporting slice.
  For example, if a customer wants to reconcile `EC2 × eu-central-1 × January`, we assume they can observe all EC2 resources they run in that region over that month with enough fidelity to reconstruct resource-time/utilization.
  This is a structural requirement, without full coverage the residual bridge loses its interpretation.
- **one-to-one mapping**: each observed workload maps to exactly one reporting slice. This is a simplifying assumption that allows us to state the problem more clearly, but the framework should be extended to handle many-to-many mappings in practice (e.g. a workload that uses compute, storage and network or is distributed).
- **single slice**: For simplicity, the approach currently assumes a single reporting slice: one project, one service, one region, one month.


## Notation

### Indices

- $`i`$ — measured workload execution, component, or reservation
- $`t`$ — time within the reporting month

We fix a single reporting slice and month (see Boundary Model), so slice and month indices are omitted below.

### Inputs

| Symbol | Description |
|--------|-------------|
| $`E_i(t)`$ | Measured IT energy for observed workload $`i`$ in kWh. |
| $`I^\star(t)`$ | Provider-compatible location-based carbon intensity, matched to the provider's accounting resolution. |
| $`M_i^\text{obs}`$ | Directly attributable embodied carbon share for observed workload $`i`$. |
| $`C_\text{reported}`$ | Provider-reported carbon for the slice. |

### Outputs

| Symbol | Description |
|--------|-------------|
| $`\text{SCI}_i = (O_i + M_i^\text{obs}) / R_i`$ | Action metric for an observed workload on the observable boundary. |
| $`\hat{C}`$ | Our estimate of the provider-reported carbon before actuals arrive. |

Workload-level $`\text{SCI}_i`$ is the primary user-facing intensity metric; $`C_\text{action}`$ is the slice-level reconciliation object.

### Core Equations

For each observed workload:

$$O_i = \int E_i(t)\, I^\star(t)\, dt$$

For the slice:

$$C_\text{action} = \sum_i\big(O_i + M_i^\text{obs}\big)$$

$$\hat{C} = C_\text{action} + \hat{\Delta}_\text{residual} \approx C_\text{reported}$$

Where:

- $`C_\text{action}`$ is the observable SCI-style carbon total for the slice.
- $`\hat{\Delta}_\text{residual}`$ is residual carbon inside the slice that the observable metric does not directly capture.

This is the central formalization change: **we reconcile at the provider slice, with the residual bridge capturing everything the action metric misses.**

### SCI Reference

We use SCI naming for $`E`$, $`I`$, $`M`$, and $`R`$; see [`references/SCI.md`](references/SCI.md). The user-facing metric is best described as an **SCI-based metric on the observable boundary**. In public cloud, teams usually cannot observe all supporting infrastructure in real time, so the raw action metric alone should not be presented as the provider's full reported footprint.

## Design: Three-Layer Architecture

### Layer 1 — Measurement and Mapping

Measure workload energy as close to the hardware as possible via power telemetry, hardware counters, or calibrated models, then map each measurement to a reporting slice.

This layer is responsible for:

- estimating $`E_i(t)`$
- computing $`O_i(T)`$
- assigning each observed workload to one or more provider slices
- verifying that coverage of the declared provider slice is complete

Output: observable per-workload SCI values and slice-aligned action totals.

### Layer 2 — Reconciliation Model

Estimate the gap between the observable action total and the provider-reported total at the slice level.

This layer does **not** cleanly identify every latent component from monthly data alone. The monthly reported target mainly constrains the **total bridge**. The decomposition of that bridge into PUE, idle, non-energy overhead, residual embodied carbon, and allocation artifacts is partly data-driven and partly prior-driven.

Output: $`\hat{C}`$ with uncertainty intervals and a decomposition of the bridge annotated by confidence.

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
- whether the available methodology disclosure is sufficient for a credible minimum viable profile

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

Estimate the residual bridge at the reporting slice before provider actuals arrive.

### Residual Bridge Decomposition

We decompose the residual bridge into carbon terms:

$$\hat{\Delta}_\text{residual} = \Delta_\text{PUE} + \Delta_\text{idle} + \Delta_\text{non-energy} + \Delta_\text{embodied,resid} + \Delta_\text{alloc}$$

Where:

- $`\Delta_\text{PUE}`$ — facility overhead not present in measured IT energy
- $`\Delta_\text{idle}`$ — idle/shared capacity not assigned by the observable boundary
- $`\Delta_\text{non-energy}`$ — provider-allocated non-energy overhead (Scope 1 diesel/refrigerants plus other Scope 3 categories)
- $`\Delta_\text{embodied,resid}`$ — embodied carbon not directly attributable from observed reservations
- $`\Delta_\text{alloc}`$ — provider methodology effects that make the reported slice differ from a purely physical allocation

### Parameter Table

| Parameter | Meaning | Units / Role | Prior | Sensitivity |
|---|---|---|---|---|
| $`\alpha_\text{PUE}`$ | Facility/IT energy ratio | Dimensionless; converts observed IT energy toward facility energy | ~1.1–1.3 | High |
| $`E_\text{idle}`$ | Unobserved idle/shared energy | kWh not assigned to observed workloads | ~15–30% of observed IT energy | Medium |
| $`M_\text{resid}`$ | Residual embodied carbon | tCO₂e not directly attributable from observed reservations | Provider LCA / profile-driven | Medium-High |
| $`\rho_\text{ne}`$ | Non-energy overhead ratio | Dimensionless carbon uplift for Scope 1 + other Scope 3 | ~0.03–0.15 | Low-Medium |
| $`\beta_\text{alloc}`$ | Allocation adjustment | Dimensionless correction for provider allocation method | Physical ~1.0; wider on usage/economic methods | High |

### Bayesian Framing

At the slice level:

$$C_\text{reported} \sim \mathcal{N}\big(C_\text{action} + \hat{\Delta}_\text{residual}(\boldsymbol{\theta}),\;\sigma^2_\text{obs}\big)$$

The important modeling point is:

- monthly data strongly constrains the **total bridge**
- the component breakdown is only partially identifiable
- side information such as published PUE, provider methodology changes, and service coverage assumptions are required for a credible decomposition

So the honest output is not "we inferred each latent component from data alone." The honest output is "we estimated the total bridge and apportioned it into components with stated prior strength and uncertainty."

### Output Format

```text
Provider slice: project=foo / sku=n2-standard-16 / region=europe-west4 / month=2026-02

Reported estimate: 12.1 tCO2e [10.6 - 13.9, 90% CI]
Observable action total: 8.7 tCO2e
Estimated residual bridge: 3.4 tCO2e

Bridge component                         Estimate    Confidence
--------------------------------------------------------------
Facility overhead (PUE)                 1.2 tCO2e   medium
Idle/shared capacity                    0.8 tCO2e   low
Non-energy overhead (S1 + other S3)     0.4 tCO2e   low-medium
Residual embodied carbon                0.9 tCO2e   medium
Allocation adjustment                   0.1 tCO2e   low

Model maturity: 8 months
Last residual error: +0.3 tCO2e (2.4%)
```

## Open Problem Formulation Questions

1. **Actionability limits:** When a provider slice is too coarse or too opaque, how should the framework expose that optimization claims are weak rather than presenting false precision?
2. **Lever reconcilability:** Which user actions should be expected to move the provider-reported number directly, approximately, or not at all under a given provider methodology?
3. **Minimum viable provider knowledge:** What minimum provider profile can be constructed from public documentation and customer-visible outputs before the framework becomes too speculative?

## Modeling Questions

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific questions.

1. **Identifiability:** Which bridge components are estimable from monthly slice-level data, and which should be treated as provider-profile priors plus side information?
2. **Non-stationarity:** How should methodology changes trigger profile version updates and regime shifts in the model?
3. **Minimum viable history:** How many months of slice-level pairs $`(C_\text{action}, C_\text{reported})`$ are needed before the bridge estimate is decision-useful for each provider?

## Repository Structure

```text
├── README.md                            # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md     # detailed provider methodology comparison
├── SCHEMA.md                            # provider profile schema and populated profiles
├── references/SCI.md                    # Software Carbon Intensity standard
├── references/SCI_AI.md                 # SCI for AI standard
```
