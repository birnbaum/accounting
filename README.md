# Reconcilable User-facing Cloud Carbon Accounting

You are a researcher.

## Mission

Provide **actionable carbon signals** to cloud users that are **reconcilable** with their GHG Protocol-compliant reported carbon footprint.

The core problem is that the metrics that make carbon data auditable and comparable across organizations (top-down, billing-based, standardized) are not the same metrics that help individual teams reduce emissions (bottom-up, granular, real-time, scoped to a team's agency). These two purposes involve genuine trade-offs — breadth vs. specificity, auditability vs. actionability, comparability vs. signal clarity.

Our position is that these two signals can maybe by design not be identical, but they must be **reconcilable**. When a user optimizes based on our bottom-up signal, that improvement should be traceable through to the number that appears in their GHG Protocol report. If the two signals diverge without explanation, users lose trust in both.

We focus on **location-based accounting** (GHG Protocol Scope 2 Guidance). Market-based accounting (RECs, PPAs) is inherently decoupled from physical consumption and therefore not actionable in the sense we care about. A team's carbon number can change without their behavior changing.

## Context: The Two Approaches

**Top-down (reporting):** The cloud provider computes its total monthly footprint from utility bills, diesel consumption, refrigerant losses, and amortized embodied carbon of hardware and buildings. It then allocates this total down to individual customers, services, and jobs. This data is auditable (backed by invoices), comparable (standardized methodology), and delayed (available weeks after month-end). It tells you the size of the problem but not what to do about it.

**Bottom-up (action):** We measure the energy consumption of each workload as close to the hardware as possible, estimate emissions using grid emission factors, and report it in near-real-time. This gives teams a clear signal for optimization. But it captures only direct compute energy. It misses facility overhead, embodied carbon, shared infrastructure, and other components that the top-down number includes.

The gap between these two is the **overhead delta**: the difference between the sum of all bottom-up signals and the provider's top-down reported total. Making this delta transparent, predictable, and shrinking over time is the core technical challenge.

## Design: Multi-Layer Architecture

### Layer 1 — Physical Energy Measurement

The ground truth. Energy consumption at the job/service level, measured as close to the hardware as possible. Methods include CPU/GPU power modeling (utilization × TDP-based models), hardware counters (RAPL, NVML), or direct power metering where available. This layer is provider-agnostic — the physics of energy measurement doesn't change across clouds.

**Output:** Energy per job/service in kWh, at sub-hourly granularity.

### Layer 2 — Real-Time Carbon Estimation

Multiply the energy signal by the grid's carbon intensity at the location and time of computation. The carbon intensity source and temporal resolution **must** match the provider's accounting methodology.

If the provider uses monthly average grid emission factors (AWS, Azure), our carbon estimates must use the same monthly averages. If the provider uses hourly factors (GCP), we can use hourly factors. Rewarding temporal shifting (run jobs at low-carbon hours) is only valid if the provider's accounting resolution is fine enough to capture the difference.

**Output:** Carbon per job/service in gCO₂e, at the provider's accounting resolution.

### Layer 3 — The Reconciliation Bridge

This is where the novel design work lives. The bridge connects the bottom-up per-job signals to the top-down GHG Protocol total by modeling the overhead delta. See the section on the **Theoretical Estimation Framework** below for details.

**Output:** Estimated total carbon footprint (bottom-up + modeled overhead), with confidence intervals, reconciled monthly against provider actuals.

### Layer 4 — User-Facing Actionable Signal

Users see an SCI-style rate metric — carbon per unit of work (per request, per pipeline run, per training epoch) — scoped to their team's agency. This is what they optimize against. But they can also "roll up" into their GHG Protocol reporting view, which shows absolute totals plus their allocated share of the overhead delta, with full methodology transparency.

**Output:** Per-team dashboards showing both the action metric (optimize this) and the reporting metric (report this), with a clear bridge between them.

## Why the Framework Must Be Provider-Adaptive

A critical insight from our analysis: **not all optimization levers are rewarded by all providers**. Whether a user's efficiency improvement shows up in their reported carbon footprint depends entirely on how the provider does their accounting.

For example:
- **Temporal shifting** (running at low-carbon hours) is only reconcilable if the provider uses sub-monthly emission factors. Currently only GCP uses hourly factors internally; AWS and Azure use monthly averages, so temporal shifting doesn't move the reported number.
- **Compute efficiency** (using fewer CPU-hours) is directly reconcilable on providers that use physical allocation (GCP, AWS for foundational services), and approximately reconcilable on Azure (which uses usage-based allocation correlated with compute/storage/network time, though the exact derivation is undisclosed).
- **Spatial shifting** (choosing a greener region) is reconcilable across all three providers, since all use regional emission factors.

This means the framework cannot be one-size-fits-all. It must be **parametrized by a provider profile** that encodes how the provider accounts for carbon.

## The Provider Profile Schema

The framework is parametrized by a **provider profile** that encodes how each cloud provider accounts for carbon. The full schema definition, populated profiles for AWS/GCP/Azure, reconcilability analysis, and minimum viable profile requirements are in [`SCHEMA.md`](SCHEMA.md).

The key insight from populating the profiles: **not all optimization levers are equally reconcilable across providers**, but the picture is more nuanced than a simple physical-vs-economic split. GCP's physical allocation makes most energy-based optimizations directly reconcilable. AWS's hybrid approach is direct for foundational services but approximate for managed services. Azure's usage-based allocation (compute, storage, and network time) correlates with physical usage but the undisclosed derivation of the usage factor limits confidence — reconcilability is approximate rather than structural mismatch.

**Universally safe:** Spatial shifting, eliminate idle resources, right-sizing.
**Provider-dependent:** Compute efficiency, architecture choice (strongest on GCP and AWS foundational; approximate on Azure).
**Currently unavailable:** Temporal shifting (no provider exposes sub-monthly data to customers).

## Theoretical Estimation Framework: Modeling the Overhead Delta

### Goal

Estimate the provider's top-down reported footprint in real time from bottom-up measurements, before the provider's actual data arrives (typically 15-21 days after month-end). This makes the reconciliation bridge predictive rather than purely retrospective.

### Core Equation

```
C_topdown ≈ C_bottomup + Δ_overhead
```

The overhead delta decomposes into six modelable components:

### Component 1 — Facility Overhead (PUE)

Energy consumed by cooling, power distribution, lighting, and networking infrastructure. Physically correlated with workload energy.

```
C_facility = C_bottomup × (PUE(region, time) - 1)
```

PUE varies with outside temperature, load level, and cooling technology. If the provider doesn't expose time-varying PUE, model it as a seasonal curve per region, calibrated from historical reconciliation data. Higher in summer (more cooling), lower in winter. Learnable from a few months of top-down actuals.

**Update cadence:** Seasonal. **Confidence:** Medium. **Modelability:** High.

### Component 2 — Idle and Shared Capacity

Servers powered on but not running user workloads; baseline power of networking and storage systems. Not captured by per-job measurement.

```
C_idle = C_bottomup × idle_ratio(utilization_level)
```

The idle ratio is a function of overall infrastructure utilization — higher when utilization is low (more idle power per unit of useful work), lower when utilization is high. For GCP, where machine-level power is decomposed into dynamic and idle components, this can be modeled more precisely. For AWS and Azure, treat as a utilization-dependent multiplier.

**Update cadence:** Continuous (tracks utilization). **Confidence:** Medium. **Modelability:** Medium.

### Component 3 — Scope 1 (Diesel, Refrigerants)

Small during normal operations. Diesel generators are backup; refrigerant leaks are stochastic. Model as a slowly-changing baseline per region.

```
C_scope1 = rolling_average(scope1_per_unit_energy, N_months) × C_bottomup
```

**Update cadence:** Monthly. **Confidence:** High (small component). **Modelability:** High.

### Component 4 — Embodied Carbon (Scope 3 Cat. 2)

The most predictable component. Hardware amortized over the provider's assumed lifetime (4 years for GCP, 6 years for AWS/Azure), buildings over 25-50 years. Model as a fixed monthly baseline per unit of allocated resource, calibrated from the provider's methodology parameters.

```
C_embodied = Σ(resource_type × embodied_factor(type) / lifetime_years / 12)
```

Barely moves month-to-month. Only changes when provider refreshes hardware fleet or updates LCA data.

**Update cadence:** Quarterly to annual. **Confidence:** High. **Modelability:** High.

### Component 5 — Other Scope 3 (FERA, Transport, Waste)

Typically allocated proportionally to energy use. Behaves as a multiplier.

```
C_other_scope3 = C_bottomup × scope3_ratio
```

Where `scope3_ratio` is calibrated from historical top-down data.

**Update cadence:** Monthly (calibrated from actuals). **Confidence:** Medium. **Modelability:** High.

### Component 6 — Allocation Artifact (Residual)

The irreducible difference between our bottom-up allocation and the provider's allocation. For physical allocation providers (GCP), this is small (5-15%). For usage-based allocation providers (Azure), this is moderate and bounded but not precisely quantifiable without more disclosure (~15-30%).

```
ε_allocation = C_topdown_actual - C_estimated_total
```

This is the residual — it captures everything the model doesn't. Its magnitude is a direct measure of how well the framework is working.

**Update cadence:** Monthly (computed when actuals arrive). **Confidence:** Provider-dependent. **Modelability:** Medium for physical allocation (GCP), medium for usage-based (Azure), low-medium for hybrid (AWS non-foundational).

### Full Estimation Model

```
C_estimated_total =
    C_bottomup_energy                                    # measured directly
  × emission_factor(region, time, provider_resolution)   # carbonized per provider method
  × PUE(region, season)                                  # facility overhead
  + C_idle_allocation(utilization_proxy)                  # idle capacity share
  + C_scope1_baseline(region)                            # diesel + refrigerants
  + C_embodied_baseline(resource_type, region)           # amortized hardware + buildings
  + C_other_scope3_ratio × C_bottomup_energy             # FERA, transport, waste
  + ε_allocation                                         # allocation residual (learned)
```

### Calibration Loop

Each month, when the provider's top-down actual arrives:

1. Compute `ε_observed = C_topdown_actual - C_estimated_total`
2. Decompose the residual: Is it seasonal (PUE model needs work)? Correlated with utilization (idle model needs work)? Random (allocation noise)?
3. Update model parameters accordingly.
4. Track the residual over time. A shrinking residual means the model is converging. A growing or volatile residual suggests a methodology change or a structural mismatch.

### Confidence Intervals

Present estimates to users as ranges rather than point estimates:

```
"Estimated footprint: X tCO₂e ± Y%"
```

The width of Y is determined by the provider profile. For GCP with physical allocation and hourly data, Y might be ±10-15%. For Azure with usage-based allocation, Y might be ±15-30%. This makes the provider's methodology quality visible to the user — which itself creates market pressure for better accounting.

## Open Design Questions

See also [`SCHEMA.md`](SCHEMA.md) for schema-specific open questions (e.g., handling usage-based allocation with undisclosed parameters, GCP's hourly-internal gap).

1. **Provider profile versioning.** Methodologies change (e.g., AWS's October 2025 Model 3.0 update). The profile needs a versioning mechanism and the framework should detect when reconciliation assumptions may need updating.

2. **Should the framework position itself as "we adapt to any methodology" or "we require X, Y, Z as minimum conditions"?** The minimum viable profile analysis (see SCHEMA.md) suggests the answer may emerge naturally: if a provider can't fill the required fields, the framework can still provide signals but cannot claim reconcilability.

3. **How to calibrate the overhead delta for usage-based providers?** Azure's usage-factor allocation is correlated with physical usage, so the calibration loop should converge — but slower and with wider confidence intervals than for physical allocation providers. What's the minimum number of months of top-down actuals needed before the model is usable?

## Repository Structure

```
├── README.md                              # this file
├── HYPERSCALER_CARBON_ACCOUNTING.md       # detailed provider methodology comparison
├── SCHEMA.md                              # provider profile schema, populated profiles, reconcilability analysis
├── references/SCI.md                      # Software Carbon Intensity standard
├── references/SCI_AI.md                   # SCI for AI standard
```
