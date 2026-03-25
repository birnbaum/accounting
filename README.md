# rSCI: Reconciled Software Carbon Intensity

**Problem**: Metrics that are reported by cloud providers for Scope 3 GHG reporting are not the same metrics that help individual teams reduce emissions. See e.g. [Measuring for Reporting vs. Measuring for Action](https://greensoftware.foundation/articles/measuring-for-reporting-vs-measuring-for-action).

- **Top-down methodology (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings.
It then allocates this total down to individual customers, services, and jobs.
This data is auditable (backed by invoices), comparable (not yet due to underspecified parts in the GHG protocol, but hopefully at some point), but coarse (usually one number per customer x service x region x month) and delayed (available 2-3 weeks after month-end).
It tells you the size of the problem but not what to do about it.
- **Bottom-up methodology (action):** We measure (or model based on proxies) workload energy as close to the hardware as possible, combine it with location-based carbon intensity, and report some kind of [SCI (Software Carbon Intensity)](https://sci.greensoftware.foundation/) signal in near real time.
This gives teams an optimization signal they can act on, but by itself it does not fully capture facility overhead, idle/shared capacity, provider-specific allocation effects, or all Scope 1/3 components.

These two signals cannot be identical.
**But they must be reconcilable**: If a team improves its bottom-up signal, that improvement should be traceable through to the cloud provider's reported number at the reporting boundary the provider actually exposes.
If the two diverge without explanation, users lose trust in both.

Note: We focus on **location-based accounting**. Market-based accounting is decoupled from physical consumption and therefore weak as an energy/carbon efficiency signal.

<details>

<summary>Why optimize toward imperfect accounting methodologies?</summary>

In practice, cloud customers' Scope 3 GHG accounting happens through the numbers providers report.
Those numbers are imperfect and provider methodologies remain heterogeneous and partially opaque.
Better standards are still needed, but even under imperfect reporting, users need a framework that maps actionable signals to the provider-reported number that governs reporting practice.

Goals of this framework:
- **For users:** provide an SCI-style metric per workload that sums up to the provider's delayed GHG report and makes uncertainties explicit.
- **For the ecosystem:** make GHG methodology quality visible by showing which energy/carbon efficiency optimization levers are rewarded, only approximately rewarded, or structurally blocked by provider accounting choices. This can inform/pressure better provider practices.
</details>


## Motivation

The GSF's Software Carbon Intensity was designed as an actionable optimization signal $$SCI = C / R,$$ which describes the carbon $C$ per unit of work $R$ (e.g., per request, per hour, per GB).
In their original formulation, carbon is the sum of operational carbon $`O`$ (energy $`E`$ × carbon intensity $`I`$) and amortized embodied carbon $`M`$:

$$C = E \cdot I + M$$

[Bashir et al. (2024)](https://arxiv.org/abs/2410.15087) showed that including $`M`$ can lead to perverse scheduling outcomes where carbon-aware schedulers route work to older, less efficient servers.
They proposed
- oSCI (operational only), which is the current state of the art for actionable carbon metrics and according to the authors, the best metric for carbon-aware scheduling.
- tSCI (where overhead of idle server are attributed to $`O`$ and $`M`$), but consider it impractical because it requires comprehensive datacenter-level information that cloud customers do not have access to.

We extend the taxonomy with **rSCI** (reconciled SCI): a variant that reconciles to the provider-reported total.

| Metric | $`C`$                                                   | Includes                                                            | Key limitation                               |
|--------|---------------------------------------------------------|---------------------------------------------------------------------|----------------------------------------------|
| SCI | $`E \cdot I + M`$                                       | Bottom-up operational + bottom-up embodied                          | Sunk carbon fallacy (Bashir et al.)          |
| oSCI | $`E \cdot I`$                                           | Bottom-up operational only                                          | Misses embodied and other overheads entirely |
| tSCI | $`E \cdot I + O_\text{idle-infra} + M + M_\text{idle-infra}`$ | SCI + bottom-up models for operational and embodied idle overhead   | Requires bottom-up datacenter knowledge      |
| **rSCI** | $`E \cdot I + w \cdot \hat{\Delta}`$                    | Operational + estimated fraction of residuals from reporting metric | (to be found out)                            |

where $`\hat{\Delta}`$ is the estimated residual bridge and $`w`$ the per-workload weighting factor. Details below.

<details>
<summary>Benefits of rSCI</summary>

- Shares tSCI's goal of allocating the full carbon footprint back to individual jobs, but practical: learns $`\Delta_{s,r}^{\text{S2}}`$ from historical ($`O`$, $`C^{\downarrow\text{S2}}`$) pairs; $`\Delta^{\text{S1}}`$ and $`\Delta^{\text{S3}}`$ come directly from the provider report.
- More comprehensive: captures *everything* between the bottom-up total and the provider-reported number, separated by scope.
- Does **not** suffer from the sunk carbon fallacy: embodied carbon enters via $`\Delta_{s,r}^{\text{S3}}`$ and is distributed by energy share ($`E_{i,s,r}/E_{s,r}`$), not attributed per-server. Old hardware → higher $`E`$ → more residual → always looks worse.
- **Does** reward scheduling toward lower-overhead infrastructure: $`\Delta_{s,r}^{\text{S2}}`$ and $`\Delta_{s,r}^{\text{S3}}`$ differ across services and regions. oSCI is blind to these factors.
</details>

<details>
<summary>Boundary mismatch assumption</summary>

We assume the observable boundary covers all activity in the reporting slice (no boundary mismatch).
A provider may bundle supporting services (storage I/O, managed networking) into a slice you only partially observe.
Without full coverage, the residual loses its interpretation.

*Example: you instrument all EC2 instances in `eu-central-1`, but the provider's `Compute` slice also includes EBS volume activity and NAT Gateway traffic.*
</details>



## Method

Let $`i`$ index workloads to be optimized by an individual $`rSCI_i`$.
Each workload has an evaluation period $`t_i`$ and all per-workload quantities like $`C_i`$ and $`R_i`$ are defined over one $`i`$.

| Type | $`t_i`$                  | Examples                                    | Typical $`R`$ choices                      |
|---|--------------------------|---------------------------------------------|--------------------------------------------|
| **Batch** | Job duration             | carbon per ML training, CI build, ...       | 1 (the job), GB processed, batches trained |
| **Interactive** | Fixed window | carbon per request, defined per 5min window | requests, tokens, queries                  |


### Energy Model

TODO: This dowes not yet fully match the concept and notation from the residual bridge section, needs to be aligned.

$$E_i = \sum_p q_p \times \varepsilon_p \quad [\text{Wh}]$$

where $`p`$ indexes resource types, $`q_p`$ is quantity consumed during $`t_i`$, and $`\varepsilon_p`$ is the energy coefficient (Wh/unit).

| Resource type | Unit ($`q_p`$) | $`\varepsilon_p`$ | Note                         |
|---|---|---|------------------------------|
| vCPU | vCPU-hours | Wh/vCPU-h | Reservation-based (= W/vCPU) |
| GPU | GPU-hours | Wh/GPU-h | Reservation-based (= W/vCPU) |
| Storage | GB-hours | Wh/GB-h | Reservation-based            |
| Disk I/O | IO operations | Wh/IO-op | Event-based                  |
| Network transfer | GB transferred | Wh/GB | Event-based                  |

Not all resource types are observable.
Unobservable components increase the residual.

<details>
<summary>Why usage-based, not utilization-based?</summary>

This is a usage-based energy model: $`E`$ depends on what you have provisioned or consumed ($`q \times \varepsilon`$), not on how hard you drive the resource.
No provider currently rewards utilization at the customer boundary (see [SCHEMA.md](SCHEMA.md)), so the utilization term does not help reconciliation.
Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into $`\Delta^{\text{S2}}`$).
</details>


### Residual Bridges $`\Delta`$

Providers report Scope 1, 2, and 3 separately per **reporting slice** (e.g., GCP: `project × service × region × month`).
We assume a workload does not span multiple projects and optimize within a single month (real-time scheduling signal).
Following, we index the top-down per-scope reported emissions $C^{\downarrow}$ by service $`s`$ and region $`r`$:

$$\Delta_{s,r}^{\text{S1}} = C_{s,r}^{\downarrow\text{S1}}, \qquad \Delta_{s,r}^{\text{S2}} = C_{s,r}^{\downarrow\text{S2}} - O_{s,r}, \qquad \Delta_{s,r}^{\text{S3}} = C_{s,r}^{\downarrow\text{S3}}$$

where $`O_{s,r} = \sum_i E_{i,s,r} \cdot I_r`$ is the bottom-up operational estimate.
Carbon intensity $`I_r`$ depends on the grid region.

- $`\Delta_{s,r}^{\text{S1}}`$ (Scope 1) is fully residual: diesel, refrigerants.
- $`\Delta_{s,r}^{\text{S2}}`$ (Scope 2 gap) is the power usage we cannot estimate bottom-up: PUE, idle capacity, power model error.
- $`\Delta_{s,r}^{\text{S3}}`$ (Scope 3) is fully residual: embodied hardware/datacenter, FERA, upstream transport, etc.

Since we can only compute each $`\Delta`$ once the provider report arrives, we need to estimate it for real-time optimization. TBD.

### Weighting factor $`w`$

...





### Reconciliation

Reconciliation is performed per service $`s`$ and region $`r`$.
By default, all residuals are allocated by energy share $`w_{i,s,r} = E_{i,s,r}/E_{s,r}`$:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_{s,r} \left( O_{i,s,r} + w_{i,s,r} \cdot \Delta_{s,r}^{\text{S1}} + w_{i,s,r} \cdot \Delta_{s,r}^{\text{S2}} + w_{i,s,r} \cdot \Delta_{s,r}^{\text{S3}} \right)$$

This collapses to:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_{s,r} E_{i,s,r} \left( I_r + \frac{\Delta_{s,r}^{\text{S1}} + \Delta_{s,r}^{\text{S2}} + \Delta_{s,r}^{\text{S3}}}{E_{s,r}} \right)$$

where $`I_r + (\Delta_{s,r}^{\text{S1}} + \Delta_{s,r}^{\text{S2}} + \Delta_{s,r}^{\text{S3}})/E_{s,r}`$ is the **effective carbon intensity** of service $`s`$ in region $`r`$.
The only workload-specific term is $`E_{i,s,r}`$.

**Reconciliation guarantee:** $`\sum_i w_{i,s,r} = 1 \implies \sum_i \text{rSCI}_i \cdot R_i = \sum_{s,r} C_{s,r}^{\downarrow}`$.

**Bridge decomposition.**
Energy-proportional allocation is a reasonable default but not structurally optimal for all components (e.g., embodied carbon depends on hardware type, not energy).
Each scope's residual can be further decomposed into sub-components $`k`$ with their own allocation keys $`w_{i,s,r}^k`$, as long as $`\sum_i w_{i,s,r}^k = 1`$:

| Component | Suggested allocation key |
|---|---|
| PUE (within $`\Delta^{\text{S2}}`$) | $`E_{i,s,r}/E_{s,r}`$ (scales with energy) |
| Idle capacity (within $`\Delta^{\text{S2}}`$) | Reservation size (idle cost follows capacity held) |
| Embodied carbon (within $`\Delta^{\text{S3}}`$) | Instance-hours × hardware cost/weight |
| Other | $`E_{i,s,r}/E_{s,r}`$ (default) |


## Open Questions

- Does the model hold for mixed batch and interactive workloads? 

1. **Energy coefficients:** Where to source reliable $`\varepsilon_p`$ values per resource type / instance family / chip generation? How sensitive is $`\Delta^{\text{S2}}`$ to $`\varepsilon_p`$ estimation error?
2. **Cold start and pooling:** Without historical data, $`\Delta_{s,r}^{\text{S2}}`$ is unknown (rSCI degrades to oSCI + raw overhead).
$`\gamma_{s,r} = C_{s,r}^{\downarrow\text{S2}} / O_{s,r}`$ is driven by provider methodology (PUE, emission factors), not individual customers — pooling $`\gamma`$ per provider × service × region could provide priors for new customers.
$`\Delta^{\text{S1}}`$ and $`\Delta^{\text{S3}}`$ need no calibration (directly from provider report).
3. **Non-stationarity and location dependence:** All residuals vary by region and over time (seasonal PUE, hardware refreshes, methodology changes).
How to model this and detect regime shifts?
4. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports.
A persistently large or volatile $`\Delta^{\text{S2}}`$ signals methodology weakness but cannot correct for it.
How to distinguish "coarse provider methodology" from "missing observable activity"?
5. **Normative reference estimate:** A second, more methodologically complete estimate that makes visible the gap between what providers report and what a fuller methodology would report — comparative, not substitutive.

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
