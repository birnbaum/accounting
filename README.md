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
| **rSCI** | $`E \cdot I + w \cdot \Delta^{\text{op}} + w \cdot \Delta^{\text{non-op}}`$ | oSCI + operational residual + non-operational overhead | ✨ (some historical data)                     |

where $`\Delta`$ is the **residual bridge**. Providers report Scope 1, 2, and 3 separately per slice, but Scope 1 (diesel, refrigerants) and Scope 3 (embodied carbon, FERA, transport) are not independent — empirically, $`\tilde{C}^{\text{S1}}/\tilde{C}^{\text{S3}}`$ is a fixed ratio per region. They collapse into a single non-operational term $`\tilde{C}^{\text{S1+3}}`$. The residual therefore has two structurally distinct parts:

$$\Delta = \underbrace{(\tilde{C}^{\text{S2}} - O)}_{\Delta^{\text{op}}} + \underbrace{\tilde{C}^{\text{S1+3}}}_{\Delta^{\text{non-op}}}$$

- $`\Delta^{\text{op}}`$: the gap between provider-reported location-based electricity carbon (Scope 2) and the bottom-up estimate $`O = \sum_i O_i`$. It captures PUE, emission factor differences, idle capacity allocation, and estimation error $`\varepsilon_O`$.
- $`\Delta^{\text{non-op}}`$: non-operational carbon (embodied hardware, diesel, refrigerants, upstream transport). Fully residual — no bottom-up signal can capture it. This is pure overhead allocation.


**Benefits of rSCI**
- it shares tSCI's goal of allocating the full carbon footprint back to individual jobs, but makes it practical: instead of requiring complete bottom-up datacenter knowledge, rSCI learns the gap from historical ($`O`$, $`\tilde{C}^{\text{S2}}`$) pairs and allocates the provider-reported non-operational overhead ($`\tilde{C}^{\text{S1+3}}`$).
- it is also more comprehensive in scope: where tSCI only adds idle server operational and embodied carbon, rSCI's residual captures *everything* between the observable operational total and the provider-reported number. The per-scope breakdown separates the operational gap ($`\Delta^{\text{op}}`$, which we can shrink by improving our energy model) from non-operational overhead ($`\Delta^{\text{non-op}}`$, which is structurally residual).
- it does **not** suffer from the sunk carbon fallacy (Bashir et al.): Embodied carbon enters via $`\tilde{C}_s^{\text{S1+3}}`$ and is distributed by energy usage ($`E_{i,s}/E_s`$), not attributed per-server. Old, inefficient hardware has higher $`E`$ → receives more residual → always looks worse. The mechanism that creates the sunk carbon fallacy (per-server embodied attribution) is structurally absent.
- but it **does** reward scheduling toward lower-overhead infrastructure. Because both $`\Delta_s^{\text{op}}`$ and $`\Delta_s^{\text{non-op}}`$ differ across slices (a region with older hardware, higher PUE, or more idle capacity has larger residuals), rSCI incentivizes placing work on lower-overhead infrastructure. These terms also change over time, e.g., fluctuating PUE, hardware refresh cycles. oSCI is blind to these factors.

## Problem Framing

### Metric Terminology
- **Reporting metric:** the top-down, provider-reported carbon (Scope 1, 2, and 3 separately) for GHG accounting, delayed by weeks.
- **Action metric:** a bottom-up, rSCI metric on the observable boundary that teams can optimize in real time.

### Boundary Model

We differentiate between:

- **Observable boundary:** a workloads' hardware reservations/utilization that we can use to compute the action metric.
- **Provider reporting boundary:** the finest slice at which the provider exposes the reporting metric.

Providers report carbon emissions at a certain level of granularity, which we call the **reporting slice**, e.g.:

- AWS: `account × service × region × month`
- GCP: `project × SKU × region × month`
- Azure: `subscription × service_category × region × month`

Within each slice, providers report Scope 1, 2, and 3 separately: $`\tilde{C}_s^{\text{S1}}`$, $`\tilde{C}_s^{\text{S2}}`$, $`\tilde{C}_s^{\text{S3}}`$. Empirically, $`\tilde{C}^{\text{S1}}/\tilde{C}^{\text{S3}}`$ is a fixed ratio per region (Scope 1 is ~1–2% of Scope 3), so they carry no independent information and collapse into $`\tilde{C}_s^{\text{S1+3}}`$. The total is $`\tilde{C}_s = \tilde{C}_s^{\text{S2}} + \tilde{C}_s^{\text{S1+3}}`$.

Every measured workload event maps to one or more reporting slices.

### Residual Bridge

We call the gap between the top-down and bottom-up metric residual bridge. The per-scope reporting gives us a natural first decomposition into two structurally distinct parts:

1. **Operational residual** $`\Delta_s^{\text{op}} = \tilde{C}_s^{\text{S2}} - O_s`$: the gap between the provider's reported location-based electricity carbon and our bottom-up estimate. Even with perfect workload telemetry, this gap persists because the provider's number includes facility overhead (PUE) and idle infrastructure that are invisible to the bottom-up model. It also includes estimation error in $`O`$ itself (energy coefficients, grid emission factor discrepancies). This is the part of the bridge we can **shrink** by improving our energy model.
2. **Non-operational residual** $`\Delta_s^{\text{non-op}} = \tilde{C}_s^{\text{S1+3}}`$: embodied carbon (hardware, buildings), diesel backup, refrigerant losses, upstream transport, FERA. No bottom-up signal can capture these — they are **fully residual** and can only be allocated as overhead.
3. **Boundary mismatch**: A provider may bundle supporting services — storage I/O, managed networking, control-plane operations — into the same reporting slice that you are only partially observing. Even if measurements are precise, a structural gap remains wherever the two boundaries do not coincide.
   - *Example: you instrument all EC2 instances in `eu-central-1` perfectly, but the provider's `Compute` slice for that account and region also includes EBS volume activity and NAT Gateway traffic that you have not instrumented. Your action total covers only a subset of what that number reflects.*
   - **Assumption**: For now, we assume no boundary mismatch: the observable boundary covers all activity in the reporting slice.
     I think this is a structural requirement, without full coverage the residual bridge loses its interpretation.

The goal is to make the bridge for each reporting slice **explicit** so that users can understand how improving the action metric maps to improving the reporting metric.

The per-scope decomposition is a free, provider-given first step. Within these two groups, further decomposition is possible (e.g., separating PUE from idle capacity within $`\Delta^{\text{op}}`$, or separating embodied carbon from FERA within $`\Delta^{\text{non-op}}`$). Each sub-component can then use a structurally appropriate allocation key.


## Method

Let $`i`$ index workloads. Each workload has an evaluation period $`t_i`$ and all per-workload quantities ($`E`$, $`I`$, $`R`$, $`O`$, oSCI, rSCI) are defined over one $`i`$.
We differentiate between two workload types:

| Type | $`t_i`$ | Examples | Typical $`R`$ choices |
|---|---|---|---|
| **Batch** | Job duration (start to finish) | ML training, ETL pipeline, CI build | 1 (the job), GB processed, images generated |
| **Interactive** | Fixed window (e.g., 5 min) | Web API, LLM inference, database serving | requests, tokens, queries |

### Energy Model

For workload $`i`$:

$$E_i = \sum_r q_r \times \varepsilon_r \quad [\text{Wh}]$$

Where $`r`$ indexes resource types, $`q_r`$ is the quantity of resource $`r`$ consumed during $`t_i`$, and $`\varepsilon_r`$ is the energy coefficient per unit of resource $`r`$ (Wh/unit).

| Resource type | Unit ($`q_r`$) | $`\varepsilon_r`$    | Note                                            |
|---|---|----------------------|-------------------------------------------------|
| vCPU | vCPU-hours | Wh/vCPU-h | Reservation-based, equals W/vCPU                |
| GPU | GPU-hours | Wh/GPU-h   | Same                                            |
| Storage | GB-hours | Wh/GB-h              | Reservation-based (provisioned capacity × time) |
| Disk I/O | IO operations | Wh/IO-op             | Event-based                                     |
| Network transfer | GB transferred | Wh/GB                | Event-based: no persistent reservation          |

For reservation-based resources (vCPU, GPU, storage), $`\varepsilon_r`$ equals the power draw in watts, since Wh per hour of reservation = W.
For event-based resources (network transfer, disk I/O), there is no persistent reservation. $`\varepsilon_r`$ is the energy per discrete unit consumed.

<details>

<summary>Why usage-based, not utilization-based?</summary>

This is a usage-based energy model: $`E`$ depends on what you have provisioned or consumed ($`q \times \varepsilon`$), not on how hard you drive the resource. It matches what all three providers allocate by at the customer level.

A more physical model would scale by utilization ($`q_r \times \text{util} \times \varepsilon_r`$), but no provider currently rewards utilization at the customer boundary (see [SCHEMA.md — Reconcilability Summary](SCHEMA.md)), so the utilization term does not help reconciliation.

- **Usage** — how many resources for how long, or how many units consumed (vCPU-hours, GB transferred, IO operations). This is what providers allocate by.
- **Utilization** — how hard you work the resource (CPU at 5% vs 95%). No provider reflects this in the customer-reported number.

The action metric (oSCI) captures both. The provider-reported number captures only usage. Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into the residual).
</details>

In practice, not all resource types are observable.
Unobservable components increase the residual.
The more components we can specify/derive, the smaller and more certain the residual becomes.


### Reconciliation

Since a workload may span multiple reporting slices $`s`$ (e.g., compute, storage, networking), reconciliation is performed **per slice**. The per-scope reporting gives us two residual terms per slice:

$$O_s = \sum_i O_{i,s}$$

$$\Delta_s^{\text{op}} = \tilde{C}_s^{\text{S2}} - O_s$$

$$\Delta_s^{\text{non-op}} = \tilde{C}_s^{\text{S1+3}}$$

$$\Delta_s = \Delta_s^{\text{op}} + \Delta_s^{\text{non-op}}$$

$`\Delta_s^{\text{op}}`$ absorbs everything inside the provider's Scope 2 that the action metric does not capture: PUE, idle/shared capacity, allocation artifacts — and the estimation error in $`O`$ itself. In the cloud, $`O`$ is not measured but estimated: $`E`$ comes from energy models (TDP-based, not metered), and $`I`$ is a grid-average approximation. The operational residual therefore includes $`\varepsilon_O = O_\text{true} - O_\text{estimated}`$.

$`\Delta_s^{\text{non-op}}`$ is the provider-reported non-operational carbon (embodied hardware, diesel, refrigerants, upstream transport). It has no bottom-up counterpart and is always fully allocated as overhead.

**Residual allocation and bridge decomposition.** By default, both residual terms are allocated by energy share: $`w_{i,s} = E_{i,s}/E_s`$. For the operational residual, this is natural — PUE and idle capacity scale with energy consumption. For the non-operational residual, energy-proportional allocation is a reasonable default but not structurally optimal: embodied carbon depends on hardware type, not energy consumption. When heterogeneous workloads share a slice (e.g., GPU and CPU instances), a single energy-proportional key may not capture structural differences in embodied carbon intensity.

Bridge decomposition generalizes the allocation. Within each of the two groups, further decompose into components:

$$\Delta_s^{\text{op}} = \sum_k \Delta_s^{\text{op},k} \qquad \Delta_s^{\text{non-op}} = \sum_k \Delta_s^{\text{non-op},k}$$

where each component $`k`$ is allocated by its own structurally appropriate key $`w_{i,s}^k`$. Energy-proportional allocation is the degenerate case where all $`w_{i,s}^k = E_{i,s}/E_s`$, collapsing the decomposed form back to the default. As components are identified and assigned better keys, allocation fairness improves without changing the reconciliation guarantee.

### rSCI

Workload $`i`$'s rSCI sums its reconciled contributions across all slices it touches:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_s \left( O_{i,s} + \sum_k w_{i,s}^k \cdot \Delta_s^{\text{op},k} + \sum_k w_{i,s}^k \cdot \Delta_s^{\text{non-op},k} \right)$$

where $`w_{i,s}^k`$ is workload $`i`$'s share of component $`k`$ in slice $`s`$. When no decomposition is available (default), all $`w_{i,s}^k = E_{i,s}/E_s`$, and the formula collapses to:

$$\text{rSCI}_i = \frac{1}{R_i} \sum_s \left( O_{i,s} + \frac{E_{i,s}}{E_s} \cdot \Delta_s^{\text{op}} + \frac{E_{i,s}}{E_s} \cdot \Delta_s^{\text{non-op}} \right) = \frac{1}{R_i} \sum_s E_{i,s} \left( I_s + \frac{\Delta_s^{\text{op}}}{E_s} + \frac{\Delta_s^{\text{non-op}}}{E_s} \right)$$

where the three terms inside the parentheses are the **effective carbon intensity** of slice $`s`$:
- $`I_s`$: grid carbon intensity (bottom-up)
- $`\Delta_s^{\text{op}}/E_s`$: operational overhead rate — PUE, idle capacity, emission factor gap per unit of energy
- $`\Delta_s^{\text{non-op}}/E_s`$: non-operational overhead rate — embodied carbon, diesel, refrigerants per unit of energy

The only workload-specific term is $`E_{i,s}`$.

**Key property (per slice):** As long as $`\sum_i w_{i,s}^k = 1`$ for each component $`k`$, we have $`\sum_i \text{rSCI}_i \cdot R_i = \sum_s \tilde{C}_s`$.

The reconciled metric distributes the full provider-reported footprint across workloads. In the default case, reducing energy usage always reduces both residual allocations and the operational term — all three independently lower rSCI. The per-scope decomposition makes the structure transparent: $`\Delta_s^{\text{op}}`$ is a quality signal we can shrink (by improving energy models, using better emission factors), while $`\Delta_s^{\text{non-op}}`$ is overhead that varies across slices but is not directly reducible by the workload. With further decomposition, component-specific keys may shift attribution relative to the default, but this reflects structurally fairer attribution.




## Open Questions

1. **Energy coefficients:** Where to source reliable $`\varepsilon_r`$ values for each resource type, and at what granularity (per instance family, per chip generation)? For reservation-based resources (vCPU, GPU), TDP and published benchmarks provide reasonable proxies. For event-based resources (network transfer, disk I/O), empirical data is scarce and provider-specific. Sources include TDP, measured averages, or provider-published figures. How sensitive is the residual to $`\varepsilon_r`$ estimation error?
2. **Cold start:** Without historical slice pairs, $`\Delta^{\text{op}}`$ is unknown and rSCI degrades to oSCI plus raw non-operational overhead allocation. The reconciliation claim is empty until calibrated. How should the framework communicate this? Options include: reporting confidence intervals that widen with fewer data points, falling back to provider-profile-derived priors (e.g., published PUE × typical embodied ratios), or explicitly labeling the estimate as "uncalibrated" until a minimum number of months are available. Note that $`\Delta^{\text{non-op}}`$ is immediately available from the provider report (no calibration needed). What is the minimum number of slice pairs needed before the operational residual estimate is decision-useful — and does this differ by provider methodology quality?
3. **Cross-customer pooling:** The operational residual ratio $`\gamma_s^{\text{op}} = \tilde{C}_s^{\text{S2}} / O_s`$ is largely driven by the provider's methodology, not the individual customer. Within a given provider × region × slice type, the same PUE and emission factors apply. A hierarchical model — pooled $`\gamma^{\text{op}}`$ per provider × region × slice type, with per-customer deviations — could let new customers inherit a calibrated prior immediately, solving the cold start problem. For the non-operational residual, $`\tilde{C}_s^{\text{S1+3}}`$ is directly available from the provider report and does not need pooling. Pooling at the sub-component level ($`\gamma_\text{PUE}`$, $`\gamma_\text{idle}`$) would be more stable than pooling the aggregate $`\gamma^{\text{op}}`$, since workload composition (GPU-heavy vs CPU-heavy) shifts the aggregate. Cross-provider pooling is likely too diffuse given methodology differences. Open design questions: privacy implications of sharing slice-level $`(O, \tilde{C}^{\text{S2}})`$ pairs (ratios only may suffice), detection of provider methodology changes as regime shifts at the pooled level, and minimum customer count per stratum before the pooled prior is useful.
4. **Bridge decomposition:** The per-scope breakdown ($`\Delta^{\text{op}}`$ vs $`\Delta^{\text{non-op}}`$) is a free, provider-given first decomposition. Within each group, further decomposition is the mechanism for fair residual allocation in heterogeneous slices. Each sub-component $`k`$ can use a structurally appropriate allocation key $`w_{i,s}^k`$:
   - **Within $`\Delta^{\text{op}}`$:**
     - **PUE:** proportional to energy $`E_{i,s}`$ (overhead scales with energy consumption)
     - **Idle capacity:** proportional to reservation size (idle cost follows capacity held, not work done)
     - **Emission factor gap / other:** default to $`E_{i,s}/E_s`$ until a better key is identified
   - **Within $`\Delta^{\text{non-op}}`$:**
     - **Embodied carbon:** instance-hours × hardware cost or weight (reflects actual hardware footprint per workload)
     - **FERA / upstream transport / other:** default to $`E_{i,s}/E_s`$

   For example, PUE could be factored out as a learnable parameter ($`O_i = \alpha_\text{PUE} \cdot E_i \cdot I`$), calibrated from provider-published PUE or historical data. As sub-components are separated and assigned their own keys, the residual allocation becomes fairer for heterogeneous slices while the reconciliation guarantee ($`\sum_i w_{i,s}^k = 1`$) is preserved. The goal is to identify whether any true unexplained residual remains after accounting for known methodology effects.
5. **Actionability limits:** What minimum provider profile can be constructed from public documentation before the framework becomes too speculative? How many months of slice-level pairs $`(O, \tilde{C}^{\text{S2}})`$ are needed before the operational residual estimate is decision-useful? When a reporting slice is too coarse or too opaque, how should the framework expose that optimization claims are weak rather than presenting false precision?
6. **Location dependence:** How should regional variation in residual composition (e.g., different PUE, grid mix, hardware vintages across regions) be modeled?
7. **Non-stationarity:** Both $`\Delta^{\text{op}}`$ and $`\Delta^{\text{non-op}}`$ should be modeled as time-varying, learned across months, to capture seasonal effects (PUE), methodology changes, and infrastructure evolution (hardware refresh cycles shifting embodied carbon). How should methodology changes trigger profile version updates and regime shifts in the model?
8. **Provider methodology opacity:** rSCI reconciles to whatever the provider reports. If the provider's methodology is flawed (e.g., uses economic allocation that doesn't reflect physical reality, or applies uniform emission factors across regions with different grid mixes), rSCI faithfully reconciles to a misleading number. The framework makes this visible — a persistently large or volatile $`\Delta^{\text{op}}`$ signals methodology weakness — but it cannot correct for it. How should the framework distinguish "high operational residual because provider methodology is coarse" from "high residual because we are missing observable activity"? Should provider methodology quality scores inform how the residual estimate is presented to users?
9. **Normative reference estimate:** a second, more methodologically complete estimate (covering omitted Scope 3 categories, questionable amortization, coarse allocation, provider-specific flaws) that makes visible the gap between what providers report and what a fuller methodology would report — comparative, not substitutive, and explicitly separate from the core reconciliation framework.

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