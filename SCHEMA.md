# Cloud Provider Carbon Accounting Profile Schema

## Purpose

This schema defines the parameters needed to configure a bottom-up carbon measurement framework so that its actionable signals are **reconcilable** with a provider's top-down reported carbon footprint (GHG Protocol, location-based).

### Provider Profiles Overview

Not all optimization levers reconcile equally across providers. Temporal shifting only reconciles if the provider uses sub-monthly emission factors; compute efficiency (reducing CPU utilization) is not rewarded by any provider at the customer level since all three use usage allocation (resource-time, not resource-load); spatial shifting is broadly reconcilable because all three providers use regional factors. The framework therefore needs provider-specific configuration.

A provider profile captures:

- reporting dimensions and recommended reporting slice
- allocation method and granularity
- temporal resolution of emission factors
- embodied-carbon treatment
- overhead and verification metadata

Summary by provider:

- **GCP:** strongest alignment for electricity-related signals at the aggregate level — internal allocation is physical and granular. However, the customer-facing step distributes energy across SKUs using price-based proportionality and allocates by usage units (e.g., vCPU-hours), so individual customer CPU utilization is not reflected in the reported number (Schneider & Mattia 2024, §3.6.1). Temporal shifting reconciles internally (hourly Electricity Maps) but only monthly data is exposed to customers.
- **AWS:** strong for foundational services (usage allocation tracks instance-hours), weaker where economic allocation is used for non-foundational services.
- **Azure:** directionally aligned for many actions, but confidence is limited by usage-factor opacity (2021 whitepaper reveals usage = "normalized cost metric," closer to economic allocation than physical), coarser service granularity, and methodological tension between sources. Carbon Optimization tool adds resource-level granularity with AI-driven recommendations.

When a provider improves methodology, new optimization levers become reconcilable. Making that visible is part of the point.

### How We Derived It

We compiled a detailed comparison of the carbon accounting methodologies of the three major hyperscalers (AWS, GCP, Azure) covering their customer-facing tools (CCFT, Cloud Carbon Footprint, EID), allocation methods, Scope 1/2/3 coverage, emission factor sources, temporal granularity, embodied carbon treatment, verification status, and reporting practices. The full comparison is in `HYPERSCALER_CARBON_ACCOUNTING.md`.

From this analysis, we identified the **variables that determine which bottom-up optimizations are reconcilable** with the top-down report. Note that Azure now has two customer-facing tools: the Emissions Impact Dashboard (EID, subscription × service × region, up to 5 years, Power BI) and Carbon Optimization (resource_group × resource level, 12 months, Azure portal + REST API, with AI-driven reduction recommendations). These variables were organized into the schema below with three design principles:

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
| `customer_reporting_dimensions` | array | Dimensions exposed to the customer in the reporting tool, e.g. `[account, service, region]` |
| `recommended_reconciliation_unit` | string | Finest provider-exposed slice at which bottom-up signals should be reconciled to provider reports |
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
| `primary_allocation_method` | enum: `usage`, `economic` | How datacenter-level energy is attributed to customers. `usage` = proportional to resource-time (vCPU-hours, instance-hours, usage time); `economic` = proportional to spend/revenue |
| `fallback_allocation_method` | enum: `usage`, `economic` \| null | Secondary method used where the primary method is unavailable |
| `fallback_allocation_scope` | string \| null | Which services or emission categories use the fallback method |
| `usage_allocation_unit` | string \| null | The resource-time unit used for usage allocation, e.g. "vCPU-hours per SKU", "instance-hours per service" |
| `economic_allocation_basis` | string \| null | e.g. "normalized cost metrics", "revenue share" |
| `allocation_granularity` | enum: `sku`, `service`, `service_category` | Finest unit of allocation |
| `idle_capacity_treatment` | enum: `allocated_proportionally`, `excluded`, `undisclosed` | How idle/unused capacity is handled |
| `allocation_uncertainty_pct` | range \| null | Estimated uncertainty range of allocation |

**Provider terminology mapping:**

| Our term | Provider term | Who uses it |
|----------|-------------|-------------|
| **Usage** | "Physical allocation" | GCP (Schneider & Mattia 2024), AWS (foundational) |
| **Usage** | "Usage-based allocation" | Azure |
| **Economic** | "Economic allocation" / "Revenue share" / "Back-charged costs" | GCP (internal shared services without sufficient usage data; price-based SKU distribution), AWS (non-foundational) |

All three providers measure power internally and allocate to customers by usage (resource-time). GCP and AWS call this "physical" — but the customer sees vCPU-hours or instance-hours, not watts. Azure more accurately self-describes as "usage-based." We use **usage** because it describes what determines the customer-reported number. Both GCP and AWS use economic/cost-based allocation as a fallback for some services (GCP: internal shared services without sufficient usage data; AWS: non-foundational services). Azure's fallback approach is not disclosed.

**Reconcilability rules:**

| `primary_allocation_method` | Reconcilability | Implication |
|-----------------------------|----------------|-------------|
| `usage` | `approximate` | Resource-time (vCPU-hours, instance-hours) is correlated with energy but does not capture utilization. Reducing resource-time reconciles; reducing compute utilization does not. This is the method all three providers use at the customer level. |
| `economic` | `structural_mismatch` | Bottom-up energy has no guaranteed relationship to allocated carbon. Reducing kWh may not reduce reported tCO₂e if cost doesn't change proportionally. AWS non-foundational uses this. |

### 4. Overhead and Shared Infrastructure

| Field | Type | Description |
|-------|------|-------------|
| `pue_type` | enum: `time_varying`, `annual_average`, `undisclosed` | How Power Usage Effectiveness is applied |
| `pue_granularity` | enum: `per_datacenter`, `per_region`, `global`, `undisclosed` | Spatial granularity of PUE |
| `scope1_allocation_method` | enum: `usage`, `economic`, `undisclosed` | How diesel, refrigerants etc. are allocated to customers |
| `cooling_allocation_method` | enum: `included_in_pue`, `separate`, `undisclosed` | How cooling overhead is handled |
| `networking_overhead_included` | boolean \| null | Whether network infrastructure energy is included |

### 5. Embodied Carbon (Scope 3 Category 2)

These are slow-moving parameters — outside the user's optimization loop but required for reconciliation.

| Field | Type | Description |
|-------|------|-------------|
| `it_hardware_included` | boolean | Servers, networking, storage |
| `it_hardware_lca_boundary` | enum: `cradle_to_gate`, `cradle_to_grave` | LCA scope for hardware |
| `it_hardware_lifetime_years` | integer | Amortization period |
| `it_hardware_lifetime_treatment` | enum: `amortize_then_zero`, `undisclosed` | What happens after amortization period. All three providers report zero embodied carbon for equipment past its amortization window. |
| `building_embodied_included` | boolean | Data center buildings |
| `building_lifetime_years` | integer \| null | Amortization period for buildings |
| `non_it_infrastructure_included` | boolean | UPS, cooling equipment, etc. |
| `end_of_life_included` | boolean | Recycling, disposal, refurbishment |
| `embodied_carbon_allocation_method` | enum: `usage`, `proportional_to_energy`, `economic` | How embodied carbon is allocated to customers |
| `lca_data_source` | string | e.g. "Supplier EPDs", "Component-level LCA", "AI-augmented" |
| `embodied_uncertainty_pct` | range \| null | Estimated uncertainty |

### 6. Other Scope 3 Categories

| Field | Type | Description |
|-------|------|-------------|
| `purchased_goods_services_included` | boolean | Category 1: Purchased Goods & Services (e.g., raw material extraction) |
| `fera_included` | boolean | Category 3: Fuel & Energy-Related Activities |
| `upstream_transport_included` | boolean | Category 4: Upstream Transportation & Distribution |
| `waste_included` | boolean | Category 5: Waste Generated in Operations |
| `business_travel_included` | boolean | Category 6: Business Travel |
| `employee_commuting_included` | boolean | Category 7: Employee Commuting |
| `downstream_transport_included` | boolean | Category 9: Downstream Transportation & Distribution |
| `end_of_life_treatment_included` | boolean | Category 12: End-of-Life Treatment of Sold Products |
| `other_scope3_allocation_method` | enum: `usage`, `proportional_to_energy`, `economic` | How these are allocated to customers |

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
customer_reporting_dimensions: [account, service, region]
recommended_reconciliation_unit: "account × service × region × month"
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
primary_allocation_method: usage
fallback_allocation_method: economic
fallback_allocation_scope: "Non-foundational services (Lambda, SageMaker, Athena, Redshift — full list not disclosed)"
usage_allocation_unit: "instance-hours per service"
economic_allocation_basis: "Revenue share (non-foundational services)"
allocation_granularity: service
idle_capacity_treatment: undisclosed
allocation_uncertainty_pct: "5-10% (physical), 20-40% (economic)"

# Overhead
pue_type: undisclosed
pue_granularity: undisclosed
scope1_allocation_method: usage
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_gate
it_hardware_lifetime_years: 6
it_hardware_lifetime_treatment: amortize_then_zero  # zero after 6 years; same as Azure
building_embodied_included: true  # added Oct 2024
building_lifetime_years: 50
non_it_infrastructure_included: true
end_of_life_included: false
embodied_carbon_allocation_method: usage  # for foundational; economic for non-foundational
lca_data_source: "Supplier EPDs; AI/LLM estimation fallback"
embodied_uncertainty_pct: "10-15% (EPD-backed), 20-50% (AI/LLM fallback)"

# Other Scope 3
fera_included: true
upstream_transport_included: true
waste_included: true
business_travel_included: false
employee_commuting_included: false
other_scope3_allocation_method: usage  # same as above; economic for non-foundational

# Verification
third_party_assurance: true
assurance_scope: "Scope 3 Cat. 2 (IT hardware), Cat. 3, Cat. 4 only"
tool_implementation_audited: false
methodology_publicly_available: true  # partial
```

**AWS — Reconcilability Summary:**

| Lever | Reconcilable? | Notes |
|-------|--------------|-------|
| Compute efficiency (reduce compute utilization) | ❌ Not rewarded (foundational) / ❌ Not rewarded (non-foundational) | Foundational services use usage allocation (instance-hours); compute utilization not reflected. Economic fallback for non-foundational is even more decoupled. |
| Temporal shifting | ❌ Not rewarded | Monthly emission factors average out intra-day variation. |
| Spatial shifting (region choice) | ✅ Direct | Monthly regional emission factors differ across regions. |
| Right-sizing / eliminate waste | ✅ Direct (foundational) | Fewer instance-hours → less allocated energy → less carbon. |
| Architecture choice (e.g. Graviton) | ⚠️ Approximate (foundational) | Only reconciles if the more efficient instance completes the job faster (fewer instance-hours). Same duration = same carbon regardless of instance efficiency. Unclear for non-foundational (economic allocation). |

---

### Google Cloud Platform

```yaml
provider_name: "Google Cloud Platform"
tool_name: "Google Cloud Carbon Footprint"
methodology_version: "2024 (Electricity Maps integration)"
reporting_delay_days: 15
customer_temporal_granularity: monthly
internal_temporal_granularity: hourly
customer_reporting_dimensions: [project, sku, region]
recommended_reconciliation_unit: "project × sku × region × month"
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
primary_allocation_method: usage
fallback_allocation_method: economic
fallback_allocation_scope: "Internal shared services without sufficient usage data use back-charged costs (~1/3 of shared service energy; Schneider & Mattia 2024, §3.4.2); SKU-level allocation uses price-based proportionality (usage × list price)"
usage_allocation_unit: "vCPU-hours per SKU (price-derived energy factor; Schneider & Mattia 2024, Eq. 10)"
economic_allocation_basis: "Price-based proportionality across SKUs (Schneider & Mattia 2024, Eq. 10)"
allocation_granularity: sku
idle_capacity_treatment: allocated_proportionally
allocation_uncertainty_pct: "5-15%"

# Overhead
pue_type: undisclosed  # likely time-varying given hourly data, but not confirmed
pue_granularity: undisclosed
scope1_allocation_method: usage
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_gate
it_hardware_lifetime_years: 4  # GCP uses financial accounting standard; actual lifetimes are longer
it_hardware_lifetime_treatment: amortize_then_zero  # "dropping those at the 4-year mark"
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
| Compute efficiency (reduce compute utilization) | ❌ Not rewarded | Customer-facing allocation is usage-based: vCPU-hours × price-derived energy factor (Schneider & Mattia 2024, Eq. 10). A VM at 5% utilization and one at 95% receive the same allocation for the same vCPU-hours. Internal physical measurement captures utilization at the team level but this signal is washed out at the customer boundary. |
| Temporal shifting | ⚠️ Internally yes, customer-facing no | GCP uses hourly internally but exposes monthly. If GCP exposes hourly data or confirms hourly accounting in reported figures, this becomes directly reconcilable. Currently the monthly aggregation washes it out for reporting purposes. |
| Spatial shifting (region choice) | ✅ Direct | Hourly CFE per region; clear regional differences. |
| Right-sizing / eliminate waste | ✅ Direct | Reducing vCPU-hours (smaller instances, turning off idle VMs) directly reduces usage units and thus allocated carbon. |
| Architecture choice (GPU vs CPU) | ⚠️ Approximate | SKU-level granularity exists, but per-SKU energy allocation is price-proportional, not physical. A cheaper SKU with the same energy draw gets less allocated carbon; a pricier SKU gets more. Price is correlated with but not identical to energy. |
| Embodied carbon (hardware choice) | ⚠️ Approximate | Proportional-to-energy allocation is a proxy; GPU-heavy workloads may be under/over-attributed. |

---

### Microsoft Azure

```yaml
provider_name: "Microsoft Azure"
tool_name: "Emissions Impact Dashboard (EID); Carbon Optimization (Azure portal + REST API)"
# EID: subscription × service × region level, up to 5 years retention, Power BI / Fabric
# Carbon Optimization: resource_group × resource level, 12-month retention, Azure portal + REST API, AI-driven reduction recommendations via Azure Advisor
methodology_version: "CHEM Whitepaper 2026; Azure Emissions Calculation Methodology (updated January 2026)"
reporting_delay_days: 19  # per Carbon Optimization docs: "Data for the previous month is available by day 19 of the current month"
customer_temporal_granularity: monthly
internal_temporal_granularity: monthly  # assumed
customer_reporting_dimensions: [subscription, service_category, region, resource_group, resource]  # resource_group and resource via Carbon Optimization only
recommended_reconciliation_unit: "subscription × service_category × region × month"
historical_recast_policy: limited_window
recast_window_months: 12
data_retention_months: 12  # Carbon Optimization: 12 months; EID offers up to 5 years via Power BI but primary retention is 12 months
api_access: true  # Fabric / Power BI (EID); Azure portal + REST API (Carbon Optimization)

# Scope 2 — Energy to Carbon
emission_factor_temporal_resolution: monthly
emission_factor_source: "Regional grid operators"
emission_factor_source_fallback: "IEA annual"
grid_region_mapping: provider_region

# Energy Allocation
primary_allocation_method: usage
fallback_allocation_method: null  # not disclosed; Azure does not describe any explicit fallback
fallback_allocation_scope: null  # not disclosed
usage_allocation_unit: "normalized cost metric (2021 whitepaper: 'the normalized cost metric associated with IaaS, PaaS or SaaS... normalized to exclude discounts and other variables'); described as compute, storage, and data transfer time in 2025 Carbon Optimization docs — unclear if methodology evolved or terminology differs"
economic_allocation_basis: null  # not formally disclosed as economic, but normalized cost metric basis is closer to economic than physical
allocation_granularity: service_category
idle_capacity_treatment: undisclosed
allocation_uncertainty_pct: "15-30%"

# Overhead
pue_type: undisclosed
pue_granularity: undisclosed
scope1_allocation_method: usage  # "usage time in compute, storage, or network categories"
cooling_allocation_method: undisclosed
networking_overhead_included: null

# Embodied Carbon
it_hardware_included: true
it_hardware_lca_boundary: cradle_to_grave
it_hardware_lifetime_years: 6
it_hardware_lifetime_treatment: amortize_then_zero  # zero after 6 years; asymmetric: if equipment life < 6 years, emissions still counted for 6 years (conservative)
building_embodied_included: false
building_lifetime_years: null
non_it_infrastructure_included: false
end_of_life_included: true
embodied_carbon_allocation_method: usage  # consistent with overall usage-based allocation approach
lca_data_source: "Component-level LCA via CHEM (Material Circularity and Life Cycle Carbon Emission Calculator v7.3); AI-augmented for scale. Component types: rack, disk drive, server blades, FPGA, power supply units, other"
embodied_uncertainty_pct: "10-20% (LCA-backed), 15-30% (AI-augmented)"

# Other Scope 3
# Azure explicitly lists "scope 3 categories 1, 2, 4, 5, 9, and 12" per emissions calculation methodology
fera_included: false  # Cat. 3 NOT in Azure's listed categories
upstream_transport_included: true  # Cat. 4 explicitly listed (upstream transportation: manufacturer → datacenter dock)
waste_included: true  # Cat. 5 explicitly listed (waste generated in operations)
downstream_transport_included: true  # Cat. 9 explicitly listed (downstream transportation: datacenter → recycler)
end_of_life_treatment_included: true  # Cat. 12 explicitly listed (recycling, landfill, composting)
purchased_goods_services_included: true  # Cat. 1 explicitly listed (raw material extraction)
business_travel_included: false
employee_commuting_included: false
other_scope3_allocation_method: usage

# Verification
third_party_assurance: true
assurance_scope: "Scope 3 methodology document only (WSP USA)"
tool_implementation_audited: false
methodology_publicly_available: true  # partial
```

**Azure — Reconcilability Summary:**

| Lever | Reconcilable? | Notes |
|-------|--------------|-------|
| Compute efficiency (reduce compute utilization) | ❌ Not rewarded | Usage allocation (compute, storage, network time). Compute utilization not reflected — same usage time = same carbon. |
| Temporal shifting | ❌ Not rewarded | Monthly emission factors. |
| Spatial shifting (region choice) | ⚠️ Approximate | Regional emission factors differ; usage-based approach preserves regional signal. |
| Right-sizing / eliminate waste | ✅ Direct | Reducing usage time (compute/storage/network) directly reduces allocated carbon. Carbon Optimization tool provides AI-driven recommendations (via Azure Advisor) for shutdown of idle VMs and rightsizing, with estimated carbon and cost savings per recommendation. |
| Architecture choice | ⚠️ Approximate | Only reconciles if the more efficient hardware completes the job faster (less usage time). Same duration = same carbon. Service-category granularity (not SKU) may not capture all differences. |
| Eliminate idle resources | ✅ Direct | Azure's allocation is based on compute, storage, and data transfer time — turning off idle resources directly reduces allocated carbon. Carbon Optimization surfaces idle VM recommendations with per-resource carbon savings estimates. |

**Note on allocation basis:** The 2021 Scope 3 Whitepaper defines Azure usage as a "normalized cost metric," which is closer to economic allocation than physical usage. If the allocation is indeed cost-based rather than resource-time-based, the reconcilability of right-sizing and idle resource elimination may be weaker than stated above — cost-normalized allocation does not guarantee that reducing physical resource consumption proportionally reduces the allocated carbon. The 2025 Carbon Optimization docs describe usage as "compute, storage, and data transfer" time, which would support stronger reconcilability. The true allocation basis is uncertain.

---

## Cross-Provider Analysis: What Can We Actually Reward?

| Optimization Lever | GCP | AWS | Azure | Depends on |
|--------------------|-----|-----|-------|------------|
| **Compute efficiency** (reduce compute utilization) | ❌ not rewarded | ❌ not rewarded | ❌ not rewarded | Allocation method — all three use usage allocation at customer level |
| **Temporal shifting** | ⚠️ internal only | ❌ | ❌ | Emission factor temporal resolution |
| **Spatial shifting** | ✅ direct | ✅ direct | ✅ direct | Emission factor spatial resolution — all three use regional factors |
| **Right-sizing** (fewer resource-time units) | ✅ direct (fewer vCPU-hours) | ✅ direct (fewer instance-hours) | ✅ direct (less usage time) | Allocation method — fewer resource-time units |
| **Hardware efficiency** (newer instance type) | ⚠️ only if fewer vCPU-hours | ⚠️ only if fewer instance-hours | ⚠️ only if less usage time | Allocation method — reconciles only if job finishes faster |
| **Eliminate idle resources** | ✅ direct (reduces vCPU-hours) | ✅ direct (reduces instance-hours) | ✅ direct (reduces usage time) | Allocation method — fewer resource-time units |

### Universally safe to reward (reconcilable across all three):
- **Spatial shifting** (all three use regional emission factors)
- **Eliminate idle resources** (reduces resource-time: vCPU-hours, instance-hours, usage time — across all allocation methods)
- **Right-sizing** (reduces resource-time, which all three providers track)

### Not rewarded by any provider at the customer level:
- **Compute efficiency** (reducing compute utilization) — all three providers use usage allocation at the customer level: GCP allocates by vCPU-hours, AWS foundational by instance-hours, Azure by usage time. No provider's customer-facing methodology reflects whether a VM or GPU instance is at 5% or 95% utilization. The only way to reduce the reported number is to reduce resource-time (run for less time, use fewer/smaller instances, turn off idle VMs).

### Conditionally reconcilable:
- **Architecture choice** — approximate on GCP (price-based SKU distribution correlates with but is not identical to energy); approximate on AWS foundational (usage-based); approximate on Azure (service-category granularity may not capture hardware-level differences)
- **Temporal shifting** — only if provider uses sub-monthly emission factors (currently: GCP internally, none customer-facing)

### Key findings:
- **Compute utilization is invisible to all three customer-facing methodologies.** This is the most important practical implication: a VM or GPU instance running idle and one at full load report the same carbon for the same duration and SKU. All three use usage allocation at the customer level. Only reducing resource-time (turning off instances, right-sizing, running for less time) moves the reported number.
- **All three providers use usage-based allocation at the customer boundary.** GCP's internal physical measurement is best-in-class, but the customer-facing step distributes energy by price-proportional SKU factors and resource-time (vCPU-hours). AWS foundational uses instance-hours. Azure uses usage time. The physically-measured total may be preserved at the aggregate level, but individual customer-level attribution is usage-based across all three. GCP and AWS both use economic/cost-based fallbacks for some services (GCP: internal shared services; AWS: non-foundational services); Azure's fallback approach is not disclosed.
- Azure's usage-factor approach is better than pure cost-based allocation but the undisclosed derivation of the usage factor limits confidence. The reconciliation gap is bounded (correlated with physical usage) but not precisely quantifiable without more disclosure from Microsoft.

---

## Minimum Viable Profile: What Must a Provider Disclose?

Based on this analysis, these are the **minimum parameters** a provider must disclose (or we must be able to determine) for the framework to generate reconcilable actionable signals:

### Required (framework cannot function without):
1. `primary_allocation_method` — usage vs economic determines whether and how well energy-based signals reconcile
2. `emission_factor_temporal_resolution` — determines which time-based optimizations are valid
3. `customer_reporting_dimensions` and `recommended_reconciliation_unit` — determine the exact slice at which reconciliation should happen
4. `allocation_granularity` — determines at what level we can provide physically meaningful action signals
5. `customer_temporal_granularity` — determines feedback loop speed

### Required for reconciliation (framework works but reconciliation gap is unbounded without):
6. `it_hardware_lifetime_years` — needed to model embodied carbon baseline
7. `embodied_carbon_allocation_method` — needed to reconcile Scope 3
8. `scope1_allocation_method` — needed for complete picture
9. `pue_type` and `pue_granularity` — needed to bridge raw energy to facility energy

### Desirable (improves accuracy but framework degrades gracefully without):
10. `fallback_allocation_scope` — which services use the fallback allocation method
11. `idle_capacity_treatment` — affects accuracy of per-slice attribution
12. `lca_data_source` — affects embodied carbon confidence bounds
13. `emission_factor_source` — affects Scope 2 accuracy

---

## Open Questions

1. **How should the framework handle Azure's usage allocation given the normalized cost metric basis?** The 2021 Scope 3 Whitepaper defines Azure usage as a "normalized cost metric... normalized to exclude discounts and other variables," which is closer to economic allocation than physical usage. The 2025 Carbon Optimization docs describe it as "compute, storage, and data transfer" time. This tension creates ambiguity about whether Azure's allocation is truly usage-based or economic-adjacent. Options: (a) treat as `approximate` with wider confidence intervals reflecting the cost-metric uncertainty, (b) require Microsoft to clarify the current allocation basis (cost-metric vs. resource-time) before claiming reconcilability, (c) empirically determine the correlation by comparing bottom-up estimates with top-down actuals over multiple months, (d) treat as two regimes — pre-2025 (cost-metric) and post-2025 (possibly resource-time) — pending confirmation of a methodology change.

2. **How to handle GCP's hourly-internal / monthly-external gap?** GCP computes hourly but reports monthly. If a user shifts load to low-carbon hours, the internal accounting captures it but the customer-facing report doesn't show it at that granularity. Do we reward it (because it's real) or not (because the customer can't verify it in their report)?

3. **How to model the overhead delta?** The gap between slice-level bottom-up action totals and provider reports includes shared infrastructure, embodied carbon, and allocation artifacts. Should the profile include an expected overhead ratio, or should this be discovered empirically?

4. **Provider profile versioning.** Methodologies change (e.g., AWS's Oct 2024 expansion). The profile needs a versioning mechanism, and ideally the framework should detect when a provider's methodology changes and flag that reconciliation assumptions may need updating.

5. **How should coverage gaps be represented?** A provider slice may be only partially instrumented. Should the profile carry explicit coverage assumptions, or should coverage be handled entirely in the reconciliation model?
