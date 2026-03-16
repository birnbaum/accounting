# rSCI: Reconciled Software Carbon Intensity

**Problem**: Metrics that are reported by cloud providers for Scope 3 GHG reporting are not the same metrics that help individual teams reduce emissions. See e.g. [Measuring for Reporting vs. Measuring for Action](https://greensoftware.foundation/articles/measuring-for-reporting-vs-measuring-for-action).

- **Top-down methodology (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (not yet due to underspecified parts in the GHG protocol, but hopefully at some point), but coarse (usually one number per customer x service x region x month) and delayed (available 2-3 weeks after month-end). It tells you the size of the problem but not what to do about it.
- **Bottom-up methodology (action):** We measure (or model based on proxies) workload energy as close to the hardware as possible, combine it with location-based carbon intensity, and report some kind of [SCI (Software Carbon Intensity)](https://sci.greensoftware.foundation/) signal in near real time. This gives teams an optimization signal they can act on, but by itself it does not fully capture facility overhead, idle/shared capacity, provider-specific allocation effects, or all Scope 1/3 components.

These two signals cannot be identical. **But they must be reconcilable**: If a team improves its bottom-up signal, that improvement should be traceable through to the cloud provider's reported number at the reporting boundary the provider actually exposes. If the two diverge without explanation, users lose trust in both.

Note: We focus on **location-based accounting**. Market-based accounting is decoupled from physical consumption and therefore weak as an energy/carbon efficiency signal.

<details>

<summary>Why optimize toward imperfect accounting methodologies?</summary>

In practice, cloud customers' Scope 3 GHG accounting happens through the numbers providers report. Those numbers are imperfect and provider methodologies remain heterogeneous and partially opaque. Better standards are still needed, but even under imperfect reporting, users need a framework that maps actionable signals to the provider-reported number that governs reporting practice.

Goals of this framework:
- **For users:** provide an SCI-style metric per workload that sums up to the provider's delayed GHG report and makes uncertainties explicit.
- **For the ecosystem:** make GHG methodology quality visible by showing which energy/carbon efficiency optimization levers are rewarded, only approximately rewarded, or structurally blocked by provider accounting choices. This can inform/pressure better provider practices.
</details>


## Motivation

The GSF's Software Carbon Intensity was designed as an actionable optimization signal $$SCI = C / R,$$ which describes the carbon $C$ per unit of work $R$ (e.g., per request, per hour, per GB).
In their original formulation, carbon is the sum of operational carbon $`O`$ (energy $`E`$ × carbon intensity $`I`$) and amortized embodied carbon:

$$C = O + M$$

$$C = E \cdot I + M$$

[Bashir et al. (2024)](https://arxiv.org/abs/2410.15087) showed that including embodied carbon $`M`$ in the optimization metric can lead to perverse scheduling outcomes where carbon-aware schedulers route work to older, less efficient servers.
They proposed
- oSCI (operational only), which is the current state of the art for actionable carbon metrics and according to the authors, the best metric for carbon-aware scheduling.
- tSCI (where overhead of idle server are attributed to $`O`$ and $`M`$), but consider it impractical because it requires comprehensive datacenter-level information that cloud customers do not have access to.

We extend the taxonomy with **rSCI** (reconciled SCI): a variant that reconciles to the provider-reported total. 

| Metric | $`C`$                                           | Includes                                             | Key limitation                               |
|--------|-------------------------------------------------|------------------------------------------------------|----------------------------------------------|
| SCI | $`E \cdot I + M`$                               | Operational + active embodied                        | Sunk carbon fallacy (Bashir et al.)          |
| oSCI | $`E \cdot I`$                                   | Operational only                                     | Misses embodied and other overheads entirely |
| tSCI | $`E \cdot I + O_\text{idle-infra} + M + M_\text{idle-infra}`$ | Full infrastructure, allocated proportionally        | Requires bottom-up datacenter knowledge      |
| **rSCI** | $`E \cdot I + w \cdot \Delta_\text{residual}`$     | oSCI + allocated residual (embodied, idle, overhead) | ✨ (some historical data)                     |

where $`\Delta_\text{residual}`$ is the **residual bridge**: the differece between the reported carbon and the sum over all bottom-up aggregated signals: 

$$\Delta_\text{residual} = C_\text{reported} - O_\text{agg}$$

It absorbs embodied carbon, idle capacity, PUE, Scope 1/3, allocation artifacts, and any estimation error for operational emissions $`\varepsilon_O`$.


**Benefits of rSCI**
- it shares tSCI's goal of allocating the full carbon footprint back to individual jobs, but makes it practical: instead of requiring complete bottom-up datacenter knowledge, rSCI learns the gap from historical ($`O_{total}`$, $`C_{reported}`$) pairs.
- it is also more comprehensive in scope: where tSCI only adds idle server operational and embodied carbon, rSCI's residual captures *everything* between the observable operational total and the provider-reported number: embodied carbon, idle capacity, PUE, Scope 1 emissions (diesel, refrigerants), allocation artifacts, and any other overhead the provider includes.
- it does **not** suffer from the sunk carbon fallacy (Bashir et al.): Since rSCI = oSCI · $`\gamma`$ (where $`\gamma = C_\text{reported} / O_\text{total}`$ is the residual factor), the allocation of overhead is proportional to operational emissions at a specific time and location. The ordering between scheduling alternatives is always identical to oSCI within a slice.
- but it **does** reward scheduling toward lower-overhead infrastructure. Because $`\gamma`$ differs across slices (a region with older hardware, higher PUE, or more idle capacity carries a larger $`\gamma`$) rSCI incentivizes placing work on nodes with lower embodied emissions and facility overhead. $`\gamma`$ also changes over time, e.g., fluctuating PUE, hardware refresh cycles. oSCI is blind to these factors.

## Problem Framing

### Metric Terminology
- **Reporting metric:** the top-down, provider-reported carbon for Scope 3 accounting that is delayed by weeks.
- **Action metric:** a bottom-up, rSCI metric on the observable boundary that teams can optimize in real time.

### Boundary Model

We differentiate between:

- **Observable boundary:** a workloads' hardware reservations/utilization that we can use to compute the action metric.
- **Provider reporting boundary:** the finest slice at which the provider exposes the reporting metric.

Providers report carbon emissions $`C_\text{reported}`$ at a certain level of granularity, which we call the **reporting slice**, e.g.:

- **AWS:** `account × service × region × month`
- **GCP:** `project × SKU × region × month`
- **Azure:** `subscription × service_category × region × month`

Every measured workload event must map to one (or eventually also multiple) reporting slices.

### Residual Bridge

We call the gap between the top-down and bottom-up metric residual bridge.
It has two distinct sources:

1. **Residual carbon inside the observable boundary**: even with perfect workload telemetry, the top-down metric includes carbon you cannot observe bottom-up: facility overhead (PUE), idle infrastructure, embodied carbon from hardware you do not own, and non-energy emissions such as diesel backup generation or refrigerant losses.
2. **Boundary mismatch**: A provider may bundle supporting services — storage I/O, managed networking, control-plane operations — into the same reporting slice that you are only partially observing. Even if measurements are precise, a structural gap remains wherever the two boundaries do not coincide.
   - *Example: you instrument all EC2 instances in `eu-central-1` perfectly, but the provider's `Compute` slice for that account and region also includes EBS volume activity and NAT Gateway traffic that you have not instrumented. Your action total covers only a subset of what that number reflects.*

The goal is to make the bridge for each reporting slice **explicit** that users can understand how improving the action metric maps to improving the reporting metric.

Later, we will try to make the bridge as small as possible, by decomposing the residual into known components using prior knowledge / estimates (e.g., PUE, embodied carbon).
This could lead to a 1) more transparent and predictable action metric. Also, we could better quantify actual residual carbon (could be missing carbon!) by the cloud provider that cannot be explained by their methodology.


### Assumptions

For now (!), we assume
1. **no boundary mismatch**: the observable boundary covers all activity in the reporting slice.
  For example, if a customer wants to reconcile `EC2 × eu-central-1 × January`, we assume they can observe all EC2 resources they run in that region over that month with enough fidelity to reconstruct resource-time/utilization.
  This is a structural requirement, without full coverage the residual bridge loses its interpretation.
2. **one-to-one mapping**: each observed workload maps to exactly one reporting slice. This is a simplifying assumption that allows us to state the problem more clearly, but the framework should be extended to handle many-to-many mappings in practice (e.g. a workload that uses compute, storage and network or is distributed).
3. **single slice**: For simplicity, the approach currently assumes a single reporting slice: one project, one service, one region, one month.


## Method

We define an evaluation period $`t`$ as a fixed time window (e.g., 5 min) for interactive workloads, or the job's duration for batch workloads. All per-period quantities ($`E`$, $`I`$, $`R`$, $`O`$, oSCI, rSCI) are defined over one $`t`$.
Let $`m`$ be the individual machine/instance serving the workload.

### Power Model

For any $`t`$, the aggregate energy across all machines $`m`$:

$$E = \sum_m P_m \cdot \Delta t, \quad \text{where } P_m = \sum_r \text{count}_{m,r} \times P_r$$

Here $`m`$ indexes individual machines/instances, $`r`$ indexes resource types (vCPU, GPU, disk, network, ...), and $`P_r`$ is the rated power per unit of resource $`r`$ (e.g., TDP, a measured average, or a provider-published figure). The monthly total is $`E_\text{total} = \sum_t E`$.

This is a usage-based power model: $`P_m`$ depends on what you have provisioned (count × rated power), not on how hard you use it. It matches what all three providers allocate by at the customer level.

A more physical model would be $`P_m = \text{count} \times \text{util} \times P_r`$, but since no provider rewards utilization at the customer boundary, the utilization term does not help reconciliation.

We define:
- **Usage** — how many resources for how long (vCPU-hours, instance-hours, GPU-hours). This is what providers allocate by.
- **Utilization** — how hard you work the resource (CPU at 5% vs 95%). No provider reflects this in the customer-reported number.

The action metric (oSCI) captures both. The provider-reported number captures only usage. Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into the residual).

In practice, not all resource types are observable.
Unobservable components (e.g., IO energy) increase the residual.
The more components we can specify/derive, the smaller and more certain the residual becomes.

**Batch vs interactive workloads.** The structural distinction determines the evaluation period $`t`$. The choice of $`R`$ (functional unit) is independent and up to the user.

| Type | $`t`$ | Examples | Typical $`R`$ choices |
|---|---|---|---|
| **Batch** | Job duration (start to finish) | ML training, ETL pipeline, CI build | 1 (the job), GB processed, images generated |
| **Interactive** | Fixed window (e.g., 5 min) | Web API, LLM inference, database serving | requests, tokens, queries |

Both use the same formula: $`\text{oSCI} = E \cdot I / R`$. What differs is how $`t`$ is defined and which $`P_m`$ terms are observable (GPU, CPU, IO). Unobservable components (e.g., IO energy) increase the residual.

Key tension for interactive workloads: idle capacity (warm fleet consuming energy but not producing $`R`$) drives up oSCI in low-utilization windows. Whether to split this out or leave it in the residual is an open question.

### Operational Carbon

$$O = E \cdot I, \quad \text{oSCI} = O \;/\; R$$

Following Bashir et al. (2024), the action layer uses oSCI: embodied carbon is a sunk cost that should not influence scheduling decisions.

### Reconciliation

$$O_\text{total} = \sum_t O$$

$$\Delta_\text{residual} = C_\text{reported} - O_\text{total}$$

$`\Delta_\text{residual}`$ absorbs everything the action metric does not capture: embodied carbon, idle/shared capacity, non-energy overhead (PUE, Scope 1), allocation artifacts — and the estimation error in $`O`$ itself. In the cloud, $`O`$ is not measured but estimated: $`E`$ comes from power models (TDP-based, not metered), and $`I`$ is a grid-average approximation. The residual therefore includes $`\varepsilon_O = O_\text{true} - O_\text{estimated}`$. This is acceptable as long as the estimation error is approximately proportional across workloads — the reconciliation factor $`\gamma`$ absorbs any systematic bias. However, once the one-to-one assumption is relaxed and heterogeneous workloads share a slice, proportionality of $`\varepsilon_O`$ can no longer be assumed: a GPU instance's power model error differs structurally from a small CPU instance's. Without some bottom-up signal, there is no basis for distinguishing their contributions, and the residual allocation becomes arbitrary.

### rSCI

$$\text{rSCI} = (O_\text{total} + \Delta_\text{residual}) / R_\text{total} = C_\text{reported} / R_\text{total}$$

**Key property:** $`\sum_t \text{rSCI} \cdot R = C_\text{reported}`$

The reconciled metric distributes the full provider-reported footprint across periods in proportion to their operational carbon. Because the residual is allocated proportionally to $`O`$, rSCI **always preserves oSCI ordering** — reducing operational carbon always reduces rSCI, and it cannot produce perverse scheduling incentives. Yet each period's rSCI reflects its fair share of the full reported footprint, including embodied carbon and overhead.

Where:

- The action layer uses oSCI to avoid the sunk carbon fallacy (Bashir et al., 2024).
- $`\Delta_\text{residual}`$ is learned from historical slice pairs $`(O_\text{total}, C_\text{reported})`$.
- Unlike tSCI (which requires full infrastructure knowledge), rSCI learns the residual from the provider-reported total.
- The service index $`i`$ (partitioning within a slice) returns when the single-service assumption is relaxed.


## Estimation

**Goal:** estimate the residual bridge at the reporting slice before provider actuals arrive.

### Residual Bridge

The residual bridge $`\Delta_\text{residual}`$ is a single fitted scalar that captures everything the action metric does not: embodied carbon (hardware and buildings), facility overhead (PUE), idle/shared capacity, non-energy overhead (Scope 1 diesel/refrigerants, other Scope 3 categories), and allocation artifacts from provider methodology. Embodied carbon is deliberately excluded from the action layer to avoid the sunk carbon fallacy (Bashir et al., 2024) — it enters only through the residual. With monthly slice-level data, these components are not individually identifiable — the total bridge is constrained, but the breakdown is not. We therefore treat $`\Delta_\text{residual}`$ as one quantity fitted from historical slice pairs rather than pretending the components can be separated.

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


## Open Questions

1. **Actionability limits:** When a reporting slice is too coarse or too opaque, how should the framework expose that optimization claims are weak rather than presenting false precision?
2. **Lever reconcilability:** Which user actions move the reporting metric directly, approximately, or not at all under a given provider methodology?
3. **Minimum viable provider knowledge:** What minimum provider profile can be constructed from public documentation before the framework becomes too speculative? How many months of slice-level pairs $`(O_\text{total}, C_\text{reported})`$ are needed before the residual bridge estimate is decision-useful?
4. **Non-stationarity:** How should methodology changes trigger profile version updates and regime shifts in the model?
5. **Cold start:** Without historical slice pairs, $`\Delta_\text{residual}`$ is unknown and rSCI degrades to oSCI. The reconciliation claim is empty until calibrated. How should the framework communicate this? Options include: reporting confidence intervals that widen with fewer data points, falling back to provider-profile-derived priors (e.g., published PUE × typical embodied ratios), or explicitly labeling the estimate as "uncalibrated" until a minimum number of months are available. What is the minimum number of slice pairs needed before the residual estimate is decision-useful — and does this differ by provider methodology quality?
6. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports. If the provider's methodology is flawed (e.g., uses economic allocation that doesn't reflect physical reality, or applies uniform emission factors across regions with different grid mixes), rSCI faithfully reconciles to a misleading number. The framework makes this visible — a persistently large or volatile $`\Delta_\text{residual}`$ signals methodology weakness — but it cannot correct for it. How should the framework distinguish "high residual because provider methodology is coarse" from "high residual because we are missing observable activity"? Should provider methodology quality scores inform how the residual estimate is presented to users?
7. **Residual instability across months:** Model $`\Delta_\text{residual}`$ as time-varying, learned across months. This captures seasonal effects, methodology changes, and infrastructure evolution.
8. **PUE as a learnable parameter:** Factor out $`\alpha_\text{PUE}`$ from $`\Delta_\text{residual}`$ and include it in the action layer ($`O_i = \alpha_\text{PUE} \cdot E_i \cdot I`$), calibrated from provider-published PUE or historical data.
9. **Bridge decomposition:** Once sufficient historical slice pairs are available, decompose $`\Delta_\text{residual}`$ into provider-methodology-informed components (embodied carbon, PUE mismatch, idle capacity, non-energy overhead, allocation artifacts) using priors from provider profiles and Bayesian modeling. The goal is to identify whether any true unexplained residual remains after accounting for known methodology effects. This decomposition can progressively refine the residual without changing the action signal — oSCI ordering is preserved regardless of how the residual is broken down.
10. **Location dependence:** How should regional variation in residual composition (e.g., different PUE, grid mix, hardware vintages across regions) be modeled?
11. **Normative reference estimate:** a second, more methodologically complete estimate (covering omitted Scope 3 categories, questionable amortization, coarse allocation, provider-specific flaws) that makes visible the gap between what providers report and what a fuller methodology would report — comparative, not substitutive, and explicitly separate from the core reconciliation framework.
12. **IO energy modeling:** How to handle IO energy — proxy model per service type, or accept it in the residual?
13. **Idle capacity attribution:** Should warm-fleet idle energy be split out in the action metric, or left in the residual?
14. **Power model granularity:** How granular should $`P_r`$ estimates be? Per instance family? Per chip generation? Source: TDP, measured average, or provider-published?
15. **Utilization in the action metric:** Should oSCI include utilization (as a finer-grained optimization signal) even though it doesn't reconcile? Or keep the action metric usage-based to match what providers reward, and treat utilization as a separate diagnostic?
16. **Allocation of residual to heterogeneous workloads:** When the one-to-one assumption is relaxed and multiple heterogeneous workloads share a slice, how should the residual be allocated?

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific and provider-profile questions.


## Repository Structure

```text
├── README.md                            # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md     # detailed provider methodology comparison
├── SCHEMA.md                            # provider profile schema and populated profiles
├── references/SCI.md                    # Software Carbon Intensity standard
├── references/SCI_AI.md                 # SCI for AI standard
├── references/SCI_SUNK_CARBON.md        # Bashir et al. (2024) — sunk carbon fallacy, oSCI/tSCI
```
