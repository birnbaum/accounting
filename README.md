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

| Metric | $`C`$                                             | Includes                                                            | Key limitation                               |
|--------|---------------------------------------------------|---------------------------------------------------------------------|----------------------------------------------|
| SCI | $`E \cdot I + M`$                                 | Bottom-up operational + bottom-up embodied                          | Sunk carbon fallacy (Bashir et al.)          |
| oSCI | $`E \cdot I`$                                     | Bottom-up operational only                                          | Misses embodied and other overheads entirely |
| tSCI | $`E \cdot I + O_\text{idle-infra} + M + M_\text{idle-infra}`$ | SCI + bottom-up models for operational and embodied idle overhead   | Requires bottom-up datacenter knowledge      |
| **rSCI** | $`E \cdot I + w \cdot \Delta`$                    | Operational + estimated fraction of residuals from reporting metric | (to be found out)                            |

where $`\Delta`$ is the residual bridge and $`w`$ the per-workload weighting factor. Details below.

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



## rSCI Definition

Let $`i`$ index **workload instances** — one evaluation of a workload over its period $`t_i`$.
All per-instance quantities ($`E_i`$, $`C_i`$, $`R_i`$) are defined over one $`i`$.
There are two common workload types:
- **Batch**: discrete jobs with a clear start and end where $`t_i`$ is the job duration and $`R_i`$ is a job-level quantity, e.g., 1 (the job), GB processed, or batches trained.
- **Interactive**: continuous services where $`t_i`$ is a fixed window (e.g., 5min) and $`R_i`$ is a request-level quantity, e.g., number of requests, tokens, or queries.


### Energy Model

We define the bottom-up energy estimate for workload $`i`$ within service $`s`$ and region $`r`$ as:

$$E_{i,s,r} = \sum_p q_p \cdot \varepsilon_p \quad [\text{Wh}]$$

where $`p`$ indexes resource types, $`q_p`$ is quantity consumed during $`t_i`$, and $`\varepsilon_p`$ is the energy coefficient (Wh/unit).
The workload-level total is $`E_i = \sum_{s,r} E_{i,s,r}`$.

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

This is a usage-based energy model: $`E`$ depends on what you have provisioned or consumed ($`q \cdot \varepsilon`$), not on how hard you drive the resource.
No provider currently rewards utilization at the customer boundary (see [SCHEMA.md](SCHEMA.md)), so the utilization term does not help reconciliation.
Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into $`\Delta^{\text{S2}}`$).
</details>


### Residual Bridges $`\Delta`$

Providers report Scope 1, 2, and 3 separately per **reporting slice** (e.g., GCP: `project × service × region × month`).
We assume a workload does not span multiple projects and optimize within a single month (real-time scheduling signal).
Following, we index the top-down per-scope reported emissions $`C^{\downarrow S1}`$, $`C^{\downarrow S2}`$, and $`C^{\downarrow S3}`$ by service $`s`$ and region $`r`$. We define the residual bridges:

- $`\Delta_{s,r}^{\text{S1}} = C_{s,r}^{\downarrow\text{S1}}`$ (Scope 1) is fully residual: diesel, refrigerants.
- $`\Delta_{s,r}^{\text{S2}} = C_{s,r}^{\downarrow\text{S2}} - O_{s,r}`$ (Scope 2 gap) is the power usage we cannot estimate bottom-up: PUE, idle capacity, power model error.
- $`\Delta_{s,r}^{\text{S3}} = C_{s,r}^{\downarrow\text{S3}}`$ (Scope 3) is fully residual: embodied hardware/datacenter, FERA, upstream transport, etc.

where 
$$O_{s,r} = \sum_i E_{i,s,r} \cdot I_r$$ 
is the bottom-up operational estimate.
Carbon intensity $`I_r`$ depends on the grid region.




### Reconciliation

Reconciliation is performed per $`(s,r)`$.
By default, all residuals are allocated by energy share 
$$w_{i,s,r} = E_{i,s,r}/E_{s,r}$$

We define:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_{s,r} \left(O_{i,s,r} +  w_{i,s,r} \left(\Delta_{s,r}^{\text{S1}} + \Delta_{s,r}^{\text{S2}} + \Delta_{s,r}^{\text{S3}} \right)\right)$$

Since $`O_{i,s,r} = E_{i,s,r} \cdot I_r`$, this collapses to:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_{s,r} E_{i,s,r} \cdot \xi_{s,r}$$

where
$$\xi_{s,r} = I_r + \frac{\Delta_{s,r}^{\text{S1}} + \Delta_{s,r}^{\text{S2}} + \Delta_{s,r}^{\text{S3}}}{E_{s,r}}$$
is the **effective carbon intensity** of service $`s`$ in region $`r`$.
The only workload-specific term is $`E_{i,s,r}`$.

Since, by construction, $`\sum_i w_{i,s,r} = 1 \implies \sum_i \text{rSCI}_i \cdot R_i = \sum_{s,r} C_{s,r}^{\downarrow}`$.

**Bridge decomposition.**
Energy-proportional allocation is a reasonable default but *maybe* not structurally optimal for all components (e.g., embodied carbon depends on hardware type, not energy).
Each scope's residual can be further decomposed into sub-components $`k`$ with their own allocation keys $`w_{i,s,r}^k`$, as long as $`\sum_i w_{i,s,r}^k = 1`$:
- PUE overhead can meaningfully be allocated by energy share since it scales with energy.
- Idle capacity overhead may be better allocated by reservation size since it follows capacity held, not energy.
- Embodied carbon may be better allocated by instance-hours × hardware cost/weight.


## Real-time Estimation

The retrospective rSCI requires $`\Delta`$ (from the provider report, delayed weeks) and $`E_{s,r}`$ (total slice energy, known only after the reporting period).
To use rSCI as a real-time optimization signal, we estimate $`\xi_{s,r}`$ from the most recent reconciled month.

**Why $`\xi`$ is approximately stable across months.**
Providers allocate all overhead — embodied, idle, facility — proportionally to SKU usage.
Both $`C^{\downarrow}_{s,r}`$ and $`O_{s,r}`$ therefore scale linearly with resource consumption, so $`\xi_{s,r} = C^{\downarrow}_{s,r} / E_{s,r}`$ is approximately load-independent.

**Factoring out grid intensity.**
Grid carbon intensity $`I_r`$ is volatile (varies hourly) but observable in real time and should not be estimated from last month.
Decomposing $`\xi`$ by scope:

$$\xi_{s,r} = \mu_{s,r} \cdot I_r + \rho_{s,r}$$

where:
- $`\mu_{s,r} = C_{s,r}^{\downarrow\text{S2}} / (E_{s,r} \cdot I_r)`$ is the **Scope 2 multiplier** (dimensionless; captures PUE and energy model error)
- $`\rho_{s,r} = (C_{s,r}^{\downarrow\text{S1}} + C_{s,r}^{\downarrow\text{S3}}) / E_{s,r}`$ is the **non-electricity overhead intensity** (gCO2eq/Wh; Scope 1 + 3)

Both are slow-moving and load-independent.
$`\rho`$ can be split by scope for diagnostics if the provider reports Scope 1 and 3 separately.

The real-time estimate is then:

$$\widehat{\text{rSCI}}_i = \frac{1}{R_i} \sum_{s,r} E_{i,s,r} \left( \hat{\mu}_{s,r} \cdot I_r + \hat{\rho}_{s,r} \right)$$

where $`I_r`$ is the current grid intensity and $`\hat{\mu}`$, $`\hat{\rho}`$ are from the last reconciled month.

**Graceful degradation:** without any history, $`\hat{\mu} = 1`$, $`\hat{\rho} = 0`$, and $`\widehat{\text{rSCI}}`$ reduces to oSCI.


## Open Questions

1. **Energy coefficients:** Where to source reliable $`\varepsilon_p`$ values per resource type / instance family / chip generation?
Practical starting points: [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) (per-instance power estimates from SPECpower data), SPECpower benchmarks mapped to cloud SKUs, or GCP's per-project energy export for calibration.
Note: absolute $`\varepsilon_p`$ error is absorbed by $`\mu`$ (overestimate $`\varepsilon`$ → higher $`E`$ → lower $`\mu`$; reconciliation still holds).
The real sensitivity is *relative* accuracy across resource types — if $`\varepsilon_{\text{GPU}}/\varepsilon_{\text{vCPU}}`$ is wrong, workloads are compared on a skewed basis.
2. **Cold start and pooling:** Without historical data, $`\hat{\mu}`$ and $`\hat{\rho}`$ are unknown ($`\widehat{\text{rSCI}}`$ degrades to oSCI).
Since $`\mu`$ and $`\rho`$ are driven by provider methodology (PUE, hardware mix), not individual customers, pooling per provider × service × region could provide priors for new customers.
3. **Non-stationarity:** $`\mu`$ and $`\rho`$ can drift over time (seasonal PUE, hardware refreshes, methodology changes).
How to detect regime shifts and update estimates?
4. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports.
A persistently large or volatile $`\Delta^{\text{S2}}`$ signals methodology weakness but cannot correct for it.
How to distinguish "coarse provider methodology" from "missing observable activity"?
Should we provide a second, more methodologically complete estimate that makes visible the gap between what providers report and what a "ideal" methodology would report?

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
