# rSCI: Reconciled Software Carbon Intensity

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


## Action Metrics

The GSF's [Software Carbon Intensity](references/SCI.md) (SCI) was designed as an actionable optimization signal $$SCI = C / R,$$ which describes the carbon $C$ per unit of work $R$ (e.g., per request, per hour, per GB).
In their original formulation, carbon is the sum of operational carbon $`O`$ (energy $`E`$ × carbon intensity $`I`$) and amortized embodied carbon:
$$C = O + M$$
$$C = E \cdot I + M$$

[Bashir et al. (2024)](https://arxiv.org/abs/2410.15087) showed that including embodied carbon $`M`$ in the optimization metric can lead to perverse scheduling outcomes where carbon-aware schedulers route work to older, less efficient servers. 
They proposed 
- oSCI (operational only), which is the current state of the art for actionable carbon metrics and according to the authors, the best metric for carbon-aware scheduling.
- tSCI (where overhead of idle server are attributed to $`O`$ and $`M`$), but consider it impractical because it requires comprehensive datacenter-level information that cloud customers do not have access to.

Overview:

| Metric | $`C`$                                           | Includes                                             | Key limitation                               |
|--------|-------------------------------------------------|------------------------------------------------------|----------------------------------------------|
| SCI | $`E \cdot I + M`$                               | Operational + active embodied                        | Sunk carbon fallacy (Bashir et al.)          |
| oSCI | $`E \cdot I`$                                   | Operational only                                     | Misses embodied and other overheads entirely |
| tSCI | $`E \cdot I + O_\text{idle-infra} + M + M_\text{idle-infra}`$ | Full infrastructure, allocated proportionally        | Requires bottom-up datacenter knowledge      |
| **rSCI** | $`E \cdot I + w \cdot \Delta_\text{residual}`$     | oSCI + allocated residual (embodied, idle, overhead) | ✨ (some historical data)                     |

We extend the taxonomy with **rSCI**: a variant that reconciles to a provider-reported total. rSCI 
- shares tSCI's goal of allocating the full carbon footprint back to individual jobs, but makes it practical: instead of requiring complete bottom-up datacenter knowledge, rSCI learns the gap from historical (O_total, C_reported) pairs. 
- is also strictly broader in scope: where tSCI only adds idle server operational and embodied carbon, rSCI's residual captures *everything* between the observable operational total and the provider-reported number: embodied carbon, idle capacity, PUE, Scope 1 emissions (diesel, refrigerants), allocation artifacts, and any other overhead the provider includes. 
- always preserves oSCI ordering: since rSCI = oSCI · γ (residual factor), reducing operational carbon always reduces rSCI, and it cannot produce perverse scheduling incentives.


## Notation

### Indices

- $`t`$ — evaluation period: a fixed time window (e.g., 5 min) for interactive workloads, or the job's duration for batch workloads. All per-period quantities ($`E`$, $`I^\star`$, $`R`$, $`O`$, oSCI, rSCI) are defined over one $`t`$.
- $`m`$ — individual machine/instance serving the workload (used inside the power model)

We fix a single reporting slice, single service, and month (see Boundary Model). The service index $`i`$ is omitted — it returns when multi-service slices are introduced.

### Inputs

| Symbol | Description |
|--------|-------------|
| $`E`$ | Aggregate measured IT energy over $`t`$, in kWh. $`E = \sum_m P_m \cdot \Delta t`$ where $`P_m`$ is the estimated power draw of machine $`m`$. |
| $`I^\star`$ | Provider-compatible location-based carbon intensity for $`t`$. For short windows this is instantaneous; for batch jobs it is the time-weighted average over the run. |
| $`C_\text{reported}`$ | Provider-reported carbon (reporting metric) for the slice (monthly). |

### Outputs

| Symbol | Description |
|--------|-------------|
| $`\text{rSCI}`$ | Action metric per $`t`$ — oSCI plus allocated residual, reconciles to provider total. |
| $`\text{rSCI}_\text{monthly} = C_\text{reported} / R_\text{total}`$ | Monthly aggregate: the reconciled metric over the full reporting period. |

### Core Equations

**Action layer (per $`t`$):**

$$O = E \cdot I^\star, \quad \text{oSCI} = O \;/\; R$$

Following Bashir et al. (2024), the action layer uses oSCI: embodied carbon is a sunk cost that should not influence scheduling decisions.

**Reconciliation layer (per slice, monthly):**

$$O_\text{total} = \sum_t O$$

$$\Delta_\text{residual} = C_\text{reported} - O_\text{total}$$

$`\Delta_\text{residual}`$ absorbs everything the action metric does not capture: embodied carbon, idle/shared capacity, non-energy overhead (PUE, Scope 1), allocation artifacts.

**Reconciled metric:**

$$\text{rSCI} = (O_\text{total} + \Delta_\text{residual}) / R_\text{total} = C_\text{reported} / R_\text{total}$$

**Key property:** $`\sum_t \text{rSCI} \cdot R = C_\text{reported}`$

The reconciled metric distributes the full provider-reported footprint across periods in proportion to their operational carbon. Because the residual is allocated proportionally to $`O`$, rSCI **always preserves oSCI ordering** — reducing operational carbon always reduces rSCI, and it cannot produce perverse scheduling incentives. Yet each period's rSCI reflects its fair share of the full reported footprint, including embodied carbon and overhead.

Where:

- The action layer uses oSCI to avoid the sunk carbon fallacy (Bashir et al., 2024).
- $`\Delta_\text{residual}`$ is learned from historical slice pairs $`(O_\text{total}, C_\text{reported})`$.
- Unlike tSCI (which requires full infrastructure knowledge), rSCI learns the residual from the provider-reported total.
- The service index $`i`$ (partitioning within a slice) returns when the single-service assumption is relaxed.

We use SCI naming for $`E`$, $`I`$, and $`R`$; see [`references/SCI.md`](references/SCI.md) and [`references/SCI_SUNK_CARBON.md`](references/SCI_SUNK_CARBON.md).

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

The residual bridge $`\Delta_\text{residual}`$ is a single fitted scalar that captures everything the action metric does not: embodied carbon (hardware and buildings), facility overhead (PUE), idle/shared capacity, non-energy overhead (Scope 1 diesel/refrigerants, other Scope 3 categories), and allocation artifacts from provider methodology. Embodied carbon is deliberately excluded from the action layer to avoid the sunk carbon fallacy (Bashir et al., 2024) — it enters only through the residual. With monthly slice-level data, these components are not individually identifiable — the total bridge is constrained, but the breakdown is not. We therefore treat $`\Delta_\text{residual}`$ as one quantity fitted from historical slice pairs rather than pretending the components can be separated.

### Parameter Table

| Parameter | Meaning | Units / Role | Prior | Sensitivity |
|---|---|---|---|---|
| $`\Delta_\text{residual}`$ | Residual bridge | tCO₂e; fitted from historical slice pairs $`(O_\text{total}, C_\text{reported})`$ | Provider profile-driven | High |

### Bayesian Framing

$$
C_\text{reported} \sim \mathcal{N}\big(O_\text{total} + \Delta_\text{residual},\;\sigma^2_\text{obs}\big)
$$

- Monthly data strongly constrains the **total bridge**.
- Side information (provider profiles, methodology changes) sets the prior on $`\Delta_\text{residual}`$.

### Output Format

```text
Provider slice: project=foo / sku=n2-standard-16 / region=europe-west4 / month=2026-02

Reported estimate (ĉ): 12.1 tCO2e [10.6 - 13.9, 90% CI]
Observable operational total (O_total): 8.7 tCO2e
Residual bridge (Δ_residual): 3.4 tCO2e

Per workload:
  web-api (interactive):  oSCI = 0.042 kgCO2e/req   |  rSCI = 0.058 kgCO2e/req
  ml-training (batch):    oSCI = 8.7 kgCO2e/job      |  rSCI = 12.1 kgCO2e/job

Reconciliation check: Σ_t rSCI · R = 12.1 tCO2e = ĉ  ✓

Model maturity: 8 months
Last residual error: +0.3 tCO2e (2.4%)
```

## Future Work

Main issue: instability across months

- **Time-dependent parameters:** Model $`\Delta_\text{residual}`$ as time-varying, learned across months. This captures seasonal effects, methodology changes, and infrastructure evolution.
- **PUE as a learnable parameter:** Factor out $`\alpha_\text{PUE}`$ from $`\Delta_\text{residual}`$ and include it in the action layer ($`O_i = \alpha_\text{PUE} \cdot E_i \cdot I^\star`$), calibrated from provider-published PUE or historical data.
- **Bridge decomposition:** Once sufficient historical slice pairs are available, decompose $`\Delta_\text{residual}`$ into provider-methodology-informed components (embodied carbon, PUE mismatch, idle capacity, non-energy overhead, allocation artifacts) using priors from provider profiles and Bayesian modeling. The goal is to identify whether any true unexplained residual remains after accounting for known methodology effects. This decomposition can progressively refine the residual without changing the action signal — oSCI ordering is preserved regardless of how the residual is broken down.
- Location dependant too!!!
- **Normative reference estimate:** a second, more methodologically complete estimate (covering omitted Scope 3 categories, questionable amortization, coarse allocation, provider-specific flaws) that makes visible the gap between what providers report and what a fuller methodology would report — comparative, not substitutive, and explicitly separate from the core reconciliation framework.

## Open Questions

1. **Actionability limits:** When a reporting slice is too coarse or too opaque, how should the framework expose that optimization claims are weak rather than presenting false precision?
2. **Lever reconcilability:** Which user actions move the reporting metric directly, approximately, or not at all under a given provider methodology?
3. **Minimum viable provider knowledge:** What minimum provider profile can be constructed from public documentation before the framework becomes too speculative? How many months of slice-level pairs $`(O_\text{total}, C_\text{reported})`$ are needed before the residual bridge estimate is decision-useful?
4. **Non-stationarity:** How should methodology changes trigger profile version updates and regime shifts in the model?
5. **Cold start:** Without historical slice pairs, $`\Delta_\text{residual}`$ is unknown and rSCI degrades to oSCI. The reconciliation claim is empty until calibrated. How should the framework communicate this? Options include: reporting confidence intervals that widen with fewer data points, falling back to provider-profile-derived priors (e.g., published PUE × typical embodied ratios), or explicitly labeling the estimate as "uncalibrated" until a minimum number of months are available. What is the minimum number of slice pairs needed before the residual estimate is decision-useful — and does this differ by provider methodology quality?
6. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports. If the provider's methodology is flawed (e.g., uses economic allocation that doesn't reflect physical reality, or applies uniform emission factors across regions with different grid mixes), rSCI faithfully reconciles to a misleading number. The framework makes this visible — a persistently large or volatile $`\Delta_\text{residual}`$ signals methodology weakness — but it cannot correct for it. How should the framework distinguish "high residual because provider methodology is coarse" from "high residual because we are missing observable activity"? Should provider methodology quality scores inform how the residual estimate is presented to users?

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific questions.

## Repository Structure

```text
├── README.md                            # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md     # detailed provider methodology comparison
├── SCHEMA.md                            # provider profile schema and populated profiles
├── references/SCI.md                    # Software Carbon Intensity standard
├── references/SCI_AI.md                 # SCI for AI standard
├── references/SCI_SUNK_CARBON.md        # Bashir et al. (2024) — sunk carbon fallacy, oSCI/tSCI
```
