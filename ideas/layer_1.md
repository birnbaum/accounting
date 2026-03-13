# Layer 1: Service-Specific Energy Methodology

## Goal

Define how to derive $`E`$ (energy per evaluation period) and $`R`$ (functional unit per evaluation period) for each service type. The evaluation period $`t`$ is a fixed time window for interactive workloads or the job's duration for batch workloads (see README Notation). The energy model must mirror what the provider's methodology actually rewards — the provider profile (layer 2) selects/constrains which power model layer 1 uses.

## General Form

For any evaluation period $`t`$, the aggregate energy across all machines $`m`$:

$$E = \sum_m P_m \cdot \Delta t, \quad \text{where } P_m = \sum_r \text{count}_{m,r} \times \text{util}_{m,r} \times \text{TDP}_r$$

Here $`m`$ indexes individual machines/instances and $`r`$ indexes resource types (vCPU, GPU, disk, network, ...). The monthly total is $`E_\text{total} = \sum_t E`$.

In practice, not all resource types are observable. Unobservable components (e.g., IO energy) increase the residual. The more components we can specify/derive, the smaller and more certain the residual becomes — but the framework should work with minimal information.

## Provider Methodology Determines the Power Model

The physical energy model is service-specific, but the **provider's allocation method** determines which version of the model you actually use:

| Allocation method | $`P_m`$ model | Example |
|---|---|---|
| **Physical** (actual energy) | $`P_m = \text{count} \times \text{util} \times \text{TDP}`$ | GCP electricity-related emissions |
| **Time-based** (hours reserved) | $`P_m = \text{TDP}`$ (utilization irrelevant) | AWS foundational services |
| **Economic** (spend-based) | $`P_m \propto \text{cost}`$ (physical energy irrelevant) | AWS non-foundational, Azure |

## Optimization Levers and Reconcilability

Three provider methodology dimensions can break known optimization levers:

| Methodology dimension | What it breaks | Detail |
|---|---|---|
| **Allocation method** (physical vs time vs economic) | Compute efficiency, hardware efficiency | If time-based: reducing CPU utilization doesn't move the number. If economic: a more efficient but pricier instance can paradoxically increase reported carbon. |
| **Temporal resolution of carbon intensity** (hourly vs monthly) | Temporal shifting | Monthly-average $`I`$ flattens intra-day grid variation. Shifting a job to a cleaner hour has no effect on the reported number. |
| **Spatial resolution of emission factors** (regional vs national vs global) | Spatial shifting | If the provider uses a single national/global factor, moving workloads to a cleaner region doesn't reconcile. |

Current provider status:

| Lever | GCP                                  | AWS                                    | Azure |
|---|--------------------------------------|----------------------------------------|---|
| **Compute efficiency** (reduce utilization) | ✅ (physical allocation)              | ⚠️ (time-based for foundational) | ❌ (economic allocation) |
| **Temporal shifting** (run when grid is cleaner) | ✅ (hourly Electricity Maps) | ❌ (monthly/annual factors)             | ❌ (monthly/annual factors) |
| **Spatial shifting** (run in cleaner region) | ✅                           | ✅                                      | ✅ |
| **Hardware efficiency** (newer instance type) | ✅ (less energy drawn)       | ⚠️ (less time, but same hourly rate)   | ❌ (newer instances can cost more) |
| **Right-sizing** (smaller instance) | ✅                           | ✅ (less time or lower cost)            | ✅ (lower cost) |

## Example Workloads

Four workload patterns along two axes: **batch vs interactive** and **$`R`$ per job vs $`R`$ per metric**.

|  | $`R`$ per job | $`R`$ per metric |
|---|---|---|
| **Batch** | 1. ML training job | 2. ETL pipeline |
| **Interactive** | 3. Web API | 4. LLM inference |

| # | Workload | Pattern | $`P_m`$ dominant terms | $`R`$ | oSCI | Key notes |
|---|----------|---------|------------------------|-------|------|-----------|
| 1 | ML training (batch, per job) | GPU run, hours/days, ~100% GPU util | GPU TDP + CPU | 1 (the job) | $`E \cdot I^\star`$ | Simplest case. $`R=1`$ ⇒ oSCI = total carbon; only comparable across identical jobs. |
| 2 | ETL pipeline (batch, per metric) | Nightly transform, CPU + heavy IO | CPU only (IO unobservable) | GB processed | $`E \cdot I^\star / R`$ | CPU-only $`E`$ understates real energy; IO falls into the residual. Good "minimal info" test case. |
| 3 | Web API (interactive, per request) | VM fleet, 40-70% util, auto-scaling | CPU | requests in $`t`$ | $`E \cdot I^\star / R`$ | Straightforward. Idle fleet capacity attributed to the windows where it occurs. |
| 4 | LLM inference (interactive, per metric) | GPU serving, 10-90% util, warm fleet | GPU + CPU | tokens in $`t`$ | $`E \cdot I^\star / R`$ | Idle GPU is the key tension — consuming energy but not producing tokens → high oSCI in low-util windows. |

All four cases use the same formula: $`\text{oSCI} = E \cdot I^\star / R`$. What differs is the evaluation period $`t`$ (time window vs job span), which $`P_m`$ terms are observable (GPU, CPU, IO), and the choice of $`R`$. Monthly totals aggregate as $`O_\text{total} = \sum_t O`$. Unobservable resource energy (IO, memory) increases the residual.

## Open

- How to handle IO energy: proxy model per service type, or accept it in the residual?
- Idle capacity attribution: should warm-fleet idle energy be split out in the action metric, or left in the residual?
- How granular should TDP estimates be? Per instance family? Per chip generation?
- What is the minimum viable $`E`$ model — just CPU/GPU utilization × time × a rough TDP estimate?
