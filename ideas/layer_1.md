# Layer 1: Service-Specific Energy Methodology

Define how to derive $`E`$ (energy per evaluation period) and $`R`$ (functional unit per evaluation period) for each service type. The evaluation period $`t`$ is a fixed time window for interactive workloads or the job's duration for batch workloads (see README Notation). The energy model must mirror what the provider's methodology actually rewards — the provider profile (layer 2) selects/constrains which power model layer 1 uses.

We define:
- **Usage** — how many resources for how long (vCPU-hours, instance-hours, GPU-hours). This is what providers allocate by.
- **Utilization** — how hard you work the resource (CPU at 5% vs 95%). No provider reflects this in the customer-reported number.

The action metric (oSCI) captures both. The provider-reported number captures only usage. Utilization improvements are real (they reduce physical energy) but invisible to provider accounting (they fall into the residual).


## Power Model

For any evaluation period $`t`$, the aggregate energy across all machines $`m`$:

$$E = \sum_m P_m \cdot \Delta t, \quad \text{where } P_m = \sum_r \text{count}_{m,r} \times P_r$$

Here $`m`$ indexes individual machines/instances, $`r`$ indexes resource types (vCPU, GPU, disk, network, ...), and $`P_r`$ is the rated power per unit of resource $`r`$ (e.g., TDP, a measured average, or a provider-published figure). The monthly total is $`E_\text{total} = \sum_t E`$.

This is a usage-based power model: $`P_m`$ depends on what you have provisioned (count × rated power), not on how hard you use it. It matches what all three providers allocate by at the customer level.

A more physical model would be $`P_m = \text{count} \times \text{util} \times P_r`$, but since no provider rewards utilization at the customer boundary, the utilization term does not help reconciliation.

In practice, not all resource types are observable. 
Unobservable components (e.g., IO energy) increase the residual. 
The more components we can specify/derive, the smaller and more certain the residual becomes.


## Example Workloads

The structural distinction is **batch vs interactive** — it determines the evaluation period $`t`$. The choice of $`R`$ (functional unit) is independent and up to the user.

| Type | $`t`$ | Examples | Typical $`R`$ choices |
|---|---|---|---|
| **Batch** | Job duration (start to finish) | ML training, ETL pipeline, CI build | 1 (the job), GB processed, images generated |
| **Interactive** | Fixed window (e.g., 5 min) | Web API, LLM inference, database serving | requests, tokens, queries |

Both use the same formula: $`\text{oSCI} = E \cdot I^\star / R`$. What differs is how $`t`$ is defined and which $`P_m`$ terms are observable (GPU, CPU, IO). Unobservable components (e.g., IO energy) increase the residual.

Key tension for interactive workloads: idle capacity (warm fleet consuming energy but not producing $`R`$) drives up oSCI in low-utilization windows. Whether to split this out or leave it in the residual is an open question.

## Open

- How to handle IO energy: proxy model per service type, or accept it in the residual?
- Idle capacity attribution: should warm-fleet idle energy be split out in the action metric, or left in the residual?
- How granular should $`P_r`$ estimates be? Per instance family? Per chip generation? Source: TDP, measured average, or provider-published?
- Should oSCI include utilization (as a finer-grained optimization signal) even though it doesn't reconcile? Or keep the action metric usage-based to match what providers reward, and treat utilization as a separate diagnostic?
