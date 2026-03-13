# Layer 1: Service-Specific Energy Methodology

## Goal

Define how to derive $`E(t)`$ (energy per time window) and $`R(t)`$ (functional unit per time window) for each service type. The energy model must mirror what the provider's methodology actually rewards — the provider profile (layer 2) selects/constrains which power model layer 1 uses.

## General Form

For any time window $`t`$, the aggregate energy across all machines $`m`$:

$$E(t) = \sum_m P_m(t) \cdot \Delta t, \quad \text{where } P_m(t) = \sum_r \text{count}_{m,r} \times \text{util}_{m,r}(t) \times \text{TDP}_r$$

Here $`m`$ indexes individual machines/instances and $`r`$ indexes resource types (vCPU, GPU, disk, network, ...). The monthly total is $`E_\text{total} = \sum_t E(t)`$.

In practice, not all resource types are observable. Unobservable components (e.g., IO energy) increase the residual. The more components we can specify/derive, the smaller and more certain the residual becomes — but the framework should work with minimal information.

## Provider Methodology Determines the Power Model

The physical energy model is service-specific, but the **provider's allocation method** determines which version of the model you actually use:

| Allocation method | $`P_m(t)`$ model | Example |
|---|---|---|
| **Physical** (actual energy) | $`P_m(t) = \text{count} \times \text{util}(t) \times \text{TDP}`$ | GCP electricity-related emissions |
| **Time-based** (hours reserved) | $`P_m(t) = \text{TDP}`$ (utilization irrelevant) | AWS foundational services |
| **Economic** (spend-based) | $`P_m(t) \propto \text{cost}`$ (physical energy irrelevant) | AWS non-foundational, Azure |

## Optimization Levers and Reconcilability

Three provider methodology dimensions can break known optimization levers:

| Methodology dimension | What it breaks | Detail |
|---|---|---|
| **Allocation method** (physical vs time vs economic) | Compute efficiency, hardware efficiency | If time-based: reducing CPU utilization doesn't move the number. If economic: a more efficient but pricier instance can paradoxically increase reported carbon. |
| **Temporal resolution of carbon intensity** (hourly vs monthly) | Temporal shifting | Monthly-average $`I`$ flattens intra-day grid variation. Shifting a job to a cleaner hour has no effect on the reported number. |
| **Spatial resolution of emission factors** (regional vs national vs global) | Spatial shifting | If the provider uses a single national/global factor, moving workloads to a cleaner region doesn't reconcile. |

Current provider status:

| Lever | GCP | AWS | Azure |
|---|---|---|---|
| **Compute efficiency** (reduce utilization) | Reconciles (physical allocation) | Partially (time-based for foundational) | Weak (economic allocation) |
| **Temporal shifting** (run when grid is cleaner) | Reconciles (hourly Electricity Maps) | Doesn't reconcile (monthly/annual factors) | Doesn't reconcile (monthly/annual factors) |
| **Spatial shifting** (run in cleaner region) | Reconciles | Reconciles | Reconciles |
| **Hardware efficiency** (newer instance type) | Reconciles (less energy drawn) | Partially (less time, but same hourly rate) | May not reconcile (newer instances can cost more) |
| **Right-sizing** (smaller instance) | Reconciles | Reconciles (less time or lower rate) | Reconciles (lower cost) |

## Example Workloads

Four workload patterns along two axes: **batch vs interactive** and **$`R`$ per job vs $`R`$ per metric**.

|  | $`R`$ per job | $`R`$ per metric |
|---|---|---|
| **Batch** | 1. ML training job | 2. ETL pipeline |
| **Interactive** | 3. Web API | 4. LLM inference |

### 1. Batch / $`R`$ per job — ML Training

- **Pattern:** GPU training run. Runs for hours/days at ~100% GPU utilization, then terminates.
- $`P_m(t) = n_\text{gpu} \times \text{TDP}_\text{gpu} + n_\text{vcpu} \times \text{util}_\text{cpu}(t) \times \text{TDP}_\text{vcpu}`$
- $`E_\text{job} = \sum_t \sum_m P_m(t) \cdot \Delta t`$ — energy of the entire run.
- $`R = 1`$ (the job). Only meaningful when comparing equally sized jobs (same model, same dataset).
- $`\text{oSCI} = E_\text{job} \cdot \bar{I}^\star / 1`$ — carbon per job. $`\bar{I}^\star`$ is the time-weighted average intensity over the run.
- **Notes:** Simplest case — near-100% utilization, ephemeral, no idle cost. $`R = 1`$ means oSCI is just total carbon; useful for comparing scheduling decisions (when to run, where to run) across identical jobs.

### 2. Batch / $`R`$ per metric — ETL Pipeline

- **Pattern:** Nightly data transformation. Mixes CPU compute with heavy disk/network IO. Scheduled, idle between runs.
- $`P_m(t) = n_\text{vcpu} \times \text{util}_\text{cpu}(t) \times \text{TDP}_\text{vcpu} + \;???`$ (IO energy not observable)
- $`E_\text{job} = \sum_t \sum_m P_m(t) \cdot \Delta t`$ — energy of the entire run, CPU-only estimate.
- $`R`$ = GB processed (or records transformed).
- $`\text{oSCI} = E_\text{job} \cdot \bar{I}^\star / R`$ — carbon per GB processed.
- **Notes:** CPU-only $`E`$ understates real energy; IO energy falls into the residual. Good test case for "minimal information" — framework works with CPU-only $`E`$ at the cost of a larger residual.

### 3. Interactive / $`R`$ per request — Web API

- **Pattern:** Fleet of VMs serving HTTP requests, stable utilization ~40-70%, horizontal scaling.
- $`P_m(t) = n_\text{vcpu} \times \text{util}_\text{cpu}(t) \times \text{TDP}_\text{vcpu}`$
- $`E(t) = \sum_m P_m(t) \cdot \Delta t`$
- $`R(t)`$ = requests in time window $`t`$.
- $`\text{oSCI}(t) = E(t) \cdot I^\star(t) \;/\; R(t)`$ — carbon per request.
- **Notes:** Straightforward case. CPU utilization is observable and is the main lever. Idle fleet capacity (scaled up but not serving) is attributed to the time windows where it occurs.

### 4. Interactive / $`R`$ per metric — LLM Inference

- **Pattern:** Serving model predictions. GPU utilization swings with traffic (10-90%). Fleet must stay warm, so idle cost is real.
- $`P_m(t) = n_\text{gpu} \times \text{util}_\text{gpu}(t) \times \text{TDP}_\text{gpu} + n_\text{vcpu} \times \text{util}_\text{cpu}(t) \times \text{TDP}_\text{vcpu}`$
- $`E(t) = \sum_m P_m(t) \cdot \Delta t`$
- $`R(t)`$ = tokens generated in time window $`t`$.
- $`\text{oSCI}(t) = E(t) \cdot I^\star(t) \;/\; R(t)`$ — carbon per token.
- **Notes:** Idle GPU capacity is the key tension — physically consuming energy but not producing tokens. Time windows with low utilization have high $`\text{oSCI}(t)`$, making idle cost visible in the action signal.

## What's Common Across Workloads

- Energy is always $`P_m(t) = \sum_r \text{count}_r \times \text{util}_r(t) \times \text{TDP}_r`$ per machine, aggregated as $`E(t) = \sum_m P_m(t) \cdot \Delta t`$ per time window
- For batch workloads, $`E_\text{job} = \sum_t E(t)`$ over the run; for interactive, $`E(t)`$ is the natural unit
- $`R`$ is always a domain-specific functional unit: per job (batch) or per time window (interactive)
- Monthly totals are aggregated: $`E_\text{total} = \sum_t E(t)`$, $`R_\text{total} = \sum_t R(t)`$
- The provider profile determines whether utilization matters for reconciliation
- Unobservable resource energy (IO, memory) increases the residual

## What Differs

- **Batch vs interactive:** batch workloads have a natural job boundary; interactive workloads use time windows
- **$`R`$ per job vs $`R`$ per metric:** per-job $`R`$ only makes sense for comparable jobs; per-metric $`R`$ enables cross-workload comparison
- Which resources dominate (CPU-only vs GPU-dominant vs mixed)
- Idle cost (always-on fleets vs ephemeral jobs)
- IO energy observability

## Open

- How to handle IO energy: proxy model per service type, or accept it in the residual?
- Idle capacity attribution: should warm-fleet idle energy be split out in the action metric, or left in the residual?
- How granular should TDP estimates be? Per instance family? Per chip generation?
- What is the minimum viable $`E(t)`$ model — just CPU/GPU utilization × time × a rough TDP estimate?
