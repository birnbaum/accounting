# Reconcilable User-facing Cloud Carbon Accounting

## Mission

Metrics that make cloud carbon data auditable and comparable across organizations are not the same metrics that help individual teams reduce emissions.
For context:

**Bottom-up (action):** We measure workload energy as close to the hardware as possible, combine it with location-based carbon intensity, and report an rSCI signal (reconciled Software Carbon Intensity) in near real time. This gives teams an optimization signal they can act on, but by itself it does not fully capture facility overhead, idle/shared capacity, provider-specific allocation effects, or all Scope 1/3 components.

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.

These two signals are not, and should not be, identical. **But they must be reconcilable**: If a team improves its bottom-up signal, that improvement should be traceable through to the cloud provider's reported number at the reporting boundary the provider actually exposes. If the two diverge without explanation, users lose trust in both.

### Why optimizing for imperfect cloud carbon accounting methodologies?
 
In practice, cloud customers' Scope 3 GHG accounting happens through the numbers providers report. Those numbers are imperfect and provider methodologies remain heterogeneous. Better disclosure, stricter boundaries, and more unified reporting standards are still needed. But even under imperfect reporting, users need a framework that maps real-time operational action to the provider-reported number that currently governs reporting practice. A useful side effect is that this mapping makes weaknesses in provider methodologies more visible rather than hiding them behind a single delayed total.

This framework serves two goals:

- **For users:** provide an rSCI action metric per workload and per provider-aligned service slice, then reconcile that signal to the provider's delayed GHG-style report.
- **For the ecosystem:** make provider methodology quality visible by showing which optimization levers are directly rewarded, only approximately rewarded, or structurally blocked by provider accounting choices.

We focus on **location-based accounting**. Market-based accounting is intentionally excluded from the action metric because it is decoupled from physical consumption and therefore weak as an operational signal.

## Problem Framing

Given:
- **Action metric:** a bottom-up, rSCI metric on the observable boundary that teams can optimize in real time.
- **Reporting metric:** the top-down, provider-reported carbon for Scope 3 accounting that is delayed by weeks.

> How do we map action metrics onto reporting metrics while being explicit about the sources and uncertainty of the gap?

### SCI Variant Taxonomy

The GSF's [Software Carbon Intensity](references/SCI.md) (SCI) was designed as a standalone optimization signal. Bashir et al. (2024) showed that including embodied carbon — a sunk cost — in the optimization metric can lead to [perverse scheduling outcomes](references/SCI_SUNK_CARBON.md) where carbon-aware schedulers route work to older, less efficient servers. They proposed oSCI (operational only) and tSCI (total infrastructure, allocated proportionally) as alternatives. We extend the taxonomy with **rSCI** — a variant that reconciles to a provider-reported total.

| Metric | Formula | Includes | Key limitation |
|--------|---------|----------|----------------|
| oSCI | $`(E \cdot I) / R`$ | Operational only | Misses embodied entirely |
| SCI | $`((E \cdot I) + M) / R`$ | + active server embodied | Sunk carbon fallacy (Bashir et al.) |
| tSCI | $`(tO + tM) / R`$ | Full infrastructure, allocated proportionally | Requires bottom-up datacenter knowledge |
| **rSCI** | $`(O_i + M_i^\text{obs} + w_i \cdot \Delta_\text{residual}(t)) / R_i`$ | Action metric + learned residual | Requires historical slice pairs for calibration |

rSCI trades the need for full infrastructure knowledge (tSCI) for a reconciliation target — the provider-reported total — and learns the gap over time.

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

The goal is to make the bridge **explicit, predictable, and small enough** that users can understand how improving the action metric maps to improving the reporting metric.
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
| $`\alpha_\text{PUE}(t)`$ | Facility/IT energy ratio, learned from provider-published PUE or calibrated from historical slice pairs; evolves over time. |
| $`M_i^\text{obs}`$ | Directly attributable embodied carbon share for observed workload $`i`$. |
| $`C_\text{reported}`$ | Provider-reported carbon (reporting metric) for the slice. |

### Outputs

| Symbol | Description |
|--------|-------------|
| $`\text{rSCI}_i = C_i^\text{rec} / R_i`$ | Action metric per workload — includes allocated residual, reconciles to provider total. |
| $`\hat{C} = \sum_i \text{rSCI}_i \cdot R_i`$ | Estimate of the reporting metric before actuals arrive. |

### Core Equations

**Action layer (per workload):**

$$O_i = \alpha_\text{PUE}(t) \cdot \int E_i(t)\, I^\star(t)\, dt$$

$$\text{SCI}_i = (O_i + M_i^\text{obs}) / R_i$$

PUE scales with energy, so reducing energy also reduces this overhead — it belongs in the action metric.

**Reconciliation layer (per slice):**

$$C_\text{action} = \sum_i\big(O_i + M_i^\text{obs}\big) = \sum_i \text{SCI}_i \cdot R_i$$

$$\hat{C} = C_\text{action} + \Delta_\text{residual}(t) \approx C_\text{reported}$$

**Allocation layer (back to workloads):**

$$w_i = (O_i + M_i^\text{obs}) / C_\text{action}$$

$$C_i^\text{rec} = O_i + M_i^\text{obs} + w_i \cdot \Delta_\text{residual}(t)$$

$$\text{rSCI}_i = C_i^\text{rec} / R_i$$

**Key property:** $`\sum_i \text{rSCI}_i \cdot R_i = \hat{C} \approx C_\text{reported}`$

Where:

- All SCI variants (oSCI, SCI, tSCI, rSCI) are action metrics with different scope and trade-offs.
- rSCI extends the family by reconciling to the provider-reported total: each workload's rSCI includes its fair share of unobservable residual carbon.
- Unlike tSCI (which requires full infrastructure knowledge), rSCI learns the residual from historical slice pairs $`(C_\text{action}, C_\text{reported})`$.
- $`\alpha_\text{PUE}(t)`$ and $`\Delta_\text{residual}(t)`$ are time-dependent (learned across months); location is fixed by the slice.

We use SCI naming for $`E`$, $`I`$, $`M`$, and $`R`$; see [`references/SCI.md`](references/SCI.md) and [`references/SCI_SUNK_CARBON.md`](references/SCI_SUNK_CARBON.md).

## Provider Profiles

Not all optimization levers reconcile equally across providers. Temporal shifting only reconciles if the provider uses sub-monthly emission factors; compute efficiency reconciles most directly under physical allocation; spatial shifting is broadly reconcilable because all three providers use regional factors. The framework therefore needs provider-specific configuration.

A provider profile captures:

- reporting dimensions and recommended reporting slice
- allocation method and granularity
- temporal resolution of emission factors
- embodied-carbon treatment
- overhead and verification metadata

Schema: [`SCHEMA.md`](SCHEMA.md).

Summary by provider:

- **GCP:** strongest direct alignment for electricity-related signals — allocation is physical and granular.
- **AWS:** strong for foundational services, weaker where economic allocation is used.
- **Azure:** directionally aligned for many actions, but confidence is limited by usage-factor opacity and coarser service granularity.

When a provider improves methodology, new optimization levers become reconcilable. Making that visible is part of the point.

## Estimation Framework

**Goal:** estimate the residual bridge at the reporting slice before provider actuals arrive.

### Residual Bridge

The residual bridge $`\Delta_\text{residual}(t)`$ is a single fitted scalar that captures everything the action metric does not: idle/shared capacity, non-energy overhead (Scope 1 diesel/refrigerants, other Scope 3 categories), residual embodied carbon not directly attributable from observed reservations, allocation artifacts from provider methodology, and any remaining PUE mismatch between the fitted $`\alpha_\text{PUE}(t)`$ and reality. With monthly slice-level data, these components are not individually identifiable — the total bridge is constrained, but the breakdown is not. We therefore treat $`\Delta_\text{residual}(t)`$ as one quantity fitted from historical slice pairs rather than pretending the components can be separated.

### Parameter Table

| Parameter | Meaning | Units / Role | Prior | Sensitivity |
|---|---|---|---|---|
| $`\alpha_\text{PUE}(t)`$ | Facility/IT energy ratio | Dimensionless; scales observed IT energy to facility energy inside the action metric | ~1.1–1.3 | High |
| $`\Delta_\text{residual}(t)`$ | Residual bridge | tCO₂e; fitted from historical slice pairs $`(C_\text{action}, C_\text{reported})`$ | Provider profile-driven | Medium-High |

### Bayesian Framing

$$
C_\text{reported} \sim \mathcal{N}\big(C_\text{action}(\alpha_\text{PUE}(t)) + \Delta_\text{residual}(t),\;\sigma^2_\text{obs}\big)
$$

- Monthly data strongly constrains the **total bridge**.
- $`\alpha_\text{PUE}(t)`$ is informed by provider-published PUE and has high sensitivity on the action metric.
- Side information (provider profiles, methodology changes) sets the prior on $`\Delta_\text{residual}(t)`$.

### Output Format

```text
Provider slice: project=foo / sku=n2-standard-16 / region=europe-west4 / month=2026-02

Reported estimate (ĉ): 12.1 tCO2e [10.6 - 13.9, 90% CI]
Observable action total (C_action): 8.7 tCO2e
Residual bridge (Δ_residual): 3.4 tCO2e

Per workload:
  workload-a: SCI = 0.042 tCO2e/req  |  rSCI = 0.058 tCO2e/req  (w_i = 0.38)
  workload-b: SCI = 0.031 tCO2e/req  |  rSCI = 0.043 tCO2e/req  (w_i = 0.27)

Reconciliation check: Σ rSCI_i · R_i = 12.1 tCO2e = ĉ  ✓

Model maturity: 8 months
Last residual error: +0.3 tCO2e (2.4%)
```

## Future Work

- **Bridge decomposition:** Once sufficient historical slice pairs are available, decompose $`\Delta_\text{residual}`$ into provider-methodology-informed components (PUE mismatch, idle capacity, non-energy overhead, residual embodied, allocation artifacts) using priors derived from provider profiles. The goal is to identify whether any true unexplained residual remains after accounting for known methodology effects.

## Open Questions

1. **Actionability limits:** When a reporting slice is too coarse or too opaque, how should the framework expose that optimization claims are weak rather than presenting false precision?
2. **Lever reconcilability:** Which user actions move the reporting metric directly, approximately, or not at all under a given provider methodology?
3. **Minimum viable provider knowledge:** What minimum provider profile can be constructed from public documentation before the framework becomes too speculative? How many months of slice-level pairs $`(C_\text{action}, C_\text{reported})`$ are needed before the residual bridge estimate is decision-useful?
4. **Non-stationarity:** How should methodology changes trigger profile version updates and regime shifts in the model?

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific questions.

## Repository Structure

```text
├── README.md                            # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md     # detailed provider methodology comparison
├── SCHEMA.md                            # provider profile schema and populated profiles
├── NORMATIVE_REFERENCE_ESTIMATE.md      # normative reference estimate methodology
├── references/SCI.md                    # Software Carbon Intensity standard
├── references/SCI_AI.md                 # SCI for AI standard
├── references/SCI_SUNK_CARBON.md        # Bashir et al. (2024) — sunk carbon fallacy, oSCI/tSCI
```
