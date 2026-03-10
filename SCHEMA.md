# Cloud Provider Carbon Accounting Profile Schema

## Purpose

This schema defines the parameters needed to configure a bottom-up carbon measurement framework so that its actionable signals are **reconcilable** with a provider's top-down reported carbon footprint (GHG Protocol, location-based).

### How We Derived It

We compiled a detailed comparison of the carbon accounting methodologies of the three major hyperscalers (AWS, GCP, Azure) covering their customer-facing tools (CCFT, Cloud Carbon Footprint, EID), allocation methods, Scope 1/2/3 coverage, emission factor sources, temporal granularity, embodied carbon treatment, verification status, and reporting practices. The full comparison is in `HYPERSCALER_CARBON_ACCOUNTING.md`.

From this analysis, we identified the **variables that determine which bottom-up optimizations are reconcilable** with the top-down report. These variables were organized into the schema below with three design principles:

1. **Each parameter carries a reconcilability flag** — `direct` (bottom-up feeds same calculation), `approximate` (correlated but not identical), or `structural_mismatch` (provider's method is decoupled from physical measurement).
2. **The schema derives actionable levers per provider** — given a filled profile, you can determine which optimizations will actually move the user's reported number.
3. **The schema identifies minimum required disclosures** — parameters the provider must disclose (or we must determine) for the framework to function at all.

Each parameter carries:
- **Value**: What the provider uses
- **Reconcilability**: How well a bottom-up signal can align with this parameter
  - `direct` — bottom-up measurement feeds the same calculation path
  - `approximate` — different method but correlated; bounded reconciliation gap
  - `structural_mismatch` — provider's method is decoupled from physical measurement; reconciliation gap is inherent and potentially large
- **Actionable levers enabled**: Which user optimizations this parameter makes visible (or invisible) in the reported number
- **Source**: Where this information comes from (public docs, inferred, undisclosed)

---

## Schema Definition

### 1. Provider Metadata

| Field | Type | Description |
|-------|------|-------------|
| `provider_name` | string | Cloud provider name |
| `tool_name` | string | Customer-facing carbon reporting tool |
| `methodology_version` | string | Version/date of methodology document |
| `reporting_delay_days` | integer | Days after month-end before data is available |
| `customer_temporal_granularity` | enum: `hourly`, `daily`, `monthly` | Finest granularity exposed to customers |
| `internal_temporal_granularity` | enum: `hourly`, `daily`, `monthly` | Finest granularity used internally (if known) |
| `historical_recast_policy` | enum: `full`, `limited_window`, `none` | Whether methodology changes are applied retroactively |
| `recast_window_months` | integer \| null | If limited_window, how far back |
| `data_retention_months` | integer \| null | How long historical data is retained |
| `api_access` | boolean | Whether programmatic data export is available |

### 2. Energy-to-Carbon Conversion (Scope 2 Location-Based)

These parameters determine whether **temporal shifting** and **spatial shifting** are rewarded.

| Field | Type | Description |
|-------|------|-------------|
| `emission_factor_temporal_resolution` | enum: `sub_hourly`, `hourly`, `monthly`, `annual` | Resolution of grid emission factors used in accounting |
| `emission_factor_source` | string | e.g. "Electricity Maps", "IEA", "regional grid operators" |
| `emission_factor_source_fallback` | string \| null | Fallback for uncovered regions |
| `grid_region_mapping` | enum: `provider_region`, `grid_balancing_area`, `country` | How provider regions map to grid regions |

**Derived: Actionable levers**

| Lever | Requires |
|-------|----------|
| Temporal shifting (run at low-carbon hours) | `emission_factor_temporal_resolution` ≤ `hourly` |
| Spatial shifting (run in greener regions) | Any resolution, but accuracy improves with `grid_balancing_area` mapping |

### 3. Energy Allocation to Customers

These parameters determine whether **compute efficiency** optimizations reconcile with the reported number.

| Field | Type | Description |
|-------|------|-------------|
| `primary_allocation_method` | enum: `physical`, `economic`, `hybrid`, `usage_based` | How datacenter-level energy is attributed to customers |
| `physical_allocation_basis` | string \| null | e.g. "CPU utilization, memory, storage I/O, network" |
| `economic_allocation_basis` | string \| null | e.g. "normalized cost metrics", "revenue share" |
| `hybrid_allocation_split` | object \| null | Which services use which method (if hybrid) |
| `hybrid_split_disclosed` | boolean | Whether the split is publicly documented |
| `allocation_granularity` | enum: `sku`, `service`, `service_category` | Finest unit of allocation |
| `idle_capacity_treatment` | enum: `allocated_proportionally`, `excluded`, `undisclosed` | How idle/unused capacity is handled |
| `allocation_uncertainty_pct` | range \| null | Estimated uncertainty range of allocation |

**Reconcilability rules:**

| `primary_allocation_method` | Reconcilability | Implication |
|-----------------------------|----------------|-------------|
| `physical` | `direct` | Bottom-up energy ≈ allocated energy. Compute efficiency gains reconcile. |
| `hybrid` | `approximate` | Reconcilable for physically-allocated services; gap for economically-allocated ones. |
| `usage_based` | `approximate` | Usage factors (compute, storage, network time) are correlated with but not identical to energy. Reconciliation gap exists but is bounded. Better than economic, less certain than physical. |
| `economic` | `structural_mismatch` | Bottom-up energy has no guaranteed relationship to allocated carbon. Reducing kWh may not reduce reported tCO₂e if cost doesn't change proportionally. |

### 4. Overhead and Shared Infrastructure

| Field | Type | Description |
|-------|------|-------------|
| `pue_type` | enum: `time_varying`, `annual_average`, `undisclosed` | How Power Usage Effectiveness is applied |
| `pue_granularity` | enum: `per_datacenter`, `per_region`, `global`, `undisclosed` | Spatial granularity of PUE |
| `scope1_allocation_method` | enum: `physical`, `economic`, `usage_based`, `undisclosed` | How diesel, refrigerants etc. are allocated to customers |
| `cooling_allocation_method` | enum: `included_in_pue`, `separate`, `undisclosed` | How cooling overhead is handled |
| `networking_overhead_included` | boolean \| null | Whether network infrastructure energy is included |

### 5. Embodied Carbon (Scope 3 Category 2)

These are slow-moving parameters — outside the user's optimization loop but required for reconciliation.

| Field | Type | Description |
|-------|------|-------------|
| `it_hardware_included` | boolean | Servers, networking, storage |
| `it_hardware_lca_boundary` | enum: `cradle_to_gate`, `cradle_to_grave` | LCA scope for hardware |
| `it_hardware_lifetime_years` | integer | Amortization period |
| `it_hardware_lifetime_treatment` | enum: `amortize_then_stop`, `amortize_then_zero`, `undisclosed` | What happens after amortization period |
| `building_embodied_included` | boolean | Data center buildings |
| `building_lifetime_years` | integer \| null | Amortization period for buildings |
| `non_it_infrastructure_included` | boolean | UPS, cooling equipment, etc. |
| `end_of_life_included` | boolean | Recycling, disposal, refurbishment |
| `embodied_carbon_allocation_method` | enum: `physical`, `proportional_to_energy`, `economic`, `usage_based` | How embodied carbon is allocated to customers |
| `lca_data_source` | string | e.g. "Supplier EPDs", "Component-level LCA", "AI-augmented" |
| `embodied_uncertainty_pct` | range \| null | Estimated uncertainty |

### 6. Other Scope 3 Categories

| Field | Type | Description |
|-------|------|-------------|
| `fera_included` | boolean | Category 3: Fuel & Energy-Related Activities |
| `upstream_transport_included` | boolean | Category 4 |
| `waste_included` | boolean | Category 5 |
| `business_travel_included` | boolean | Category 6 |
| `employee_commuting_included` | boolean | Category 7 |
| `other_scope3_allocation_method` | enum: `physical`, `proportional_to_energy`, `economic`, `usage_based` | How these are allocated to customers |

### 7. Verification and Trust

| Field | Type | Description |
|-------|------|-------------|
| `third_party_assurance` | boolean | Formal GHG assurance engagement |
| `assurance_scope` | string \| null | What categories/scopes are covered |
| `tool_implementation_audited` | boolean | Whether the customer tool (not just methodology) is verified |
| `methodology_publicly_available` | boolean | Full methodology documentation published |

---

## Provider Profiles

### AWS

```yaml
provider_name: "Amazon Web Services"
tool_name: "Customer Carbon Footprint Tool (CCFT)"
methodology_version: "Model 3.0, October 2025"
reporting_delay_days: 21
customer_temporal_granularity: monthly
internal_temporal_granularity: monthly  # assumed; not disclosed as hourly
historical_recast_policy: full
recast_window_months: null  # full recast to Jan 2020
data_retention_months: 38
api_access: false

# Scope 2 — Energy to Carbon
emission_factor_temporal_resolution: monthly
emission_factor_source: "Regional grid operators"
emission_factor_source_fallback: "IEA annual"
grid_region_mapping: provider_region

# Energy Allocation
primary_allocation_method: hybrid
physical_allocation_basis: "CPU utilization, memory, storage I/O, network throughput"
economic_allocation_basis: "Revenue share (non-foundational services)"
hybrid_allocation_split:
  physical: "Foundational services (EC2, S3, RDS, etc.)"
  economic: "Non-foundational services (Lambda, SageMaker, Athena, Redshift, managed services)"
hybrid_split_disclosed: false  # list of non-foundational services not public
allocation_granularity: service
idle_capacity_treatment: undisclosed
allocation_uncertainty_pct: "5-10% (physical), 20-40% (economic)"

# Overhead
pue_type: undisclosed
pue_granularity: undisclosed
scope1_allocation_method: physical
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_gate
it_hardware_lifetime_years: 6
it_hardware_lifetime_treatment: amortize_then_stop
building_embodied_included: true  # added Oct 2024
building_lifetime_years: 50
non_it_infrastructure_included: true
end_of_life_included: false
embodied_carbon_allocation_method: physical  # for foundational; economic for non-foundational
lca_data_source: "Supplier EPDs; AI/LLM estimation fallback"
embodied_uncertainty_pct: "10-15% (EPD-backed), 20-50% (AI/LLM fallback)"

# Other Scope 3
fera_included: true
upstream_transport_included: true
waste_included: true
business_travel_included: false
employee_commuting_included: false
other_scope3_allocation_method: physical  # same hybrid as above

# Verification
third_party_assurance: true
assurance_scope: "Scope 3 Cat. 2 (IT hardware), Cat. 3, Cat. 4 only"
tool_implementation_audited: false
methodology_publicly_available: true  # partial
```

**AWS — Reconcilability Summary:**

| Lever | Reconcilable? | Notes |
|-------|--------------|-------|
| Compute efficiency (reduce kWh) | ✅ Direct (foundational) / ⚠️ Approximate (non-foundational) | Physical allocation tracks kWh for EC2 etc. Economic fallback breaks this for managed services. |
| Temporal shifting | ❌ Not rewarded | Monthly emission factors average out intra-day variation. |
| Spatial shifting (region choice) | ✅ Direct | Monthly regional emission factors differ across regions. |
| Right-sizing / eliminate waste | ✅ Direct (foundational) | Fewer resources → less allocated energy → less carbon. |
| Architecture choice (e.g. Graviton) | ⚠️ Approximate | Reflected in physical allocation; unclear for managed services. |

---

### Google Cloud Platform

```yaml
provider_name: "Google Cloud Platform"
tool_name: "Google Cloud Carbon Footprint"
methodology_version: "2024 (Electricity Maps integration)"
reporting_delay_days: 15
customer_temporal_granularity: monthly
internal_temporal_granularity: hourly
historical_recast_policy: full
recast_window_months: null  # unlimited via BigQuery
data_retention_months: null  # unlimited
api_access: true  # BigQuery export

# Scope 2 — Energy to Carbon
emission_factor_temporal_resolution: hourly  # internal; monthly exposed
emission_factor_source: "Electricity Maps API"
emission_factor_source_fallback: "IEA annual"
grid_region_mapping: provider_region  # hourly CFE per region

# Energy Allocation
primary_allocation_method: physical
physical_allocation_basis: "Machine-level power telemetry (dynamic + idle decomposition)"
economic_allocation_basis: null
hybrid_allocation_split: null
hybrid_split_disclosed: true  # full methodology published
allocation_granularity: sku
idle_capacity_treatment: allocated_proportionally
allocation_uncertainty_pct: "5-15%"

# Overhead
pue_type: undisclosed  # likely time-varying given hourly data, but not confirmed
pue_granularity: undisclosed
scope1_allocation_method: physical
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_gate
it_hardware_lifetime_years: 4  # GCP uses financial accounting standard; actual lifetimes are longer
it_hardware_lifetime_treatment: amortize_then_stop
building_embodied_included: true  # included in customer-facing tool per methodology docs
building_lifetime_years: null  # included but amortization period not publicly specified
non_it_infrastructure_included: true  # partial
end_of_life_included: false
embodied_carbon_allocation_method: proportional_to_energy
lca_data_source: "Component-level LCA, Fraunhofer IZM reviewed"
embodied_uncertainty_pct: "10-15% (IT hardware), 20-35% (non-electricity Scope 3)"

# Other Scope 3
fera_included: true
upstream_transport_included: true  # partial
waste_included: false
business_travel_included: true
employee_commuting_included: true
other_scope3_allocation_method: proportional_to_energy

# Verification
third_party_assurance: false  # academic review only
assurance_scope: "LCA methodology only (Fraunhofer IZM, ISO 14040/14044)"
tool_implementation_audited: false
methodology_publicly_available: true
```

**GCP — Reconcilability Summary:**

| Lever | Reconcilable? | Notes |
|-------|--------------|-------|
| Compute efficiency (reduce kWh) | ✅ Direct | Machine-level power telemetry; SKU-level allocation. Best-in-class. |
| Temporal shifting | ⚠️ Internally yes, customer-facing no | GCP uses hourly internally but exposes monthly. If GCP exposes hourly data or confirms hourly accounting in reported figures, this becomes directly reconcilable. Currently the monthly aggregation washes it out for reporting purposes. |
| Spatial shifting (region choice) | ✅ Direct | Hourly CFE per region; clear regional differences. |
| Right-sizing / eliminate waste | ✅ Direct | Physical allocation at SKU level tracks resource consumption tightly. |
| Architecture choice (GPU vs CPU) | ✅ Direct | SKU-level granularity captures hardware differences. |
| Embodied carbon (hardware choice) | ⚠️ Approximate | Proportional-to-energy allocation is a proxy; GPU-heavy workloads may be under/over-attributed. |

---

### Microsoft Azure

```yaml
provider_name: "Microsoft Azure"
tool_name: "Emissions Impact Dashboard (EID)"
methodology_version: "CHEM Whitepaper 2026"
reporting_delay_days: 15
customer_temporal_granularity: monthly
internal_temporal_granularity: monthly  # assumed
historical_recast_policy: limited_window
recast_window_months: 12
data_retention_months: 12
api_access: true  # Fabric / Power BI

# Scope 2 — Energy to Carbon
emission_factor_temporal_resolution: monthly
emission_factor_source: "Regional grid operators"
emission_factor_source_fallback: "IEA annual"
grid_region_mapping: provider_region

# Energy Allocation
primary_allocation_method: usage_based
physical_allocation_basis: "Compute, storage, and data transfer usage time per datacenter region"
economic_allocation_basis: null  # source doc describes usage-based, not cost-based
hybrid_allocation_split: null
hybrid_split_disclosed: true  # partial — method disclosed, usage factor derivation not
allocation_granularity: service_category
idle_capacity_treatment: undisclosed
allocation_uncertainty_pct: "15-30%"

# Overhead
pue_type: undisclosed
pue_granularity: undisclosed
scope1_allocation_method: usage_based  # "usage time in compute, storage, or network categories"
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_grave
it_hardware_lifetime_years: 6
it_hardware_lifetime_treatment: amortize_then_zero  # ERROR: drops to zero after 6 years
building_embodied_included: false
building_lifetime_years: null
non_it_infrastructure_included: false
end_of_life_included: true
embodied_carbon_allocation_method: usage_based  # consistent with overall usage-factor approach
lca_data_source: "Component-level LCA via CHEM; AI-augmented for scale"
embodied_uncertainty_pct: "10-20% (LCA-backed), 15-30% (AI-augmented)"

# Other Scope 3
fera_included: true
upstream_transport_included: true  # partial; Azure source explicitly lists Cat. 4 in scope (hardware transport in LCA)
waste_included: false  # Azure lists Cat. 5 in scope but refers to hardware end-of-life, not operational waste
business_travel_included: false
employee_commuting_included: false
other_scope3_allocation_method: usage_based

# Verification
third_party_assurance: true
assurance_scope: "Scope 3 methodology document only (WSP USA)"
tool_implementation_audited: false
methodology_publicly_available: true  # partial
```

**Azure — Reconcilability Summary:**

| Lever | Reconcilable? | Notes |
|-------|--------------|-------|
| Compute efficiency (reduce kWh) | ⚠️ Approximate | Usage-based allocation (compute, storage, network time) correlates with energy but the exact relationship is undisclosed. Reducing usage time should reduce allocated carbon, but the mapping is not transparent enough to confirm 1:1. |
| Temporal shifting | ❌ Not rewarded | Monthly emission factors. |
| Spatial shifting (region choice) | ⚠️ Approximate | Regional emission factors differ; usage-factor approach preserves regional signal. |
| Right-sizing / eliminate waste | ⚠️ Approximate | Reducing usage (compute/storage/network) should reduce the usage factor and thus allocated carbon. |
| Architecture choice | ⚠️ Approximate | More efficient hardware using less compute time → lower usage factor, but the granularity of the usage factor (service category, not SKU) may not capture all efficiency gains. |
| Reduce usage time | ✅ Direct | Azure's usage factor is based on compute, storage, and data transfer time — directly reducing these reduces allocated carbon. |

---

## Cross-Provider Analysis: What Can We Actually Reward?

| Optimization Lever | AWS (foundational) | AWS (non-foundational) | GCP | Azure |
|--------------------|-------------------|----------------------|-----|-------|
| **Compute efficiency** | ✅ direct | ⚠️ approximate | ✅ direct | ⚠️ approximate |
| **Temporal shifting** | ❌ | ❌ | ⚠️ internal only | ❌ |
| **Spatial shifting** | ✅ direct | ⚠️ approximate | ✅ direct | ⚠️ approximate |
| **Right-sizing** | ✅ direct | ⚠️ approximate | ✅ direct | ⚠️ approximate |
| **Architecture choice** | ✅ direct | ❌ mismatch | ✅ direct | ⚠️ approximate |
| **Eliminate idle resources** | ✅ direct | ⚠️ approximate | ✅ direct | ⚠️ approximate |

### Universally safe to reward (reconcilable across all three):
- **Spatial shifting** (all three use regional emission factors)
- **Eliminate idle resources** (reduces energy, usage time, and cost across all allocation methods)
- **Right-sizing** (reduces resource usage, which is tracked by all three providers)

### Conditionally reconcilable:
- **Compute efficiency** — direct on GCP and AWS foundational services; approximate on Azure (usage-based allocation correlates with but is not identical to energy)
- **Architecture choice** — direct on GCP (SKU-level) and AWS foundational (physical allocation); approximate on Azure (service-category granularity may not capture hardware-level differences)
- **Temporal shifting** — only if provider uses sub-monthly emission factors (currently: GCP internally, none customer-facing)

### Key uncertainty:
- Azure's usage-factor approach is better than pure cost-based allocation but the undisclosed derivation of the usage factor limits confidence. The reconciliation gap is bounded (correlated with physical usage) but not precisely quantifiable without more disclosure from Microsoft.

---

## Minimum Viable Profile: What Must a Provider Disclose?

Based on this analysis, these are the **minimum parameters** a provider must disclose (or we must be able to determine) for the framework to generate reconcilable actionable signals:

### Required (framework cannot function without):
1. `primary_allocation_method` — physical vs usage-based vs economic determines whether and how well energy-based signals reconcile
2. `emission_factor_temporal_resolution` — determines which time-based optimizations are valid
3. `allocation_granularity` — determines at what level we can provide signals
4. `customer_temporal_granularity` — determines feedback loop speed

### Required for reconciliation (framework works but reconciliation gap is unbounded without):
5. `it_hardware_lifetime_years` — needed to model embodied carbon baseline
6. `embodied_carbon_allocation_method` — needed to reconcile Scope 3
7. `scope1_allocation_method` — needed for complete picture
8. `pue_type` and `pue_granularity` — needed to bridge raw energy to facility energy

### Desirable (improves accuracy but framework degrades gracefully without):
9. `hybrid_allocation_split` — which services are physically vs economically allocated
10. `idle_capacity_treatment` — affects accuracy of per-job attribution
11. `lca_data_source` — affects embodied carbon confidence bounds
12. `emission_factor_source` — affects Scope 2 accuracy

---

## Open Questions

1. **How should the framework handle usage-based allocation with undisclosed parameters?** Azure's usage-factor approach correlates with physical usage but the exact derivation is undisclosed. Options: (a) treat as `approximate` and provide reconcilable signals with wider confidence intervals, (b) require Microsoft to disclose usage factor derivation before claiming reconcilability, (c) empirically determine the correlation by comparing bottom-up estimates with top-down actuals over multiple months.

2. **How to handle GCP's hourly-internal / monthly-external gap?** GCP computes hourly but reports monthly. If a user shifts load to low-carbon hours, the internal accounting captures it but the customer-facing report doesn't show it at that granularity. Do we reward it (because it's real) or not (because the customer can't verify it in their report)?

3. **How to model the overhead delta?** The gap between sum-of-bottom-up-signals and top-down-total includes shared infrastructure, embodied carbon, and allocation artifacts. Should the profile include an expected overhead ratio, or should this be discovered empirically?

4. **Provider profile versioning.** Methodologies change (e.g., AWS's Oct 2024 expansion). The profile needs a versioning mechanism, and ideally the framework should detect when a provider's methodology changes and flag that reconciliation assumptions may need updating.