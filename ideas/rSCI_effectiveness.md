# rSCI Effectiveness Analysis

How does rSCI hold up against the critique axes in Bashir et al. (2024)?

## Background

Bashir et al. evaluate SCI variants for carbon-aware scheduling and identify failure modes: the sunk carbon fallacy (SCI), impracticality (tSCI), and incomplete scope (oSCI). They recommend oSCI for scheduling. Our rSCI builds on oSCI and adds a reconciliation layer. This analysis evaluates whether the reconciliation layer introduces new problems.

## rSCI Definition (current)

```
oSCI_i = O_i / R_i                              (action layer)
O_total = Σ O_i                                  (slice total)
ĉ = O_total + Δ_residual ≈ C_reported            (reconciliation)
w_i = O_i / O_total                              (allocation weight)
rSCI_i = (O_i + w_i · Δ_residual) / R_i          (reconciled metric)
       = oSCI_i · γ    where γ = 1 + Δ_residual / O_total
```

## 1. Sunk Carbon Fallacy

**Bashir et al. concern:** SCI includes embodied carbon (M) per server, creating incentives to prefer older inefficient servers with lower amortized M.

**rSCI exposure: none.** The action layer is pure oSCI — no embodied carbon term. Embodied carbon enters only through Δ_residual, which is a slice-level scalar, not a per-workload term. Since rSCI_i = oSCI_i · γ and γ is constant across workloads within a slice, the ranking between scheduling alternatives is identical to oSCI. A workload with lower oSCI always has lower rSCI.

**Verdict: resolved.**

## 2. Complexity / Data Requirements

**Bashir et al. concern:** tSCI requires "comprehensive datacenter-level information" and "sophisticated data collection infrastructure" — dismissed as impractical.

**rSCI exposure: low.** rSCI requires:
- Workload energy telemetry (E_i) — same as oSCI
- Carbon intensity data (I) — same as oSCI
- Provider-reported carbon per slice (C_reported) — available from provider dashboards/APIs, delayed by weeks
- Historical (O_total, C_reported) pairs to learn Δ_residual — minimum ~3-6 months

No datacenter inventory, no per-server embodied carbon estimates, no idle server enumeration. The only additional input beyond oSCI is C_reported, which cloud customers already receive for Scope 3 reporting.

**One learned parameter** (Δ_residual) vs. tSCI's requirement to know every server in the datacenter.

**Verdict: practical.** Strictly simpler than tSCI. Marginal complexity over oSCI, justified by the reconciliation goal.

## 3. Proportional Allocation Incentives

**Concern:** Does the w_i allocation create gaming or perverse incentives?

Since w_i = O_i / O_total and rSCI_i = oSCI_i · γ:
- Reducing O_i reduces both oSCI_i and rSCI_i proportionally
- The γ factor is the same for all workloads in the slice — no workload can game it individually
- A team that optimizes aggressively sees its rSCI drop by exactly the same ratio as its oSCI

The allocation is not zero-sum in a problematic way: if one team halves its O_i, its rSCI halves. Other teams' rSCI is unchanged (their O_i and γ are the same — γ shifts slightly because O_total changed, but this is a second-order effect shared equally).

**Verdict: no gaming concern.** The uniform scaling means w_i allocation is invisible to individual optimization decisions.

## 4. Signal vs. Accounting Identity

**Bashir et al. concern:** Scheduling and accounting should use different metrics because they serve different purposes.

**rSCI exposure: partially resolved.** Because rSCI = oSCI · γ:
- **Within a slice:** rSCI and oSCI give identical rankings. For scheduling decisions between workloads or configurations in the same slice, they are interchangeable.
- **Across slices:** γ varies by slice. A low-carbon-intensity slice may have a high γ (fixed overhead is a larger fraction of small O_total). This means rSCI could discourage moving to a cleaner region if the overhead ratio is worse there — even though oSCI would clearly favor the move.

This is not a bug — it reflects reality. The provider *will* report higher overhead ratios for low-utilization or low-intensity slices. But it means:
- **Intra-slice scheduling** (which job, which config, when): use rSCI or oSCI — same signal
- **Cross-slice decisions** (which region, which provider): oSCI gives the pure operational signal, rSCI gives the provider-reported reality. Both are useful; the choice depends on what you're optimizing for.

**Verdict: manageable tension.** The framework should be explicit that rSCI is the reconciled view of what the provider reports, not a universal optimization target. For cross-slice decisions, teams should consider both oSCI and rSCI.

## 5. Scope Compared to tSCI

**tSCI scope:** idle server operational + idle server embodied (datacenter-internal only).

**rSCI scope:** everything between O_total and C_reported — embodied carbon, idle capacity, PUE, Scope 1 (diesel, refrigerants), allocation artifacts, and any other overhead the provider includes in its methodology.

rSCI is strictly broader because it reconciles to the provider's actual reported number rather than reconstructing components bottom-up. The trade-off: you know the total gap but not its composition (without further decomposition work).

**Verdict: advantage rSCI** for practical carbon accounting. tSCI has better component visibility but requires impossible data access.

## Summary

| Critique | rSCI exposure | Severity |
|----------|--------------|----------|
| Sunk carbon fallacy | Not present — action layer is pure oSCI | Resolved |
| Complexity / data requirements | One learned parameter + C_reported | Low |
| Proportional allocation gaming | γ is uniform — no individual gaming possible | Resolved |
| Signal vs. identity conflation | Same signal within slice; γ varies across slices | Low (explicit about scope) |
| Scope vs. tSCI | Broader (all provider-reported overhead) but opaque | Trade-off |

rSCI avoids the primary failure modes identified by Bashir et al. while adding reconciliation to the provider-reported total — something none of oSCI, SCI, or tSCI provide.
