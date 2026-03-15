# Layer 1: Service-Specific Energy Methodology

## Goal

Define how to derive $`E`$ (energy per evaluation period) and $`R`$ (functional unit per evaluation period) for each service type. The evaluation period $`t`$ is a fixed time window for interactive workloads or the job's duration for batch workloads (see README Notation). The energy model must mirror what the provider's methodology actually rewards — the provider profile (layer 2) selects/constrains which power model layer 1 uses.

## Usage vs Utilization

Two concepts that all three providers conflate or ignore at the customer level:

- **Usage** — resource-time: how many resources for how long (vCPU-hours, instance-hours, GPU-hours). This is what providers allocate by.
- **Utilization** — resource-load: how hard you work the resource (CPU at 5% vs 95%). No provider reflects this in the customer-reported number.

The action metric (oSCI) captures both. The provider-reported number captures only usage. Utilization improvements are real (they reduce physical energy) but invisible to provider accounting — they fall into the residual.

## Power Model

For any evaluation period $`t`$, the aggregate energy across all machines $`m`$:

$$E = \sum_m P_m \cdot \Delta t, \quad \text{where } P_m = \sum_r \text{count}_{m,r} \times \text{TDP}_r$$

Here $`m`$ indexes individual machines/instances and $`r`$ indexes resource types (vCPU, GPU, disk, network, ...). The monthly total is $`E_\text{total} = \sum_t E`$.

This is a usage-based power model: $`P_m`$ depends on what you have provisioned (count × TDP), not on how hard you use it. It matches what all three providers allocate by at the customer level.

A more physical model would be $`P_m = \text{count} \times \text{util} \times \text{TDP}`$, but since no provider rewards utilization at the customer boundary, the utilization term does not help reconciliation — it would only widen the gap between the action metric and the provider-reported number. We therefore keep the power model usage-based and let utilization improvements flow through oSCI as an optimization signal that the residual absorbs.

In practice, not all resource types are observable. Unobservable components (e.g., IO energy) increase the residual. The more components we can specify/derive, the smaller and more certain the residual becomes — but the framework should work with minimal information.

## Why Not a Utilization-Based Power Model?

GCP internally measures actual machine power and allocates dynamic power proportional to GCU usage — a genuine physical/utilization-based model (Schneider & Mattia 2024, §3.3). But the customer-facing step (Eq. 10) distributes each internal team's total energy across SKUs using price-based proportionality, then allocates to customers by usage (vCPU-hours). A VM running at 5% CPU for one hour receives the same carbon allocation as one at 95% — same SKU, same usage. The physical signal is preserved at the aggregate level (the Compute Engine team's total reflects real energy) but is washed out at the individual customer level.

AWS and Azure are similarly usage-based at the customer boundary (instance-hours and usage time respectively). No provider exposes a utilization-based allocation to customers.

Since the framework's goal is reconciliation to provider-reported numbers, the power model must match what providers actually reward: usage.

## Optimization Levers and Reconcilability

See [SCHEMA.md — Cross-Provider Analysis](../SCHEMA.md#cross-provider-analysis-what-can-we-actually-reward) for the full lever table and provider-specific reconcilability analysis.

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
- Should oSCI include utilization (as a finer-grained optimization signal) even though it doesn't reconcile? Or keep the action metric usage-based to match what providers reward, and treat utilization as a separate diagnostic?
