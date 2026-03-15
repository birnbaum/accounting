# Cloud Carbon Accounting Methodology Comparison: AWS, Google Cloud, Azure
## Agent-Ready Technical Reference — IaaS/PaaS Focus

Based on:
- AWS Customer Carbon Footprint Methodology, Model 3.0: https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology.pdf
- Google Carbon Footprint reporting methodology: https://docs.cloud.google.com/carbon-footprint/docs/methodology
- Azure emissions calculation methodology: https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology

**Scope:** This document covers only IaaS and PaaS offerings. Microsoft 365 and other SaaS products are explicitly excluded.  
**Sources:** AWS CCFT Methodology PDF (October 2025), Apex Companies LLC Assurance Statement, Google Cloud Carbon Footprint Methodology Docs, Schneider & Mattia arXiv:2406.09645, Azure Emissions Calculation Methodology (Microsoft Learn), Microsoft Scope 3 Whitepaper (2021), Microsoft Cloud Hardware Emissions Methodology (CHEM) Whitepaper (2026), GHG Protocol Corporate Standard, GHG Protocol Scope 3 Standard, GHG Protocol Scope 2 Guidance (2015), HotCarbon 2024 academic papers.  
**Last updated:** March 2026

---

## 1. Tool Overview

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Tool name** | Customer Carbon Footprint Tool (CCFT) | Google Cloud Carbon Footprint | Emissions Impact Dashboard (EID) |
| **Launched** | 2022 | 2021 | 2020 |
| **Scope 3 added** | April 2024 (IT hardware); expanded Oct 2024 (buildings, non-IT, waste, transport) | 2021 (embodied carbon included from launch) | 2021 (methodology whitepaper) |
| **Primary calculation approach** | Usage allocation for foundational services (instance-hours); economic (revenue) fallback for non-foundational services | Two-stage: physical measurement internally (machine-level power telemetry) → usage allocation at customer boundary (vCPU-hours × price-derived SKU factor) | LCA-based embodied carbon (CHEM) + usage allocation via customer usage factors per datacenter region |
| **Claimed GHG standard** | GHG Protocol Corporate Standard + Scope 3 Standard | GHG Protocol Corporate Standard + Scope 3 Standard | GHG Protocol Corporate Standard + Scope 3 Standard |
| **Third-party verified** | Yes — limited scope | No — academic critical review only | Yes — limited scope |
| **Verifier** | Apex Companies, LLC | Fraunhofer IZM (ISO 14040/14044 critical review) | WSP USA |
| **Verification scope** | Scope 3 Cat. 2, 3, 4 only; Scope 1 unverified; Oct 2024 expansion not re-verified | LCA methodology for hardware embodied carbon only; customer tool not audited | Scope 3 methodology document only; tool implementation not audited |
| **Reporting delay** | ≤21 days (as of Dec 2025; previously ~3 months) | ~15 days | ~15 days (by 15th of following month) |
| **Historical data retention** | 38 months | Unlimited (BigQuery export) | 12 months only |
| **Historical recasting on methodology change** | Full recast to January 2020 | Full recast capability via BigQuery | 12-month window only |
| **API / programmatic access** | No | Yes (BigQuery export) | Yes (Microsoft Fabric / Power BI) |
| **Service coverage** | 200+ AWS services | All GCP services (per SKU per region) | Major Azure IaaS/PaaS services |

---

## 2. Scope 1 Emissions

All three providers include Scope 1 in their customer-facing tools. Scope 1 sources for cloud data centers are: stationary combustion (diesel backup generators, natural gas boilers), fugitive emissions (refrigerant leaks from cooling systems), and mobile combustion (fleet vehicles).

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Stationary combustion included** | Yes | Yes | Yes |
| **Fugitive refrigerant emissions included** | Yes | Yes | Yes |
| **Mobile combustion (fleet)** | Unclear | Yes | Unclear |
| **Allocation method to customers** | Usage (resource utilization described as physical) | Usage at customer level (physical measurement internally; price-based SKU distribution + vCPU-hours to customers) | Usage (customer usage factors per datacenter region) |
| **Scope 1 independently verified** | No | No | No |

**GHG Protocol position:** The GHG Protocol Corporate Standard requires all owned/controlled combustion and fugitive sources. All three comply on coverage. On allocation, the GHG Protocol guidance prefers physical allocation. All three providers use usage allocation at the customer level for Scope 1: GCP's internal physical measurement feeds into a usage-based customer-facing step; AWS describes its method as physical but customer-facing granularity is consistent with usage allocation; Azure uses a usage-factor approach.

**Key difference:** GCP measures power physically internally (machine-level telemetry) but the customer-facing step distributes by resource-time. AWS describes physical allocation but does not disclose whether individual customer utilization is reflected. Azure describes a usage-factor approach ("usage time in compute, storage, or network categories helps attribute Scope 1 and 2 emissions"), but the detailed allocation parameters are not fully disclosed, making independent verification difficult.

---

## 3. Scope 2 Emissions

All three providers report both location-based (LBM) and market-based (MBM) Scope 2, as required by the GHG Protocol Scope 2 Guidance (2015).

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Location-based method (LBM)** | Yes | Yes | Yes |
| **Market-based method (MBM)** | Yes | Yes | Yes |
| **LBM emission factor source** | Regional grid operator data; IEA fallback | Electricity Maps API (hourly); IEA annual fallback | Regional grid operator data; IEA fallback |
| **LBM temporal granularity** | Monthly | Hourly (internal); monthly (customer-facing) | Monthly |
| **MBM instrument** | Energy Attribute Certificates (EACs) | Power Purchase Agreements (PPAs) + EACs | Power Purchase Agreements (PPAs) |
| **EAC/PPA temporal matching** | Not disclosed (likely annual) | Hourly CFE percentage reported per region | Not disclosed |
| **EAC/PPA spatial matching** | Not disclosed | Reported at region level | Not disclosed |
| **Uncertainty (LBM)** | Medium (~5–15%) | Low–Medium (~5–10%) | Medium (~5–15%) |

**Key difference — temporal granularity:** GCP uses hourly Electricity Maps data internally, which captures significant intra-day variation in grid carbon intensity. AWS and Azure use monthly or annual grid factors, which average out this variation. The GHG Protocol Scope 2 Guidance recommends the most accurate available data, making GCP's approach most aligned with the spirit of the standard.

**Key difference — EAC matching:** GCP reports hourly carbon-free energy (CFE) percentages per region, indicating more granular renewable energy matching. AWS and Azure do not disclose their matching methodology, suggesting likely annual matching. Hourly, location-matched EAC matching is the best practice (as recommended by the GHG Protocol Scope 2 Technical Guidance and the GSF Real Time Energy and Carbon Standard).

---

## 4. Scope 3 Emissions — Category Coverage

The GHG Protocol Scope 3 Standard defines 15 upstream and downstream categories. For cloud providers (as service providers, not product sellers), the most material upstream categories are Category 2 (Capital Goods), Category 3 (Fuel and Energy-Related Activities / FERA), Category 4 (Upstream Transportation), Category 5 (Waste), Category 6 (Business Travel), and Category 7 (Employee Commuting).

| GHG Protocol Scope 3 Category | AWS | GCP | Azure | Notes |
|---|---|---|---|---|
| **Cat. 1: Purchased Goods & Services** | N/A | N/A | N/A | Not applicable — these providers *are* the service |
| **Cat. 2: IT Hardware (servers, networking, storage)** | ✅ Full | ✅ Full | ⚠️ Partial (critical flaw) | Azure: zero emissions after 6-year cutoff — see §6.2 |
| **Cat. 2: Data center buildings (embodied carbon)** | ✅ Full (added Oct 2024) | ✅ Full | ❌ Excluded | Azure excludes (methodology doc notes it "might add as data becomes available") |
| **Cat. 2: Non-IT infrastructure (UPS, cooling, etc.)** | ✅ Full | ⚠️ Partial | ❌ Excluded | AWS most complete |
| **Cat. 3: Fuel & Energy-Related Activities (FERA)** | ✅ Full | ✅ Full | ✅ Full | All three comply |
| **Cat. 4: Upstream Transportation & Distribution** | ✅ Full | ⚠️ Partial | ⚠️ Partial | Hardware lifecycle LCA includes transport; Azure source explicitly lists Cat. 4 in scope |
| **Cat. 5: Waste Generated in Operations** | ✅ Full | ❌ Excluded | ❌ Excluded | AWS only |
| **Cat. 6: Business Travel** | ❌ Excluded | ✅ Full | ❌ Excluded | GCP only |
| **Cat. 7: Employee Commuting** | ❌ Excluded | ✅ Full | ❌ Excluded | GCP only |
| **Cat. 8–15: Downstream categories** | N/A | N/A | N/A | Not material for cloud providers as service sellers |
| **End-of-Life Treatment of Hardware** | ❌ Excluded | ❌ Excluded | ✅ Full | Not a standard GHG Protocol category; Azure only |

**GHG Protocol category count (approximate):**
- **AWS:** 4 categories (Cat. 2 full incl. buildings, Cat. 3, Cat. 4, Cat. 5)
- **GCP:** 4 categories (Cat. 2 full incl. buildings, Cat. 3, Cat. 6, Cat. 7)
- **Azure:** 3 categories (Cat. 2 partial with lifetime flaw, Cat. 3 unclear, Cat. 4 partial via hardware LCA)

**GHG Protocol position:** The Scope 3 Standard requires companies to include all material categories. For cloud providers, Category 2 (Capital Goods) is unambiguously material and required. Categories 3, 4, 5, 6, and 7 are likely material for hyperscale operators but are not included by all providers. The omission of these categories is a gap, not necessarily a violation — the GHG Protocol allows companies to exclude immaterial categories with justification. However, none of the three providers publicly discloses a materiality assessment justifying their exclusions.

---

## 5. Allocation Methodology

Allocation is the most technically complex and consequential methodological choice. It determines how data-center-level emissions are attributed to individual customer workloads.

### 5.1 AWS — Usage Allocation with Economic Fallback

AWS uses a two-tier allocation cascade:

**Tier 1 (foundational services — EC2, S3, RDS, etc.):** AWS describes this as physical allocation based on resource utilization metrics (CPU utilization, memory usage, storage I/O, network throughput). However, at the customer level the allocation unit is instance-hours — usage allocation. Whether internal physical telemetry (actual CPU utilization) feeds into the per-instance-hour factor, or whether all instances of the same type receive the same hourly rate regardless of utilization, is not publicly disclosed. The methodology document describes the approach as physical, but the customer-facing granularity (per service per region per account, monthly) is consistent with usage allocation.

**Tier 2 (non-foundational services — Lambda, SageMaker, Athena, Redshift, and many managed services):** Economic allocation based on the service's relative revenue contribution (equivalent revenue share). Revenue is used as a proxy for resource consumption.

**Critical weakness:** The list of non-foundational services is not publicly disclosed. The proportion of total emissions subject to economic allocation is not disclosed. Revenue is a poor proxy for resource consumption — a high-margin service may consume fewer resources than a low-margin one yet be allocated more emissions. Estimated uncertainty for non-foundational service allocation: ~20–40%.

### 5.2 GCP — Usage Allocation with Economic Fallback

GCP uses the most granular approach of the three providers, but it operates in two distinct stages with different allocation methods:

**Stage 1 — Internal allocation (physical):** Machine-level power monitoring at rack level. Each physical machine's power draw is decomposed into dynamic power (workload-driven, allocated proportional to GCU usage) and idle power (allocated by resource-weighted shares). Shared internal services (Colossus, Spanner, Bigtable) are reallocated from service providers to end-user teams via resource-based or cost-based methods. This stage is genuinely physical and best-in-class. Uncertainty: ~5–15%.

**Stage 2 — Customer-facing allocation (price-based + usage units):** Each internal team's total energy is distributed across customer-facing SKUs using **price-based proportionality** (Schneider & Mattia 2024, Eq. 10): energy per usage unit for a SKU is set proportional to that SKU's list price. Customers are then allocated based on their **usage units** (e.g., vCPU-hours for Compute Engine, GiB-months for storage). This means a VM at 5% CPU utilization and one at 95% receive identical carbon allocation for the same vCPU-hours and SKU. The physical signal from Stage 1 is preserved at the aggregate level (the Compute Engine team's total reflects real energy) but is washed out at the individual customer level.

**Non-electricity Scope 3 emissions (embodied carbon, FERA, transport):** Allocated using a proportional ratio: customer electricity use / total GCP electricity use. This is a simplification assuming non-electricity emissions are proportional to electricity consumption. Uncertainty: ~20–35%.

**Strength:** Internal machine-level power monitoring is the most accurate approach for electricity-related emissions. The two-stage methodology paper (Schneider & Mattia 2024) is fully published, making GCP the most transparent provider.

**Weakness:** The price-based SKU distribution step means customer-facing allocation does not reflect actual CPU utilization — only usage units (time × size). The paper explicitly acknowledges this: "Cost-based allocation doesn't signal actual efficiency differences." The proportional allocation for non-electricity Scope 3 is a proxy that may not accurately reflect the actual distribution of embodied carbon across customers with different workload types (e.g., GPU-heavy AI workloads vs. CPU-only compute).

### 5.3 Azure — Usage Allocation

Azure uses usage allocation via customer usage factors:

**Azure IaaS/PaaS:** Emissions are allocated based on a customer's relative Azure usage in a given datacenter region. An algorithm calculates a usage factor (emissions per unit of customer usage in a specific region) and applies it directly. Usage is calculated from compute, storage, and data transfer. The methodology is described as consistent across Scope 1, 2, and 3. The precise definition of the "usage factor" units and how they are derived are not fully disclosed in the public methodology document, limiting independent verification. Uncertainty: ~15–30%.

**GHG Protocol position on allocation:** The Scope 3 Standard prefers physical allocation. All three providers use usage allocation at the customer level: GCP allocates by vCPU-hours (per SKU), AWS foundational by instance-hours (per service), and Azure by usage time (per region). GCP's internal pipeline measures power physically (machine-level power telemetry), but the customer-facing step introduces price-based proportionality (Schneider & Mattia 2024, Eq. 10). Without full disclosure of how AWS's per-instance-hour rate or Azure's usage factor are derived, it is not possible to confirm precise GHG Protocol alignment for any provider at the customer boundary.

### 5.4 Allocation Comparison Table

| Dimension | AWS | GCP | Azure |
|---|---|---|---|
| **Internal method** | Described as physical (foundational) | Physical (machine-level power telemetry, GCU-proportional) | Not disclosed |
| **Customer-facing method** | Usage (foundational: instance-hours) | Usage (vCPU-hours × price-derived energy factor per SKU) | Usage (customer usage factor per region) |
| **Fallback method** | Economic (non-foundational) | Proportional ratio (non-electricity Scope 3) | None |
| **Allocation granularity** | Service + region + account | SKU + region + account | Service category + region + account |
| **Idle capacity allocation** | Not disclosed | Allocated to services proportionally (internal) | Not disclosed |
| **CPU utilization reflected in customer allocation** | No (usage allocation) | No (usage allocation; price-proportional SKU distribution) | No (usage allocation) |
| **Allocation parameters disclosed** | Partial | Full (methodology paper: Schneider & Mattia 2024) | Partial (usage factor definition not fully disclosed) |
| **GHG Protocol alignment** | Partial | Partial (internal is physical/best-in-class; customer-facing introduces price-based step) | Partial (usage allocation aligns with GHG Protocol intent; parameters undisclosed) |

---

## 6. Equipment Lifetime and Embodied Carbon

### 6.1 Default Equipment Lifetime Assumption

Providers differ in the default equipment lifetime assumed for amortizing IT hardware embodied carbon. GCP uses **4 years** (aligned with financial accounting standards, though actual lifetimes are noted as significantly longer); AWS and Azure both use **6 years**.

| Provider | IT Hardware Lifetime | Building Lifetime | End-of-Life Treatment | LCA Boundary |
|---|---|---|---|---|
| **AWS** | 6 years | 50 years | Excluded (cradle-to-gate) | Cradle-to-gate |
| **GCP** | **4 years** | Included in customer tool | Excluded (cradle-to-gate) | Cradle-to-gate |
| **Azure** | 6 years | Excluded from customer tool | Included (CHEM) | Cradle-to-grave |

GCP's 4-year assumption means its per-year amortized embodied carbon is **50% higher** than what a 6-year assumption would produce for the same hardware — a material difference. GCP explicitly acknowledges this is a financial accounting convention and that real lifetimes are longer. AWS and Azure's 6-year assumption is closer to the physical median of hyperscale server refresh cycles (3–7 years) but may understate annual embodied carbon relative to actual utilization periods. The GHG Protocol Scope 3 Standard does not specify a required equipment lifetime, making this an area of under-specification where providers must make defensible choices.

### 6.2 Azure's Critical Equipment Lifetime Flaw

Azure's implementation of the 6-year lifetime contains a **methodological error**: once equipment has been in service for 6 years, its amortized Scope 3 embodied carbon contribution drops to **zero** in the EID.

This is incorrect. The embodied carbon of the equipment was emitted during manufacturing regardless of how long the equipment runs. A server that runs for 10 years does not have zero embodied carbon in years 7–10 — the carbon was emitted at manufacture and should have been fully amortized by year 6. The correct interpretation is that the embodied carbon is fully allocated by the end of the amortization period, not that it disappears.

The practical consequence is perverse: if Microsoft extends hardware lifetimes beyond 6 years (which it has publicly committed to as a sustainability measure), the EID reports *lower* Scope 3 emissions — the opposite of the correct direction. This creates a systematic underestimation for long-lived equipment. Microsoft has not publicly acknowledged this flaw or announced plans to fix it.

### 6.3 AWS Building Amortization

AWS amortizes data center building embodied carbon over 50 years. A 30-year assumption (more conservative and arguably more appropriate for data center facilities) would increase annual building embodied carbon by ~40–60%. The 50-year assumption is defensible but on the optimistic end.

### 6.4 LCA Methodology for Embodied Carbon

| Provider | LCA Approach | Data Source | Verification |
|---|---|---|---|
| **AWS** | Supplier EPDs (primary); AI/LLM estimation (fallback for undocumented components) | Supplier-provided Environmental Product Declarations | Apex Companies (limited scope) |
| **GCP** | Component-level LCA; academic literature for undocumented components | Internal LCA + Fraunhofer IZM review | Fraunhofer IZM critical review (ISO 14040/14044) |
| **Azure** | Component-level LCA via CHEM (Cloud Hardware Emissions Methodology); AI-augmented for scale | Component-level LCA + AI-augmented CHEM (2026 whitepaper) | WSP USA (methodology document only) |

AWS's use of AI/LLM estimation as a fallback for components without supplier EPDs introduces ~20–50% uncertainty for affected components. The proportion of the fleet relying on AI/LLM estimation is not disclosed.

---

## 7. Key Variables, Uncertainty, and Update Cadence

**Important caveat:** The uncertainty ranges below are estimates derived from methodology documentation, academic literature (particularly Bhagavathula et al. HotCarbon 2024, which found up to 1.45× deviation between embodied carbon models), and expert judgment. They are not formally published values from the providers. A rigorous quantification would require Monte Carlo simulation and access to provider internal data.

### 7.1 AWS Variables

| Variable | Source | Uncertainty | Update Cadence | Recast on Change |
|---|---|---|---|---|
| Energy consumption (MWh) | Utility meters | Low (~2–5%) | Monthly | Yes |
| Location-based emission factor | Regional grid operators; IEA | Medium (~5–15%) | Annually | Yes |
| Market-based emission factor | AWS renewable energy contracts (EACs) | Medium (~5–10%) | Annually | Yes |
| Service allocation ratio — foundational | AWS internal telemetry | Low–Medium (~5–10%) | Monthly | Yes |
| **Service allocation ratio — non-foundational** | AWS internal revenue data | **High (~20–40%)** | Not disclosed | Unknown |
| Embodied carbon — IT hardware (EPD-backed) | Supplier EPDs | Low–Medium (~10–15%) | With methodology updates | Yes |
| **Embodied carbon — IT hardware (AI/LLM fallback)** | AI/LLM estimation | **High (~20–50%)** | Not disclosed | Unknown |
| Embodied carbon — buildings | Engineering assessments | Medium–High (~15–25%) | Infrequent | Yes |
| Equipment lifetime — IT hardware | AWS internal assumption (6 yr) | Medium (~10–20%) | Rarely | Yes |
| Equipment lifetime — buildings | AWS internal assumption (50 yr) | Medium (~10–20%) | Rarely | Yes |

### 7.2 GCP Variables

| Variable | Source | Uncertainty | Update Cadence | Recast on Change |
|---|---|---|---|---|
| Machine-level power (kW) | Hardware telemetry | **Very Low (~1–3%)** | Continuous | Yes |
| Grid emission factor — Electricity Maps | Electricity Maps API | Low–Medium (~5–10%) | Hourly | Yes |
| Grid emission factor — IEA fallback | IEA annual data | Medium–High (~10–20%) | Annually | Yes |
| Carbon-free energy (CFE) % | Electricity Maps; GCP PPA procurement | Low–Medium (~5–10%) | Hourly | Yes |
| SKU-level carbon intensity factor | GCP internal telemetry | Low–Medium (~5–15%) | Monthly | Yes |
| **Non-electricity Scope 3 allocation ratio** | GCP internal electricity data | **High (~20–35%)** | Monthly | Yes |
| Embodied carbon — IT hardware | Fraunhofer IZM LCA | Low–Medium (~10–15%) | With LCA updates | Yes |
| Equipment lifetime — IT hardware | GCP internal assumption (4 yr, financial accounting standard) | Medium (~10–20%) | Rarely | Yes |

### 7.3 Azure Variables

| Variable | Source | Uncertainty | Update Cadence | Recast on Change |
|---|---|---|---|---|
| Hardware component LCA factor (EPD-backed) | Component-level LCA (CHEM) | Low–Medium (~10–20%) | With CHEM updates | Yes (12-mo window) |
| Hardware component LCA factor (AI-augmented) | AI-augmented CHEM (2026) | Medium–High (~15–30%) | With CHEM updates | Yes (12-mo window) |
| **Equipment lifetime — IT hardware** | Azure internal assumption (6 yr, zero after) | **High — systematic error** | Rarely | Yes (12-mo window) |
| **Usage factor (Azure IaaS/PaaS)** | Azure internal data (compute, storage, data transfer time) | **High (~15–30%)** | Monthly | Yes (12-mo window) |
| Regional electricity emission factor | Regional grid operators; IEA | Medium (~5–15%) | Annually | Yes (12-mo window) |
| End-of-life disposition factor | Microsoft disposition programs | Medium (~10–20%) | With CHEM updates | Yes (12-mo window) |

---

## 8. Reporting Delays and Recasting Practices

### 8.1 Reporting Delays

| Provider | Current Delay | Previous Delay | Change |
|---|---|---|---|
| **AWS** | ≤21 days (as of Dec 2025) | ~3 months | Major improvement |
| **GCP** | ~15 days | ~1 month | Moderate improvement |
| **Azure** | ~15 days (by 15th of following month) | ~1 month | Moderate improvement |

All three providers now offer sub-month reporting delays. AWS's December 2025 improvement (from ~3 months to ≤21 days) is the most significant recent change in reporting timeliness.

### 8.2 Recasting Practices

Recasting is the retroactive recalculation of historical emissions when methodology changes are made. It is essential for consistent year-over-year comparison and trend analysis.

| Provider | Recast Scope | Recast Trigger | Data Retention |
|---|---|---|---|
| **AWS** | Full recast to January 2020 | Any methodology change | 38 months |
| **GCP** | Full historical recast | Methodology changes; manual backfill via BigQuery | Unlimited (BigQuery) |
| **Azure** | 12-month window only | Methodology changes | 12 months |

**AWS recasting:** AWS recasts all historical data back to January 2020 when emission factors or allocation methods change. The April 2024 Scope 3 addition and October 2024 expansion were both applied retroactively. This is best practice.

**GCP recasting:** GCP has full historical recast capability via BigQuery. The Electricity Maps integration (introduced 2022) was applied retroactively. Customers with BigQuery export can access the full corrected history.

**Azure recasting:** Azure's 12-month retention window is a significant limitation. When methodology changes are made, only the most recent 12 months can be retroactively corrected. This makes multi-year trend analysis unreliable and prevents full GHG Protocol compliance on the recasting requirement. The GHG Protocol requires that when methodology changes are made, base year emissions should be recalculated — Azure's 12-month window prevents this for any change affecting data older than 12 months.

---

## 9. Spatial, Temporal, and Service Granularity

### 9.1 Spatial Granularity

| Provider | Regional Breakdown | Sub-Regional | Notes |
|---|---|---|---|
| **AWS** | Per AWS region | No | ~30+ regions globally |
| **GCP** | Per GCP region | No | ~40+ regions; hourly CFE per region |
| **Azure** | Per Azure region | No | ~60+ regions; some grouped |

No provider offers sub-regional (availability zone or data center level) granularity to customers.

### 9.2 Temporal Granularity

| Provider | Customer-Facing | Internal Calculation | Sub-Monthly Available |
|---|---|---|---|
| **AWS** | Monthly | Unknown | No |
| **GCP** | Monthly | Hourly | No (hourly CFE data only, not customer emissions) |
| **Azure** | Monthly | Unknown | No |

All three providers expose only monthly data to customers. GCP calculates internally at hourly resolution but aggregates to monthly for customer reporting. This is a systemic gap: carbon-aware computing requires sub-hourly granularity, but no provider exposes this to customers.

### 9.3 Service Granularity

| Provider | Service Coverage | Breakdown Level | Notes |
|---|---|---|---|
| **AWS** | 200+ services | Per service per region per account | Most comprehensive service coverage |
| **GCP** | All GCP services | Per SKU per region per project | SKU-level is highly granular |
| **Azure** | Major Azure IaaS/PaaS services | Per service category per region per subscription | Some services grouped |

---

## 10. Third-Party Verification — Detailed Assessment

### 10.1 AWS — Apex Companies, LLC

Apex Companies, LLC conducted an independent assurance engagement of the CCFT methodology. Key details:
- **Scope covered:** Scope 3 Categories 2 (Capital Goods — IT hardware), 3 (FERA), and 4 (Upstream Transportation)
- **Scope NOT covered:** Scope 1 (all sources), Scope 2, and the October 2024 Scope 3 expansion (buildings, non-IT equipment, waste)
- **Verification standard:** Not publicly disclosed
- **Assurance level:** Not publicly disclosed (limited or reasonable not stated)
- **What was verified:** The underlying management system and GHG emissions calculations for the three covered categories

**Assessment:** Legitimate but narrowly scoped. The non-disclosure of the verification standard and assurance level limits credibility. The October 2024 expansion — which added building embodied carbon, non-IT equipment, waste, and upstream transport — has not been re-verified, meaning approximately 30–40% of the current CCFT scope is unverified. AWS's public claim that "the CCFT methodology has been verified by an independent third party" is technically accurate but potentially misleading given the narrow scope.

### 10.2 GCP — Fraunhofer IZM Critical Review

Fraunhofer IZM (Institute for Reliability and Microintegration) conducted a critical review of Google Cloud's hardware embodied carbon LCA methodology per ISO 14040/14044.
- **Review type:** Academic critical review — not formal third-party assurance
- **Scope covered:** LCA methodology for hardware embodied carbon calculation
- **Scope NOT covered:** Customer-facing tool accuracy, data pipelines, allocation calculations, Scope 1, Scope 2, non-electricity Scope 3
- **Standard:** ISO 14040/14044 (LCA critical review, not GHG assurance)

**Assessment:** Methodologically rigorous for what it covers, but not equivalent to formal third-party assurance under ISO 14064-3 or similar. There is no independent audit confirming that what customers see in the Carbon Footprint tool accurately reflects the underlying methodology. GCP is the only provider with no formal GHG assurance engagement.

### 10.3 Azure — WSP USA

WSP USA conducted a third-party review of Azure's Scope 3 emissions methodology.
- **Scope covered:** Scope 3 methodology document
- **Scope NOT covered:** Scope 1, Scope 2, customer tool implementation accuracy, data pipelines
- **Standard:** Not fully disclosed; aligned with GHG Protocol principles

**Assessment:** Covers the methodology document but not the tool implementation. Provides assurance that the stated methodology is consistent with GHG Protocol, but not that the tool correctly implements the methodology.

### 10.4 Comparative Summary

None of the three providers offers comprehensive, end-to-end independent verification of their customer-facing tools. All three verification claims cover methodology documents or specific calculation approaches, not the full customer-facing tool. This is a systemic industry gap.

| Verification Dimension | AWS | GCP | Azure |
|---|---|---|---|
| Formal GHG assurance engagement | Yes | No | Yes |
| Scope 1 verified | No | No | No |
| Scope 2 verified | No | No | No |
| Scope 3 Cat. 2 (IT hardware) verified | Yes | LCA review only | Yes (methodology doc) |
| Scope 3 Cat. 3 (FERA) verified | Yes | No | Yes (methodology doc) |
| Scope 3 Cat. 4 (Transport) verified | Yes | No | N/A (excluded) |
| Oct 2024 expansion verified | No | N/A | N/A |
| Tool implementation verified | No | No | No |
| Verification standard disclosed | No | ISO 14040/14044 | Partial |
| Assurance level disclosed | No | N/A | Partial |

---

## 11. GHG Protocol Compliance Analysis

### 11.1 Areas of Clear Compliance (All Three Providers)

All three providers comply with: reporting both location-based and market-based Scope 2; including Scope 1 stationary combustion and fugitive emissions; including FERA in Scope 3 (Category 3); using GHG Protocol-aligned system boundaries and emission factor sources.

### 11.2 Clear Divergences from GHG Protocol Requirements

| Issue | Provider | GHG Protocol Requirement | Provider Practice | Severity |
|---|---|---|---|---|
| Allocation parameters undisclosed | Azure | Physical allocation preferred; parameters must be verifiable | Usage-factor approach described but internal derivation not disclosed | Medium |
| Equipment lifetime cutoff (zero after 6 yr) | Azure | Amortize over actual useful life | Zero emissions after 6 years | Critical |
| Historical recasting window | Azure | Recast base year when methodology changes | 12-month window only | High |
| Scope 3 material categories excluded | All | Include all material categories | Significant gaps (see §4) | High |
| Materiality assessment not disclosed | All | Justify exclusions with materiality assessment | No public materiality assessment | Medium |

### 11.3 Ambiguous Interpretations (Under-Specified GHG Protocol Areas)

These are areas where the GHG Protocol does not fully specify the correct approach and providers have made different but potentially defensible choices. A gold standard should resolve these ambiguities.

| Under-Specified Area | AWS Interpretation | GCP Interpretation | Azure Interpretation |
|---|---|---|---|
| Allocation of shared cloud infrastructure | Usage for foundational (instance-hours); economic fallback for non-foundational | Physical measurement internally; usage at customer boundary (vCPU-hours × price-derived factor); proportional ratio (non-electricity Scope 3) | Usage throughout (usage factors; parameters undisclosed) |
| Equipment lifetime assumption | 6 yr (IT); 50 yr (buildings) | 4 yr (IT, financial accounting standard) | 6 yr (IT) |
| EAC/PPA temporal matching | Not disclosed | Hourly CFE reported | Not disclosed |
| Building embodied carbon inclusion | Included (Oct 2024) | Included in customer tool | Excluded from customer tool |
| End-of-life hardware treatment | Excluded (cradle-to-gate) | Excluded (cradle-to-gate) | Included (cradle-to-grave) |
| Business travel and commuting | Excluded | Included | Excluded |
| Idle capacity allocation | Not disclosed | Proportionally allocated | Not disclosed |

---

## 12. Weaknesses and Methodological Gaps

### 12.1 AWS — Weaknesses

**Critical:**

1. **Economic allocation fallback for non-foundational services.** Revenue-based allocation is used for an undisclosed set of services including Lambda, SageMaker, Athena, Redshift, and many managed services. Revenue is a poor proxy for resource consumption. The list of affected services and the proportion of total emissions subject to this fallback are not publicly disclosed. Estimated uncertainty: ~20–40%. This is the single largest source of opacity in the CCFT.

2. **Incomplete and non-transparent verification.** Apex Companies verification covers only Scope 3 Categories 2, 3, and 4. Scope 1 is unverified. The October 2024 expansion (buildings, non-IT equipment, waste) has not been re-verified. The verification standard and assurance level are not disclosed. AWS's public claim of third-party verification is technically accurate but potentially misleading.

**High:**

3. **AI/LLM fallback for hardware embodied carbon.** For hardware components without supplier-provided Environmental Product Declarations (EPDs), AWS uses AI/LLM estimation. Estimated uncertainty: ~20–50% for affected components. The proportion of the fleet relying on this fallback is not disclosed.

4. **Business travel and employee commuting excluded.** GHG Protocol Categories 6 and 7 are excluded. GCP includes both. No materiality assessment justifying the exclusion is published.

5. **Allocation methodology opacity.** The specific allocation ratios, the service classification criteria (foundational vs. non-foundational), and the revenue data used for economic allocation are not publicly disclosed. This makes independent verification or replication impossible.

**Medium:**

6. **50-year building amortization may underestimate annual carbon.** A 30-year assumption (more conservative, arguably more appropriate for data center facilities) would increase annual building embodied carbon by ~40–60%.

7. **No sub-monthly temporal granularity.** Monthly data only; carbon-aware computing requires sub-hourly granularity.

8. **EAC temporal and spatial matching not disclosed.** Likely annual matching, which overstates renewable energy impact relative to hourly, location-matched matching.

### 12.2 GCP — Weaknesses

**Critical:**

1. **End-of-life hardware emissions excluded from customer tool.** GCP uses cradle-to-gate LCA only. End-of-life treatment (recycling, disposal, refurbishment) represents approximately 5–15% of hardware lifecycle emissions. This is excluded despite being included in GCP's internal LCA.

**High:**

2. **Non-electricity Scope 3 uses simplified proportional allocation.** The ratio of customer electricity use to total GCP electricity use is used as a proxy for all non-electricity Scope 3 emissions (embodied carbon, FERA, transport). This assumes non-electricity emissions are proportional to electricity consumption, which may not hold for GPU-heavy AI workloads vs. CPU-only compute. Estimated uncertainty: ~20–35%.

3. **No formal third-party assurance of customer tool.** The Fraunhofer IZM critical review covers only the LCA methodology for hardware embodied carbon. The customer-facing tool, data pipelines, and allocation calculations have not been independently audited.

4. **4-year amortization period understates equipment lifetimes.** GCP uses a 4-year financial accounting standard for hardware amortization, despite acknowledging actual lifetimes are significantly longer. This produces higher annual embodied carbon than a 6-year assumption, but may overstate yearly allocation if hardware is actually used for 8–10 years.

5. **IEA annual fallback for uncovered grid regions.** For regions not covered by Electricity Maps, GCP falls back to IEA annual average emission factors. Estimated uncertainty: ~10–20% for affected regions. Affected regions are not disclosed.

**Medium:**

6. **Waste generated in operations excluded.** GHG Protocol Category 5 excluded. No materiality assessment published.

7. **Hourly internal data not exposed to customers.** GCP calculates emissions internally at hourly resolution but exposes only monthly aggregates. This prevents customers from performing carbon-aware optimization using provider-reported data.

### 12.3 Azure — Weaknesses

**Critical:**

1. **Zero emissions after 6-year equipment lifetime — methodological error.** Once IT hardware has been in service for 6 years, its amortized Scope 3 embodied carbon drops to zero in the EID. This is a methodological error, not just a gap. The embodied carbon was emitted at manufacture and should have been fully amortized by year 6 — not disappear. If Microsoft extends hardware lifetimes beyond 6 years (a stated sustainability goal), the EID will report *lower* Scope 3 emissions, creating a perverse incentive. Not acknowledged by Microsoft.

2. **Allocation parameters not fully disclosed.** Azure describes a usage-factor approach (emissions per unit of customer usage in a given region) consistent across Scope 1, 2, and 3. However, the internal derivation of the usage factor — including what "usage" units are measured and how they are aggregated — is not publicly disclosed. This prevents independent verification or replication. Estimated uncertainty: ~15–30%.

**High:**

3. **Narrowest Scope 3 coverage of the three providers.** Only 2 of 15 GHG Protocol categories (Cat. 2 with flaw, Cat. 3). AWS covers 4 categories; GCP covers 3–4. Building embodied carbon, upstream transport, waste, business travel, and employee commuting are all excluded.

4. **Building embodied carbon excluded.** No announced plans to include. This is a material omission for a company operating 200+ data centers globally.

5. **WSP USA verification does not cover customer tool accuracy.** Verification covers only the methodology document. There is no assurance that the EID correctly implements the stated methodology.

6. **Methodology inconsistency with Microsoft corporate GHG disclosure.** The sum of all customer-reported emissions in the EID does not equal Microsoft's corporate Scope 3 disclosure. Microsoft has not publicly reconciled this discrepancy. This raises questions about whether the EID is internally consistent with Microsoft's own accounting.

7. **12-month data retention prevents multi-year trend analysis.** Insufficient for GHG Protocol base year recalculation requirements. Makes it impossible to track emissions trends over the 3–5 year horizons relevant to corporate sustainability commitments.

**Medium:**

8. **End-of-life methodology not fully transparent.** While Azure includes end-of-life treatment (unique among the three providers), the specific disposition rates and calculation methodology are not fully disclosed.

9. **Renewable energy matching methodology not disclosed.** PPA temporal and spatial matching criteria are not disclosed, making it impossible to assess the quality of market-based Scope 2 accounting.

---

## 13. Gold Standard Requirements — Compliance Assessment

The following table assesses each provider against a set of gold standard requirements derived from GHG Protocol guidance and best practices. Status codes: **Full** = fully met; **Partial** = partially met or with caveats; **Not Met** = not met; **Unclear** = insufficient information to assess; **Error** = actively incorrect (not just a gap).

| Gold Standard Requirement | AWS | GCP | Azure | Notes |
|---|---|---|---|---|
| **SCOPE 1** | | | | |
| Include all stationary combustion sources | Full | Full | Full | |
| Include fugitive refrigerant emissions | Full | Full | Full | |
| Use physical allocation to customers | Partial | Partial | Not Met | All three use usage allocation at customer level; GCP measures physically internally; AWS describes as physical but customer-facing is instance-hours; Azure uses usage factors |
| Independent verification of Scope 1 | Not Met | Not Met | Not Met | No provider verifies Scope 1 |
| **SCOPE 2** | | | | |
| Report both LBM and MBM | Full | Full | Full | |
| Use granular (sub-annual) grid emission factors | Partial | Full | Partial | GCP: hourly; AWS/Azure: monthly |
| Disclose EAC/PPA temporal matching method | Unclear | Partial | Unclear | GCP reports hourly CFE; others undisclosed |
| Use location-matched EACs/PPAs | Unclear | Partial | Unclear | Best practice; only GCP partially disclosed |
| **SCOPE 3 — CAPITAL GOODS (CAT. 2)** | | | | |
| Include IT hardware embodied carbon | Full | Full | Error | Azure: zero after 6 yr — methodological error |
| Include building embodied carbon | Full | Full | Not Met | Azure excludes; AWS added Oct 2024; GCP includes in customer tool |
| Include non-IT infrastructure | Full | Partial | Not Met | |
| Use cradle-to-grave LCA (incl. end-of-life) | Not Met | Not Met | Full | Azure only; others cradle-to-gate |
| Disclose equipment lifetime assumption | Full | Partial | Partial | |
| Use defensible equipment lifetime | Full | Full | Error | Azure: zero-after-6yr creates systematic error |
| **SCOPE 3 — FERA (CAT. 3)** | | | | |
| Include fuel and energy-related activities | Full | Full | Full | All three comply |
| **SCOPE 3 — UPSTREAM TRANSPORT (CAT. 4)** | | | | |
| Include upstream hardware transportation | Full | Partial | Not Met | |
| **SCOPE 3 — WASTE (CAT. 5)** | | | | |
| Include waste generated in operations | Full | Not Met | Not Met | AWS only |
| **SCOPE 3 — BUSINESS TRAVEL & COMMUTING (CAT. 6/7)** | | | | |
| Include business travel (Cat. 6) | Not Met | Full | Not Met | GCP only |
| Include employee commuting (Cat. 7) | Not Met | Full | Not Met | GCP only |
| **ALLOCATION** | | | | |
| Use physical allocation as primary method | Partial | Partial | Partial | GCP: physical measurement internally, but customer-facing uses price-based SKU distribution + usage units; Azure: usage-factor approach, parameters undisclosed |
| Disclose allocation methodology and parameters | Partial | Full | Partial | GCP is most transparent (full methodology published); Azure: usage factor definition not fully disclosed |
| Disclose which services use economic allocation | Not Met | Full | N/A | AWS does not disclose non-foundational list; Azure does not use cost-based allocation |
| **REPORTING** | | | | |
| Report with ≤1 month lag | Full | Full | Full | All three now comply |
| Full historical recasting on methodology change | Full | Full | Partial | Azure: 12-month window only |
| Retain ≥3 years of data | Full | Full | Not Met | Azure: 12 months only |
| Provide programmatic API access | Not Met | Full | Full | AWS has no API |
| **VERIFICATION** | | | | |
| Formal third-party assurance (all material categories) | Partial | Not Met | Partial | No provider covers all categories |
| Disclose verification standard and assurance level | Not Met | Partial | Partial | AWS does not disclose standard/level |
| Verify tool implementation (not just methodology) | Not Met | Not Met | Not Met | None of the three |
| **TRANSPARENCY** | | | | |
| Publish full methodology documentation | Partial | Full | Partial | GCP most transparent |
| Publish materiality assessment for excluded categories | Not Met | Not Met | Not Met | None of the three |
| Reconcile customer tool with corporate GHG disclosure | Not Met | Partial | Not Met | Azure has known discrepancy |

---

## 14. Summary Comparison Table

| Dimension | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Overall approach** | Usage with economic fallback | Physical measurement internally; usage at customer boundary | LCA + usage |
| **Scope 1 coverage** | Full | Full | Full (usage allocation) |
| **Scope 2 granularity** | Monthly | Hourly (internal) / Monthly (customer) | Monthly |
| **Scope 3 category count** | 4 of 15 | 3–4 of 15 | 2 of 15 |
| **Building embodied carbon** | Yes (Oct 2024) | Yes | No |
| **End-of-life hardware** | No | No | Yes (with error) |
| **Allocation method** | Usage (foundational) + economic fallback | Physical measurement internally; usage at customer level (vCPU-hours × price-derived factor) + proportional proxy for non-electricity Scope 3 | Usage (customer usage factor; parameters undisclosed) |
| **Equipment lifetime flaw** | None | None | Critical (zero after 6 yr) |
| **Reporting delay** | ≤21 days | ~15 days | ~15 days |
| **Historical recasting** | Full (to Jan 2020) | Full (unlimited) | 12-month window |
| **Data retention** | 38 months | Unlimited | 12 months |
| **API access** | No | Yes (BigQuery) | Yes (Fabric/Power BI) |
| **Third-party verification** | Limited (Cat. 2/3/4 only) | Academic review only | Limited (methodology doc) |
| **Service granularity** | 200+ services | Per SKU | Service categories |
| **Temporal granularity** | Monthly | Monthly (hourly internal) | Monthly |
| **Methodology transparency** | Partial | Full | Partial |
| **GHG Protocol alignment** | Partial | Strong | Partial (improved from prior characterization; limited by undisclosed parameters) |

---

## 15. Key Cross-Cutting Observations

**1. No provider achieves comprehensive GHG Protocol compliance.** All three providers have significant gaps in Scope 3 category coverage, and none offers end-to-end independent verification of their customer-facing tools. The gaps are different in nature: AWS's primary gap is opacity (undisclosed non-foundational services, undisclosed verification scope); GCP's primary gap is scope (end-of-life hardware excluded, sub-monthly data not exposed, 4-year vs. actual lifetime mismatch); Azure's primary gap is methodology (undisclosed allocation parameters, 6-year cutoff error, 12-month retention).

**2. The GHG Protocol is under-specified for cloud contexts.** Several of the most consequential methodological differences between providers — allocation of shared infrastructure, equipment lifetime assumptions, building embodied carbon inclusion, EAC temporal matching — arise from areas where the GHG Protocol does not provide cloud-specific guidance. These are areas of legitimate interpretive divergence, not clear violations. A gold standard for cloud carbon accounting must resolve these ambiguities.

**3. Verification claims are narrower than they appear.** All three providers make verification claims that are technically accurate but potentially misleading. AWS's "third-party verified" claim covers only 3 of 15 Scope 3 categories, excludes Scope 1, and does not cover the most recent methodology expansion. Azure's WSP USA review covers a methodology document, not the tool. GCP's Fraunhofer review covers LCA methodology, not the customer tool. No provider has had its full customer-facing tool independently audited.

**4. All three providers use usage allocation at the customer level; Azure's parameters are undisclosed.** GCP measures power physically internally (machine-level telemetry) but the customer-facing step distributes energy by price-proportional SKU factors and resource-time (vCPU-hours), making it usage-based at the customer boundary. AWS foundational uses instance-hours (usage). Azure describes a usage-factor approach ("relative Azure usage per datacenter region") for all emission types — also usage-based. The key differences are transparency (GCP published its full methodology; AWS and Azure have not) and what the usage unit captures (GCP: vCPU-hours per SKU; AWS: instance-hours per service; Azure: undisclosed usage factor per region). None reflects CPU utilization in the customer-reported number.

**5. Azure's 6-year equipment lifetime cutoff is a unique methodological error.** This is not a gap (a missing category) but an error (an incorrect calculation). It creates a systematic underestimation of Scope 3 embodied carbon for long-lived equipment and a perverse incentive against hardware lifetime extension. It is the only clear methodological error (as opposed to gap) identified across the three providers.

**6. GCP has the most transparent and granular methodology but the physical signal does not reach customers.** GCP's internal machine-level power monitoring is best-in-class. Its hourly Electricity Maps integration is best-in-class for Scope 2. It includes building embodied carbon in the customer tool (alongside AWS), which is best practice. However, the customer-facing allocation step distributes energy across SKUs using price-based proportionality and allocates to customers by resource-time (vCPU-hours), making it usage-based at the customer boundary — the same category as AWS foundational and Azure (Schneider & Mattia 2024, §3.6.1). CPU utilization is not reflected in the customer-reported number. GCP also excludes end-of-life hardware and operational waste — categories that AWS includes. GCP's 4-year amortization assumption (vs. AWS's 6-year) also means higher reported annual embodied carbon per asset.

**7. AWS has the broadest Scope 3 coverage but the most opaque allocation.** AWS and GCP both include building embodied carbon. AWS is the only provider to also include non-IT equipment, operational waste, and a more complete upstream transport scope. But its economic allocation fallback for non-foundational services — affecting an undisclosed proportion of total emissions — is the largest single source of opacity in any of the three tools.

**8. CPU utilization is invisible to all three customer-facing methodologies.** All three providers use usage allocation at the customer level: GCP (vCPU-hours), AWS foundational (instance-hours), Azure (usage time). A VM running idle and a VM at full load report the same carbon for the same duration and SKU. Only reducing resource-time (turning off VMs, right-sizing, running for less time) moves the reported number. This is the most important practical finding for users trying to reduce their reported footprint through compute efficiency.

---

## 16. References

1. AWS Customer Carbon Footprint Tool Methodology PDF (2024/2025) — https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology.pdf
2. AWS CCFT Methodology Assurance Statement — Apex Companies LLC (2024) — https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf
3. AWS CCFT Release Notes — https://docs.aws.amazon.com/ccft/latest/releasenotes/what-is-ccftrn.html
4. Google Cloud Carbon Footprint Methodology — https://cloud.google.com/carbon-footprint/docs/methodology
5. Schneider, I. & Mattia, T. (2024). Carbon Accounting in the Cloud. arXiv:2406.09645 — https://arxiv.org/abs/2406.09645
6. Google Cloud Carbon Footprint Release Notes — https://cloud.google.com/carbon-footprint/docs/release-notes
7. Azure Emissions Calculation Methodology — https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology
8. Microsoft Scope 3 Emissions Methodology Whitepaper (2021) — https://download.microsoft.com/download/7/...
9. Microsoft Cloud Hardware Emissions Methodology (CHEM) Whitepaper (2026) — https://datacenters.microsoft.com/wp-content/uploads/...
10. GHG Protocol Corporate Standard — https://ghgprotocol.org/corporate-standard
11. GHG Protocol Scope 3 Standard — https://ghgprotocol.org/scope-3-standard
12. GHG Protocol Scope 2 Guidance — https://ghgprotocol.org/scope_2_guidance
13. Bhagavathula et al. (2024). Understanding Implications of Uncertainty in Embodied Carbon Models. HotCarbon 2024.
14. Lyu et al. (2023). Myths and Misconceptions Around Reducing Carbon Embedded in Cloud Platforms. HotCarbon 2023.
15. Simon et al. (2024). BoaviztAPI: A Bottom-Up Model to Assess Environmental Impacts of Cloud Services. HotCarbon 2024.
