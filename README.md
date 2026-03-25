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
| **rSCI** | $`E \cdot I + w \cdot (\Delta^{\text{S1}} + \Delta^{\text{S2}} + \Delta^{\text{S3}})`$ | oSCI + per-scope residuals | Requires some historical data |

### Residual Bridge

Providers report Scope 1, 2, and 3 separately per **reporting slice** $`s`$ (e.g., GCP: `project × service × region × month`). This gives three residual terms:

$$\Delta_s^{\text{S1}} = \tilde{C}_s^{\text{S1}}, \qquad \Delta_s^{\text{S2}} = \tilde{C}_s^{\text{S2}} - O_s, \qquad \Delta_s^{\text{S3}} = \tilde{C}_s^{\text{S3}}$$

where $`O_s = \sum_i E_{i,s} \cdot I_s`$ is the bottom-up operational estimate for slice $`s`$.

- $`\Delta^{\text{S2}}`$ (Scope 2 gap): PUE, idle capacity, emission factor differences, estimation error. The part we can **shrink**.
- $`\Delta^{\text{S1}}`$ (Scope 1): diesel, refrigerants. Fully residual — pure overhead.
- $`\Delta^{\text{S3}}`$ (Scope 3): embodied hardware, FERA, upstream transport. Fully residual — pure overhead.

Current empirical observation: $`\tilde{C}^{\text{S1}}/\tilde{C}^{\text{S3}}`$ is a fixed ratio per region (~1–2%), so S1 and S3 carry no independent information today. We keep them separate in the formulation for generality.

**Why rSCI avoids the sunk carbon fallacy:** Embodied carbon enters via $`\Delta_s^{\text{S3}}`$ and is distributed by energy share, not attributed per-server. Old hardware → higher $`E`$ → more residual → always looks worse.

<details>
<summary>Boundary mismatch</summary>

We assume the observable boundary covers all activity in the reporting slice (no boundary mismatch). A provider may bundle supporting services (storage I/O, managed networking) into a slice you only partially observe. Without full coverage, the residual loses its interpretation.

*Example: you instrument all EC2 instances in `eu-central-1`, but the provider's `Compute` slice also includes EBS volume activity and NAT Gateway traffic.*
</details>


## Method

Let $`i`$ index workloads. Each workload has an evaluation period $`t_i`$ and all per-workload quantities are defined over one $`i`$.

| Type | $`t_i`$ | Examples | Typical $`R`$ choices |
|---|---|---|---|
| **Batch** | Job duration (start to finish) | ML training, ETL pipeline, CI build | 1 (the job), GB processed, images generated |
| **Interactive** | Fixed window (e.g., 5 min) | Web API, LLM inference, database serving | requests, tokens, queries |

### Energy Model

$$E_i = \sum_r q_r \times \varepsilon_r \quad [\text{Wh}]$$

where $`r`$ indexes resource types, $`q_r`$ is quantity consumed during $`t_i`$, and $`\varepsilon_r`$ is the energy coefficient (Wh/unit).

| Resource type | Unit ($`q_r`$) | $`\varepsilon_r`$ | Note |
|---|---|---|---|
| vCPU | vCPU-hours | Wh/vCPU-h | Reservation-based (= W/vCPU) |
| GPU | GPU-hours | Wh/GPU-h | Same |
| Storage | GB-hours | Wh/GB-h | Reservation-based |
| Disk I/O | IO operations | Wh/IO-op | Event-based |
| Network transfer | GB transferred | Wh/GB | Event-based |

Not all resource types are observable. Unobservable components increase the residual.

<details>
<summary>Why usage-based, not utilization-based?</summary>

This is a usage-based energy model: $`E`$ depends on what you have provisioned or consumed ($`q \times \varepsilon`$), not on how hard you drive the resource. No provider currently rewards utilization at the customer boundary (see [SCHEMA.md](SCHEMA.md)), so the utilization term does not help reconciliation. Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into $`\Delta^{\text{S2}}`$).
</details>

### Reconciliation

Reconciliation is performed **per slice** $`s`$. By default, all residuals are allocated by energy share $`w_{i,s} = E_{i,s}/E_s`$:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_s \left( O_{i,s} + w_{i,s} \cdot \Delta_s^{\text{S1}} + w_{i,s} \cdot \Delta_s^{\text{S2}} + w_{i,s} \cdot \Delta_s^{\text{S3}} \right)$$

This collapses to:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_s E_{i,s} \left( I_s + \frac{\Delta_s^{\text{S1}} + \Delta_s^{\text{S2}} + \Delta_s^{\text{S3}}}{E_s} \right)$$

where $`I_s + (\Delta_s^{\text{S1}} + \Delta_s^{\text{S2}} + \Delta_s^{\text{S3}})/E_s`$ is the **effective carbon intensity** of slice $`s`$. The only workload-specific term is $`E_{i,s}`$.

**Reconciliation guarantee:** $`\sum_i w_{i,s} = 1 \implies \sum_i \text{rSCI}_i \cdot R_i = \sum_s \tilde{C}_s`$.

**Bridge decomposition.** Energy-proportional allocation is a reasonable default but not structurally optimal for all components (e.g., embodied carbon depends on hardware type, not energy). Each scope's residual can be further decomposed into sub-components $`k`$ with their own allocation keys $`w_{i,s}^k`$, as long as $`\sum_i w_{i,s}^k = 1`$:

| Component | Suggested allocation key |
|---|---|
| PUE (within $`\Delta^{\text{S2}}`$) | $`E_{i,s}/E_s`$ (scales with energy) |
| Idle capacity (within $`\Delta^{\text{S2}}`$) | Reservation size (idle cost follows capacity held) |
| Embodied carbon (within $`\Delta^{\text{S3}}`$) | Instance-hours × hardware cost/weight |
| Other | $`E_{i,s}/E_s`$ (default) |


## Open Questions

1. **Energy coefficients:** Where to source reliable $`\varepsilon_r`$ values per resource type / instance family / chip generation? How sensitive is $`\Delta^{\text{S2}}`$ to $`\varepsilon_r`$ estimation error?
2. **Cold start and pooling:** Without historical slice pairs, $`\Delta^{\text{S2}}`$ is unknown (rSCI degrades to oSCI + raw overhead). $`\gamma_s = \tilde{C}_s^{\text{S2}} / O_s`$ is driven by provider methodology (PUE, emission factors), not individual customers — pooling $`\gamma`$ per provider × region × slice type could provide priors for new customers. $`\Delta^{\text{S1}}`$ and $`\Delta^{\text{S3}}`$ need no calibration (directly from provider report).
3. **Non-stationarity and location dependence:** All residuals vary by region and over time (seasonal PUE, hardware refreshes, methodology changes). How to model this and detect regime shifts?
4. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports. A persistently large or volatile $`\Delta^{\text{S2}}`$ signals methodology weakness but cannot correct for it. How to distinguish "coarse provider methodology" from "missing observable activity"?
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
