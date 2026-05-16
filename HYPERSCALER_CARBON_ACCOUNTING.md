# Cloud Carbon Accounting Methodology Comparison: AWS, Google Cloud, Azure
## Agent-Ready Technical Reference — IaaS/PaaS Focus

Based on:
- AWS Customer Carbon Footprint Methodology, Model 3.0 (October 2025): https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-methodology.pdf
- Google Carbon Footprint reporting methodology: https://docs.cloud.google.com/carbon-footprint/docs/methodology
- Azure emissions calculation methodology (updated January 2026): https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology

**Scope:** IaaS and PaaS only. Microsoft 365 and other SaaS products are excluded.
**Sources:** AWS CCFT Methodology PDF (Model 3.0, Oct 2025), Apex Companies LLC Assurance Statement (Oct 2025, ISO 14064-3:2019, limited assurance, ±5% materiality), Google Cloud Carbon Footprint Methodology Docs, Schneider & Mattia arXiv:2406.09645, Azure Emissions Calculation Methodology (Microsoft Learn, updated January 2026), Microsoft Scope 3 Whitepaper (2021), Microsoft Cloud Hardware Emissions Methodology (CHEM) Whitepaper (2026), Azure Carbon Optimization Docs (2025), GHG Protocol Corporate / Scope 3 / Scope 2 Standards, HotCarbon 2024 papers.
**Last updated:** May 2026

---

## 1. Tool Overview

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Tool name** | Customer Carbon Footprint Tool (CCFT) | Google Cloud Carbon Footprint | Emissions Impact Dashboard (EID); Carbon Optimization (Azure portal + REST API) |
| **Launched** | March 2022 (CCFT) | October 2021 (Carbon Footprint, GA) | January 2020 (as Microsoft Sustainability Calculator; renamed Emissions Impact Dashboard later) |
| **Scope 3 added** | April 2024 (Cat. 2 IT hardware); expanded Oct 2025 in Model 3.0 (Cat. 2 buildings + non-IT, Cat. 3 FERA, Cat. 4 upstream transport) | 2021 (embodied carbon from launch) | 2021 (methodology whitepaper) |
| **Primary calculation approach** | Usage allocation for foundational services (instance-hours); economic (revenue) fallback for non-foundational services | Two-stage: physical machine-level power telemetry internally → usage allocation at customer boundary (vCPU-hours × price-derived SKU factor) | LCA-based embodied carbon (CHEM) + usage allocation via customer usage factors per datacenter region |
| **Claimed GHG standard** | GHG Protocol Corporate + Scope 3 | Same | Same |
| **Third-party verified** | Yes — limited assurance | No — academic critical review only | Yes — limited scope |
| **Verifier** | Apex Companies, LLC (ISO 14064-3:2019, limited, ±5% materiality) | Fraunhofer IZM (ISO 14040/14044 critical review) | WSP USA |
| **Verification scope** | Model 3.0 methodology incl. Scope 3 Cat. 2, 3, 4; Scope 1 and Scope 2 not in CCFT assurance boundary | LCA methodology for hardware embodied carbon only; customer tool not audited | Scope 3 methodology document only; tool implementation not audited |
| **Reporting delay** | ≤21 days (as of Dec 2025; previously ~3 months) | ~15 days | ~19 days |
| **Historical data retention** | 38 months | Unlimited (BigQuery export) | 12 months (Carbon Optimization); up to 60 months (EID via Power BI) |
| **Historical recasting on methodology change** | Full recast to January 2020 | Full recast capability via BigQuery | 12-month window only |
| **API / programmatic access** | No | Yes (BigQuery export) | Yes (Microsoft Fabric / Power BI for EID; REST API for Carbon Optimization) |
| **Service coverage** | 200+ services | All GCP services (per SKU per region) | Major Azure IaaS/PaaS services |
| **Additional capabilities** | — | — | Carbon Optimization: resource_group × resource granularity + AI-driven reduction recommendations via Azure Advisor with estimated carbon and cost savings |

---

## 2. Scope 1 Emissions

All three include Scope 1. Sources for cloud data centers: stationary combustion (diesel backup generators, gas boilers), fugitive refrigerant emissions, mobile combustion (fleet).

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Stationary combustion** | Yes | Yes | Yes |
| **Fugitive refrigerants** | Yes | Yes | Yes |
| **Mobile combustion (fleet)** | Unclear | Yes | Yes (doc lists "stationary and mobile combustion") |
| **Allocation to customers** | Usage (described as physical) | Usage at customer level (physical measurement internally) | Usage (customer usage factors per region) |
| **Scope 1 independently verified** | Not in CCFT assurance boundary | No | No |

**GHG Protocol position:** Corporate Standard requires all owned/controlled combustion and fugitive sources — all three comply on coverage. GHG Protocol prefers physical allocation; all three use usage allocation at the customer level. GCP measures power physically internally but distributes by resource-time at the customer step; AWS describes its method as physical without disclosing whether customer-level utilization is reflected; Azure uses a usage-factor approach with parameters not fully disclosed.

---

## 3. Scope 2 Emissions

All three report both location-based (LBM) and market-based (MBM), as required by GHG Protocol Scope 2 Guidance (2015).

| Attribute | AWS | Google Cloud | Azure |
|---|---|---|---|
| **LBM / MBM** | Yes / Yes | Yes / Yes | Yes / Yes |
| **LBM emission factor source** | Regional grid operators; IEA fallback | Electricity Maps API (hourly); IEA annual fallback | Regional grid operators; IEA fallback |
| **LBM temporal granularity** | Monthly | Hourly (internal); monthly (customer-facing) | Monthly |
| **MBM instrument** | Energy Attribute Certificates (EACs) | PPAs + EACs | PPAs |
| **EAC/PPA temporal matching** | Not disclosed (likely annual) | Hourly CFE % reported per region | Not disclosed |
| **EAC/PPA spatial matching** | Not disclosed | Region-level | Not disclosed |

**Key differences:** GCP's hourly Electricity Maps data captures intra-day grid variation that monthly factors average out; GCP is the only provider reporting hourly CFE percentages per region. AWS and Azure do not disclose EAC/PPA matching methodology, suggesting likely annual matching. Hourly, location-matched matching is best practice per GHG Protocol Scope 2 Technical Guidance and GSF Real-Time Energy and Carbon Standard.

---

## 4. Scope 3 Emissions — Category Coverage

GHG Protocol Scope 3 defines 15 categories. The materially relevant ones for cloud providers are Cat. 2 (Capital Goods), Cat. 3 (FERA), Cat. 4 (Upstream Transport), Cat. 5 (Waste), Cat. 6 (Business Travel), Cat. 7 (Employee Commuting).

| GHG Protocol Scope 3 Category | AWS | GCP | Azure | Notes |
|---|---|---|---|---|
| **Cat. 1: Purchased Goods & Services** | N/A | N/A | ✅ Full | Azure lists Cat. 1 (raw material extraction); N/A for AWS/GCP |
| **Cat. 2: IT Hardware** | ✅ Full | ✅ Full | ✅ Full | All amortize; lifetime assumptions in §6. Azure CHEM covers rack, disk drive, server blades, FPGA, PSU, other |
| **Cat. 2: Buildings (embodied)** | ✅ Full (Model 3.0, Oct 2025) | ✅ Full | ❌ Excluded | Azure: "might add as data becomes available" |
| **Cat. 2: Non-IT infrastructure (UPS, cooling)** | ✅ Full (Model 3.0) | ⚠️ Partial | ❌ Excluded | |
| **Cat. 3: FERA** | ✅ Full | ✅ Full | ❌ Excluded | Azure lists categories 1, 2, 4, 5, 9, 12 — Cat. 3 not included |
| **Cat. 4: Upstream Transport** | ✅ Full (Model 3.0) | ⚠️ Partial | ✅ Full | Azure: manufacturer → datacenter dock |
| **Cat. 5: Waste** | ❌ Excluded | ❌ Excluded | ✅ Full | |
| **Cat. 6: Business Travel** | ❌ Excluded | ✅ Full | ❌ Excluded | GCP only |
| **Cat. 7: Employee Commuting** | ❌ Excluded | ✅ Full | ❌ Excluded | GCP only |
| **Cat. 9: Downstream Transport** | ❌ Excluded | ❌ Excluded | ✅ Full | Azure: datacenter → recycler |
| **Cat. 12: End-of-Life Treatment** | ❌ Excluded | ❌ Excluded | ✅ Full | Azure: recycling, landfill, composting |
| **Cat. 8, 10, 11, 13–15** | N/A | N/A | N/A | Not material for cloud providers |

**Approximate category counts:**
- **AWS:** 3 categories (Cat. 2 full incl. buildings + non-IT, Cat. 3, Cat. 4)
- **GCP:** 4 categories (Cat. 2 full incl. buildings, Cat. 3, Cat. 6, Cat. 7)
- **Azure:** 6 categories (Cat. 1, 2, 4, 5, 9, 12) — broadest count, but excludes FERA and buildings

**GHG Protocol position:** The standard requires all material categories. Cat. 2 is unambiguously material and required; Cat. 3–7 are likely material for hyperscale operators. The standard allows exclusions with justification, but none of the three providers publishes a materiality assessment for its excluded categories.

---

## 5. Allocation Methodology

Allocation determines how data-center-level emissions are attributed to customer workloads — the most technically consequential methodological choice.

### 5.1 AWS — Usage Allocation with Economic Fallback

**Tier 1 (foundational services — defined in Model 3.0 as "AWS services that have dedicated server racks in AWS data centers"):** Described as physical allocation based on resource utilization (CPU, memory, storage I/O, network). At the customer level the unit is instance-hours — usage allocation. Whether internal utilization telemetry feeds the per-instance-hour factor is not publicly disclosed.

**Tier 2 (non-foundational services):** Per the Model 3.0 methodology document, non-foundational services are defined as "AWS services with no dedicated server racks, which rely on foundational services to provide functionality to end customers." Allocated by **equivalent revenue** — defined in the methodology as "a standardized measure of usage-based revenue that excludes pricing variation factors such as discounts, and other adjustments." Revenue is used as a proxy for resource consumption.

**Critical transparency gap:** The Model 3.0 methodology document defines the foundational vs. non-foundational distinction but **does not publish an explicit list of which AWS services fall into each category.** It mentions EC2, S3, EBS, Lambda, and SageMaker by name as covered services without classifying them. The share of total CCFT emissions subject to economic allocation is also not disclosed. Revenue is a poor proxy for resource consumption — a high-margin service can be allocated more emissions despite consuming fewer resources.

### 5.2 GCP — Two-Stage Allocation

**Stage 1 (internal, physical):** Machine-level power monitoring via Borg telemetry. Each machine's power is decomposed into dynamic power (workload-driven, allocated proportional to GCU — Google Compute Unit — usage) and idle power (allocated by resource-weighted shares of GCU, RAM, etc.). Idle power is approximately 60% of average server energy consumption (Schneider & Mattia 2024, citing prior work). Shared internal services (e.g., Cloud Storage built on Blobstore/Colossus) are reallocated to end-user teams.

**Stage 1.5 (cost-based fallback for shared services):** Where shared internal services lack sufficient usage data, GCP reallocates energy by back-charged internal costs ("cost-based approach... typically less desirable than a resource-based approach"). Implemented as two rounds of reallocation. Affected service set and emission fraction not disclosed.

**Stage 2 (customer-facing, price-proportional):** Each internal team's energy is distributed across customer-facing SKUs by a formula in which energy per usage unit is **proportional to list price** (commitment, committed-use, and sustained-use discounts excluded). Customers are then allocated by usage units (vCPU-hours for Compute Engine, GiB-months for storage, etc.). The paper explicitly notes (§3.6): "One limitation of this approach is that customers do not receive a signal about how switching from SKU A to SKU B can reduce their actual emissions, but rather their allocated emissions based on list prices."

**Non-electricity Scope 3 (embodied, FERA, transport):** Per the Carbon Footprint documentation, allocated by proportional ratio of customer electricity to total GCP electricity — i.e., assumes non-electricity emissions track electricity consumption.

**Strengths:** Internal machine-level telemetry (the only published example among the three providers); the two-stage methodology (Schneider & Mattia 2024) is fully documented. **Weakness:** Customer-facing allocation does not reflect actual compute utilization — only resource-time scaled by list price; proportional non-electricity allocation may not match distribution across workload mixes (e.g., GPU AI vs. CPU compute).

### 5.3 Azure — Usage Allocation (Normalized Cost Metric)

Azure uses usage allocation via customer usage factors per datacenter region, consistent across Scope 1, 2, and 3. The underlying definition of "usage" has evolved:

- **2021 Whitepaper:** Azure usage is "the normalized cost metric associated with IaaS, PaaS or SaaS... normalized to exclude discounts and other variables." This is closer to economic allocation than the term "usage" suggests.
- **2025 Carbon Optimization docs:** Usage is described as "compute, storage, and data transfer" time — implying resource-time allocation.

It is unclear whether this is a methodology evolution or different terminology for the same approach. The internal derivation of the usage factor is not disclosed, limiting independent verification. (The CHEM 2026 whitepaper notes that Microsoft "shifted from financial proxies to pLCA" for *embodied carbon* modeling — a separate methodology track from customer-level allocation.)

**Methodology pipeline (2021 Whitepaper, 8 stages):**
1. **Component LCA:** Material Circularity and Life Cycle Carbon Emission Calculator v7.3 applied to components (rack, disk drive, server blades, FPGA, PSU, other)
2. **Datacenter aggregation**
3. **Region aggregation**
4. **Customer usage calculation:** Normalized cost metric per customer per region
5. **Region emission factors applied**
6. **M365 usage factors** (SaaS — excluded from this document's scope)
7. **Customer emissions:** Combine steps 4–6
8. **Combine Scope 1 + 2 + 3** into total customer emissions

**Two customer-facing tools:**
- **Emissions Impact Dashboard (EID):** subscription × service × region, up to 5-year retention, Power BI / Microsoft Fabric
- **Carbon Optimization:** resource_group × resource, 12-month retention, Azure portal + REST API, AI-driven reduction recommendations via Azure Advisor

### 5.4 Allocation Comparison Table

| Dimension | AWS | GCP | Azure |
|---|---|---|---|
| **Internal method** | Described as physical (foundational) | Physical (machine-level power telemetry, GCU-proportional) | Not disclosed |
| **Customer-facing method** | Usage (foundational: instance-hours); economic (non-foundational: revenue) | Usage (vCPU-hours × price-derived energy factor per SKU) | Usage (normalized cost metric per 2021 whitepaper; compute/storage/data-transfer time per 2025 docs) |
| **Fallback method** | Economic (non-foundational) | Cost-based (internal shared services); proportional ratio (non-electricity Scope 3) | Not disclosed |
| **Granularity** | Service + region + account | SKU + region + project | Service category + region + subscription |
| **Compute utilization reflected** | No | No | No |
| **Allocation parameters disclosed** | Partial | Full (Schneider & Mattia 2024) | Partial (usage factor definition undisclosed) |

**GHG Protocol alignment at customer boundary:** All three are usage-based — GCP by vCPU-hours per SKU, AWS foundational by instance-hours per service, Azure by usage time per region. GCP measures power physically internally but introduces price-based proportionality at the customer step (Schneider & Mattia 2024, §3.6). Without full disclosure of per-instance-hour or usage-factor derivations, precise GHG Protocol alignment cannot be confirmed for any provider.

---

## 6. Equipment Lifetime and Embodied Carbon

### 6.1 Default Lifetime Assumptions

| Provider | IT Hardware | Building | End-of-Life | LCA Boundary |
|---|---|---|---|---|
| **AWS** | 6 years | 50 years | Excluded | Cradle-to-gate |
| **GCP** | **4 years** | Included in customer tool | Excluded | Cradle-to-gate |
| **Azure** | 6 years | Excluded from customer tool | Included (CHEM) | Cradle-to-grave |

GCP's 4-year assumption produces **50% higher** annual amortized embodied carbon than 6-year for the same hardware (6/4 = 1.5). GCP acknowledges this is a financial accounting convention and that real lifetimes are longer. The GHG Protocol does not specify a required lifetime.

### 6.2 Post-Amortization Treatment

All three report **zero amortized embodied carbon** for equipment beyond its assumed lifetime. AWS's methodology specifies that hardware past its planned retirement contributes zero, justified as avoiding overallocation/double counting. GCP states: "dropping those at the 4-year mark." Azure EID behaves identically at 6 years.

Total embodied carbon is fully allocated over the amortization period, but in any given month, equipment past its window contributes zero — so fleet-wide monthly Scope 3 decreases as equipment ages past the assumed lifetime.

### 6.3 LCA Methodology

| Provider | Approach | Source | Verification |
|---|---|---|---|
| **AWS** | "Component-level hybrid LCA" waterfall (Model 3.0): (1) Process-based LCA with engineering attributes (PLCA-Eng); (2) ML-based interpolation/extrapolation from PLCA data points (Extrap.); (3) Representative Category Average LCA with K-Nearest-Neighbors classification (RCA-LCA); (4) Component-level EIO-LCA (cost-based) fallback. Data sources: supplier primary data, ecoinvent, GaBi, imec.netzero, USEEIO, TechInsights | Component BOMs + EMT attributes | Apex (limited, ISO 14064-3:2019) |
| **GCP** | Component-level LCA | Internal LCA + Fraunhofer IZM review | Fraunhofer IZM critical review (ISO 14040/14044) |
| **Azure** | Process-based LCA via CHEM; integrates Microsoft PDM/FMD data + automated material-to-LCI mapping (Makersite); semiconductor data from imec SSTS; ecoinvent LCI database; AI-augmented proxy selection (CHEM whitepaper 2026) | CHEM | WSP USA (methodology document only) |

AWS's pathway selection is based on materiality and data availability — components with primary data go through PLCA-Eng; long-tail/low-frequency components fall back to RCA-LCA or Comp-EIO-LCA (cost-based, using NAICS sector emission factors). The fleet proportion relying on each pathway is not disclosed. AWS amortizes data center buildings over 50 years; a 30-year assumption would raise annual building embodied carbon by ~67% (50/30) — arithmetic identity, not an empirical estimate.

---

## 7. Key Variables and Update Cadence

Sources and cadence are drawn directly from each provider's methodology documentation. (Quantitative uncertainty ranges per variable are not published by any provider and are not included here.) For context on embodied-carbon model variance, Bhagavathula et al. (HotCarbon 2024) report variations as much as **1.5× across iMec process-node assessments published in different years** and **>4× across 94 published SSD embodied-carbon LCAs** (the latter compiled by Tannu & Nair).

### 7.1 AWS Variables

| Variable | Source | Update | Recast |
|---|---|---|---|
| Energy consumption (MWh) | Utility meters | Monthly | Yes |
| LBM emission factor | Regional grid; IEA | Annual | Yes |
| MBM emission factor | EACs | Annual | Yes |
| Service allocation — foundational | Internal telemetry | Monthly | Yes |
| **Service allocation — non-foundational** | Internal revenue data | Not disclosed | Unknown |
| Embodied carbon — IT (PLCA-Eng / Extrap.) | Component BOMs + EMT attributes; imec.netzero, ecoinvent, GaBi | Methodology updates | Yes |
| Embodied carbon — IT (RCA-LCA / Comp-EIO-LCA fallback) | Mass + KNN classification; NAICS sector emission factors | Methodology updates | Yes |
| Embodied carbon — buildings | Engineering assessments | Infrequent | Yes |
| Lifetime — IT (6 yr) / buildings (50 yr) | Internal assumption | Rarely | Yes |

### 7.2 GCP Variables

| Variable | Source | Update | Recast |
|---|---|---|---|
| Machine-level power | Borg hardware telemetry | Continuous | Yes |
| Grid factor — Electricity Maps | Electricity Maps API | Hourly | Yes |
| Grid factor — IEA fallback | IEA annual | Annual | Yes |
| CFE % | Electricity Maps; PPAs | Hourly | Yes |
| SKU-level carbon intensity | Internal telemetry | Monthly | Yes |
| Non-electricity Scope 3 ratio | Internal electricity data | Monthly | Yes |
| Embodied carbon — IT | Internal LCA + Fraunhofer IZM | LCA updates | Yes |
| Lifetime — IT (4 yr) | Internal assumption | Rarely | Yes |

### 7.3 Azure Variables

Reporting delay: ~19 days; retention: 12 months (Carbon Optimization) / 60 months (EID).

| Variable | Source | Update | Recast |
|---|---|---|---|
| Hardware LCA factor | CHEM (pLCA + Makersite + imec SSTS + ecoinvent) | CHEM updates | Yes (12-mo) |
| Lifetime — IT (6 yr default) | Internal assumption | Rarely | Yes (12-mo) |
| **Usage factor** | 2021: "normalized cost metric"; 2025 docs: "compute/storage/data-transfer time" | Monthly | Yes (12-mo) |
| Regional electricity factor | Regional grid; IEA | Annual | Yes (12-mo) |
| End-of-life disposition | Microsoft programs | CHEM updates | Yes (12-mo) |

---

## 8. Reporting Delays and Recasting

| Provider | Current | Previous | Change |
|---|---|---|---|
| **AWS** | ≤21 days (Dec 2025) | ~3 months | Major improvement |
| **GCP** | ~15 days | ~1 month | Moderate |
| **Azure** | ~19 days | ~1 month | Moderate |

All three providers now offer sub-month reporting delays.

| Provider | Recast Scope | Trigger | Retention |
|---|---|---|---|
| **AWS** | Recast to January 2020 | "At least annually upon completion of third-party assurance of Amazon's footprint or when significant methodology updates are introduced" (Model 3.0 §1) | 38 months |
| **GCP** | Full historical | Methodology changes; manual via BigQuery | Unlimited (BigQuery) |
| **Azure** | 12-month window only | Methodology changes | 12 months (Carbon Optimization) / 60 months (EID) |

AWS recasts all data back to January 2020 (best practice — the April 2024 Scope 3 addition and October 2025 Model 3.0 expansion were both applied retroactively). GCP's Electricity Maps integration (2022) was retroactively applied. Azure's 12-month recasting window prevents GHG Protocol-aligned base year recalculation for any change affecting older data; the EID's 5-year retention mitigates trend-analysis concerns but not the recast scope itself.

---

## 9. Spatial, Temporal, and Service Granularity

| Provider | Regions | Sub-Regional | Customer Temporal | Internal Temporal | Service Granularity |
|---|---|---|---|---|---|
| **AWS** | ~30+ | No | Monthly | Unknown | Per service × region × account (200+ services) |
| **GCP** | ~40+ | No (hourly CFE per region only) | Monthly | Hourly | Per SKU × region × project |
| **Azure** | ~60+ | No | Monthly | Unknown | Per service category × region × subscription |

No provider offers sub-regional (AZ or DC-level) granularity. All three expose only monthly data to customers. GCP calculates internally at hourly resolution but aggregates to monthly — a systemic gap, since carbon-aware computing requires sub-hourly granularity.

---

## 10. Third-Party Verification — Detailed Assessment

### 10.1 AWS — Apex Companies, LLC

Apex conducted an independent assurance engagement of the Model 3.0 (October 2025) methodology.
- **Standard:** ISO 14064-3:2019
- **Assurance level:** Limited
- **Materiality threshold:** ±5% for aggregate errors in sampled data
- **Criteria:** WRI/WBCSD GHG Protocol Corporate Standard, Scope 2 Guidance, Scope 3 Standard; ISO 14064-1:2018
- **Scope covered:** Scope 3 Cat. 2 (Capital Goods — IT hardware, buildings, non-IT), Cat. 3 (FERA), Cat. 4 (Upstream Transport)
- **Outside CCFT scope (not verified, but also not reported in CCFT):** fleet vehicles, AWS warehouses and manufacturing facilities, offices, customer-facility sites (Outposts, etc.), other Scope 3 categories AWS does not report
- **Lead verifier:** Trevor A. Donaghu; **technical reviewer:** Mary E. Armstrong-Friberg

**Assessment:** The Model 3.0 methodology is independently verified at a limited-assurance level — meaningfully weaker than reasonable assurance. The verified scope matches the reported scope (the categories AWS reports are the categories Apex verified). The standard, level, materiality, and verifiers are all disclosed in the assurance letter. The primary legitimate critique is that limited assurance uses negative-form language ("nothing has come to our attention to indicate...") rather than positive confirmation — adequate but not the strongest available level.

### 10.2 GCP — Fraunhofer IZM Critical Review

Fraunhofer IZM conducted a critical review of GCP's hardware embodied carbon LCA per ISO 14040/14044.
- **Review type:** Academic critical review — not formal third-party GHG assurance
- **Covered:** LCA methodology for hardware embodied carbon
- **Not covered:** Customer tool accuracy, data pipelines, allocation calculations, Scope 1, Scope 2, non-electricity Scope 3

**Assessment:** Methodologically rigorous for what it covers, but not equivalent to ISO 14064-3 GHG assurance. There is no independent audit confirming that the customer-facing tool reflects the underlying methodology. GCP is the only provider with no formal GHG assurance engagement.

### 10.3 Azure — WSP USA

WSP USA reviewed Azure's Scope 3 methodology.
- **Covered:** Scope 3 methodology document
- **Not covered:** Scope 1, Scope 2, tool implementation accuracy, data pipelines
- **Standard:** Not fully disclosed; aligned with GHG Protocol principles

**Assessment:** Covers the methodology document but not the tool implementation. Provides assurance that the stated methodology is GHG Protocol-aligned, not that the tool correctly implements it.

### 10.4 Comparative Summary

None of the three offers comprehensive end-to-end verification of their customer-facing tool implementation.

| Verification Dimension | AWS | GCP | Azure |
|---|---|---|---|
| Formal GHG assurance engagement | Yes (ISO 14064-3:2019, limited) | No | Yes |
| Scope 1 verified | Not in CCFT boundary | No | No |
| Scope 2 verified | Not in CCFT boundary | No | No |
| Scope 3 Cat. 2 (IT hardware + buildings + non-IT) verified | Yes | LCA review only | Yes (methodology doc) |
| Scope 3 Cat. 3 (FERA) verified | Yes | No | N/A (excluded) |
| Scope 3 Cat. 4 (Transport) verified | Yes | No | Yes (methodology doc) |
| Tool implementation verified | No | No | No |
| Verification standard disclosed | Yes (ISO 14064-3:2019) | ISO 14040/14044 | Partial |
| Assurance level disclosed | Yes (limited) | N/A | Partial |

---

## 11. GHG Protocol Compliance Analysis

### 11.1 Areas of Clear Compliance

All three providers comply with: reporting both LBM and MBM Scope 2; including Scope 1 stationary combustion and fugitive emissions; using GHG Protocol-aligned system boundaries and emission factor sources. AWS and GCP include FERA (Cat. 3); Azure does not.

### 11.2 Clear Divergences

| Issue | Provider | GHG Protocol Requirement | Provider Practice | Severity |
|---|---|---|---|---|
| Allocation parameters undisclosed | AWS, Azure | Physical allocation preferred; parameters verifiable | AWS: non-foundational economic; Azure: usage-factor parameters undisclosed | Medium |
| Historical recasting window | Azure | Recast base year on methodology change | 12-month window only | High |
| Scope 3 material categories excluded | All | Include all material categories | Significant gaps (§4) | High |
| Materiality assessment not disclosed | All | Justify exclusions with materiality assessment | None published | Medium |

### 11.3 Under-Specified GHG Protocol Areas

Where the standard does not fully specify the correct approach:

| Under-Specified Area | AWS | GCP | Azure |
|---|---|---|---|
| Allocation of shared cloud infrastructure | Usage (foundational) + economic fallback (non-foundational) | Physical internally; usage at customer boundary (vCPU-hours × price factor); proportional ratio for non-electricity Scope 3 | Normalized cost metric (2021) / compute-storage-data-transfer time (2025); undisclosed |
| Equipment lifetime | 6 yr (IT); 50 yr (buildings) | 4 yr (IT, financial accounting) | 6 yr (IT) |
| EAC/PPA temporal matching | Not disclosed | Hourly CFE reported | Not disclosed |
| Building embodied carbon | Included (Model 3.0) | Included | Excluded |
| End-of-life hardware | Excluded | Excluded | Included |
| Business travel and commuting | Excluded | Included | Excluded |
| Idle capacity allocation | Not disclosed | Proportionally allocated | Not disclosed |

---

## 12. Weaknesses and Methodological Gaps

### 12.1 AWS

**Critical:**
1. **Economic allocation fallback for non-foundational services.** Equivalent-revenue allocation applied to "AWS services with no dedicated server racks" (Model 3.0 definition). The methodology document does **not publish the list of services classified as non-foundational**, nor the share of total CCFT emissions allocated this way. Revenue is a poor proxy for resource consumption — a high-margin service can be allocated more emissions despite consuming fewer resources. This is the largest source of opacity in CCFT.

**High:**
2. **Cost-based EIO-LCA fallback for embodied carbon.** When primary data, parametric models, and mass-based representative LCA are all unavailable, AWS falls back to Component-level EIO-LCA — sector-level emission factors (kgCO2e/$) from NAICS codes multiplied by component cost. This is a cost-based proxy, not a physical measurement. The fleet proportion relying on each of the four LCA pathways is not disclosed.
3. **Limited (vs. reasonable) assurance.** Apex's engagement is limited assurance — adequate but the weaker available level. Negative-form conclusion language ("nothing has come to our attention").
4. **Business travel and employee commuting excluded.** Cat. 6 and 7 excluded; no materiality assessment justifying exclusion.
5. **Allocation methodology opacity.** Foundational vs. non-foundational classification criteria and revenue data for economic allocation not publicly disclosed — replication impossible.

**Medium:**
6. **50-year building amortization may understate annual carbon.** A 30-year assumption would raise annual building embodied carbon by ~67% (50/30 arithmetic).
7. **Monthly-only customer-facing granularity.**
8. **EAC matching not disclosed** — likely annual, overstating renewable energy impact vs. hourly location-matched matching.

### 12.2 GCP

**Critical:**
1. **End-of-life hardware excluded from customer tool.** Methodology is cradle-to-gate; end-of-life emissions of hardware and buildings are explicitly excluded per the GCP methodology document.

**High:**
2. **Non-electricity Scope 3 uses simplified proportional allocation.** Customer-electricity / total-electricity ratio applied to all non-electricity Scope 3 (embodied, FERA, transport). May not hold for GPU AI vs. CPU workloads.
3. **No formal third-party GHG assurance of customer tool.** Fraunhofer review covers LCA methodology only.
4. **4-year amortization shorter than real hardware life.** Financial accounting standard; GCP acknowledges actual hardware lifetimes are longer.
5. **IEA annual fallback** for regions not covered by Electricity Maps. Affected regions not disclosed.

**Medium:**
6. **Waste (Cat. 5) excluded.** No materiality assessment published.
7. **Hourly internal data not exposed to customers** — prevents customer carbon-aware optimization using provider data.

### 12.3 Azure

**Critical:**
1. **Allocation parameters undisclosed; "usage" may be a normalized cost metric.** 2021 Whitepaper defines Azure usage as a "normalized cost metric... normalized to exclude discounts and other variables" — closer to economic than physical allocation. 2025 docs describe it as "compute, storage, and data transfer" time. Unclear whether evolution or rephrasing. Internal derivation of the usage factor is not disclosed.

**High:**
2. **FERA (Cat. 3) excluded.** Azure lists categories 1, 2, 4, 5, 9, 12; FERA is omitted. Both AWS and GCP include it; FERA is typically material for energy-intensive operations.
3. **Building embodied carbon excluded.** No announced plans. Material omission for an operator with 200+ data centers.
4. **WSP USA verification does not cover customer tool accuracy.** Covers methodology document only.
5. **Methodology inconsistency with Microsoft corporate GHG disclosure (explicitly acknowledged).** The 2021 Scope 3 Whitepaper footnote 2 states: "Microsoft Cloud is exploring new methods for emissions reporting that Microsoft has not yet adopted in its corporate disclosure. The underlying methodologies and emissions findings generated from the calculator will differ from those reflected in Microsoft's corporate disclosure." Microsoft has not publicly reconciled the two numbers.
6. **12-month recasting window insufficient for GHG Protocol base year recalculation.** EID's 5-year retention mitigates trend-analysis limitation; recasting scope remains 12 months.

**Medium:**
7. **End-of-life methodology not fully transparent.** Azure includes EoL (uniquely), but specific disposition rates and calculation methodology are not disclosed.
8. **Renewable energy matching methodology not disclosed.** PPA temporal and spatial matching criteria not disclosed.

---

## 13. Gold Standard Requirements — Compliance Assessment

Status codes: **Full** = fully met; **Partial** = partially met or with caveats; **Not Met** = not met; **Unclear** = insufficient information.

| Gold Standard Requirement | AWS | GCP | Azure | Notes |
|---|---|---|---|---|
| **SCOPE 1** | | | | |
| Stationary combustion sources | Full | Full | Full | |
| Fugitive refrigerant emissions | Full | Full | Full | |
| Physical allocation to customers | Partial | Partial | Not Met | All use usage allocation at customer level |
| Independent verification of Scope 1 | Not Met | Not Met | Not Met | |
| **SCOPE 2** | | | | |
| Both LBM and MBM | Full | Full | Full | |
| Granular (sub-annual) grid factors | Partial | Full | Partial | GCP hourly; others monthly |
| EAC/PPA temporal matching disclosed | Unclear | Partial | Unclear | GCP reports hourly CFE |
| Location-matched EACs/PPAs | Unclear | Partial | Unclear | |
| **SCOPE 3 — CAPITAL GOODS (CAT. 2)** | | | | |
| IT hardware embodied carbon | Full | Full | Full | AWS/Azure 6-yr; GCP 4-yr |
| Building embodied carbon | Full | Full | Not Met | AWS added Model 3.0 (Oct 2025) |
| Non-IT infrastructure | Full | Partial | Not Met | |
| Cradle-to-grave LCA (incl. end-of-life) | Not Met | Not Met | Full | Azure only |
| Disclose lifetime assumption | Full | Partial | Partial | |
| Defensible lifetime | Full | Full | Full | All use financial-service-life amortization |
| **SCOPE 3 — FERA (CAT. 3)** | Full | Full | Not Met | |
| **SCOPE 3 — UPSTREAM TRANSPORT (CAT. 4)** | Full | Partial | Full | |
| **SCOPE 3 — WASTE (CAT. 5)** | Not Met | Not Met | Full | Azure only |
| **SCOPE 3 — DOWNSTREAM TRANSPORT (CAT. 9)** | Not Met | Not Met | Full | Azure only |
| **SCOPE 3 — END-OF-LIFE (CAT. 12)** | Not Met | Not Met | Full | Azure only |
| **SCOPE 3 — BUSINESS TRAVEL / COMMUTING (CAT. 6/7)** | Not Met | Full | Not Met | GCP only |
| **ALLOCATION** | | | | |
| Physical allocation as primary method | Partial | Partial | Partial | GCP physical internally; customer-facing price-based |
| Disclose allocation methodology and parameters | Partial | Full | Partial | GCP most transparent |
| Disclose which services use economic allocation | Not Met | Partial | N/A | AWS: non-foundational list undisclosed |
| **REPORTING** | | | | |
| ≤1 month lag | Full | Full | Full | All three comply |
| Full historical recasting | Full | Full | Partial | Azure: 12-month window |
| Retain ≥3 years | Full | Full | Partial | Azure CO 12mo / EID 60mo |
| Programmatic API | Not Met | Full | Full | AWS has no API |
| **VERIFICATION** | | | | |
| Formal third-party assurance | Partial (limited) | Not Met | Partial | |
| Disclose verification standard and level | Full | Partial | Partial | AWS: ISO 14064-3:2019, limited, ±5% |
| Verify tool implementation (not just methodology) | Not Met | Not Met | Not Met | |
| **TRANSPARENCY** | | | | |
| Publish full methodology | Partial | Full | Partial | |
| Publish materiality assessment for excluded categories | Not Met | Not Met | Not Met | |
| Reconcile customer tool with corporate GHG disclosure | Not Met | Partial | Not Met | Azure has known discrepancy |

---

## 14. Summary Comparison Table

| Dimension | AWS | Google Cloud | Azure |
|---|---|---|---|
| **Overall approach** | Usage with economic fallback | Physical internally; usage at customer boundary | LCA + usage |
| **Scope 1 coverage** | Full | Full | Full |
| **Scope 2 granularity** | Monthly | Hourly (internal) / Monthly (customer) | Monthly |
| **Scope 3 category count** | 3 of 15 (Cat. 2, 3, 4) | 4 of 15 (Cat. 2, 3, 6, 7) | 6 of 15 (Cat. 1, 2, 4, 5, 9, 12) — broadest count, excludes FERA |
| **Building embodied carbon** | Yes (Model 3.0, Oct 2025) | Yes | No |
| **End-of-life hardware** | No | No | Yes |
| **Allocation method** | Usage (foundational) + economic fallback | Physical internally; usage at customer (vCPU-hr × price factor) + proportional proxy for non-electricity Scope 3 | Usage (normalized cost metric / compute-storage-data-transfer time; parameters undisclosed) |
| **Post-amortization treatment** | Zero after 6 yr | Zero after 4 yr | Zero after 6 yr |
| **Reporting delay** | ≤21 days | ~15 days | ~19 days |
| **Recasting** | Full to Jan 2020 | Full (unlimited) | 12-month window |
| **Retention** | 38 months | Unlimited | 12 months (CO) / 60 months (EID) |
| **API** | No | Yes (BigQuery) | Yes (Fabric/Power BI; REST) |
| **Third-party verification** | Limited assurance, ISO 14064-3:2019, Cat. 2/3/4 | Academic LCA review only | Methodology document only |
| **Methodology transparency** | Partial | Full | Partial |
| **GHG Protocol alignment** | Partial | Strong | Partial |

---

## 15. Key Cross-Cutting Observations

**1. No provider achieves comprehensive GHG Protocol compliance.** All three have significant gaps in Scope 3 category coverage, and none offers end-to-end independent verification of customer-facing tool implementations. The gaps differ in nature: AWS's primary gap is allocation opacity (undisclosed non-foundational service list); GCP's is scope (end-of-life excluded, sub-monthly data unexposed, 4-yr vs. actual lifetime mismatch); Azure's is methodology (undisclosed allocation parameters, 12-month recast, FERA and buildings excluded).

**2. The GHG Protocol is under-specified for cloud contexts.** The most consequential methodological differences — allocation of shared infrastructure, equipment lifetime, building embodied carbon inclusion, EAC temporal matching — arise from areas where the standard does not provide cloud-specific guidance. These are interpretive divergences, not violations. A gold standard for cloud carbon accounting must resolve these ambiguities.

**3. Verification claims are narrower than they appear.** AWS's Apex assurance covers the Model 3.0 methodology and its 3 reported Scope 3 categories at limited assurance; the tool implementation itself is not audited. Azure's WSP USA review covers the methodology document, not the tool. GCP's Fraunhofer review covers LCA methodology only. No provider has had its customer-facing tool independently audited end-to-end.

**4. All three use usage allocation at the customer level.** GCP measures power physically internally (machine-level telemetry) but the customer-facing step distributes energy by price-proportional SKU factors and resource-time (vCPU-hours). AWS foundational uses instance-hours. Azure uses a usage-factor approach per region. The key differences are transparency (GCP published; AWS and Azure have not) and what the usage unit captures (GCP: vCPU-hours per SKU; AWS: instance-hours per service; Azure: undisclosed). None reflects compute utilization in the customer-reported number.

**5. All three report zero embodied carbon past the amortization window.** AWS/Azure 6 yr; GCP 4 yr. Total embodied carbon is fully allocated over the period, but fleet-wide monthly Scope 3 decreases as equipment ages past the assumed lifetime.

**6. GCP has the most transparent and granular methodology.** Internal machine-level power monitoring is best-in-class; hourly Electricity Maps for Scope 2 is best-in-class; building embodied carbon is in the customer tool (alongside AWS). The customer-facing allocation step is usage-based (price-proportional, resource-time) — a shared limitation across all three. GCP excludes end-of-life and operational waste. 4-yr amortization (vs. AWS/Azure 6-yr) yields higher reported annual embodied carbon per asset.

**7. Azure has the broadest Scope 3 category count but excludes FERA and buildings.** Azure covers 6 categories (Cat. 1, 2, 4, 5, 9, 12) and uniquely includes Cat. 9 downstream transport and Cat. 12 end-of-life. AWS covers 3 (Cat. 2 incl. buildings + non-IT, Cat. 3, Cat. 4). GCP covers 4 and uniquely includes business travel and commuting. All three have allocation opacity: AWS economic for non-foundational; GCP cost-based fallback for internal services and price-based SKU distribution; Azure's "usage" potentially being a normalized cost metric.

**8. Compute utilization is invisible to all three customer-facing methodologies.** A VM or GPU at idle and one at full load report the same carbon for the same duration and SKU. Only reducing resource-time (turning off, right-sizing, shorter runs) moves the reported number. This is the most important practical finding for users trying to reduce their reported footprint through compute efficiency.

---

## 16. References

1. AWS Customer Carbon Footprint Tool Methodology, Model 3.0 (October 2025) — https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-methodology.pdf
2. AWS CCFT Methodology Assurance Statement — Apex Companies LLC (October 2025, ISO 14064-3:2019, limited) — https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf
3. AWS CCFT Release Notes — https://docs.aws.amazon.com/ccft/latest/releasenotes/what-is-ccftrn.html
4. Google Cloud Carbon Footprint Methodology — https://docs.cloud.google.com/carbon-footprint/docs/methodology
5. Schneider, I. & Mattia, T. (2024). Carbon Accounting in the Cloud. arXiv:2406.09645 — https://arxiv.org/abs/2406.09645
6. Google Cloud Carbon Footprint Release Notes — https://cloud.google.com/carbon-footprint/docs/release-notes
7. Azure Emissions Calculation Methodology (updated January 2026) — https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology
8. Microsoft, "A new approach for Scope 3 emissions transparency" — Microsoft Scope 3 Emissions Methodology Whitepaper (2021)
9. Microsoft Cloud Hardware Emissions Methodology (CHEM) Whitepaper (2026)
10. Azure Carbon Optimization Overview — https://learn.microsoft.com/en-us/azure/carbon-optimization/overview
11. Azure Carbon Optimization Terminology — https://learn.microsoft.com/en-us/azure/carbon-optimization/terminology
12. GHG Protocol Corporate Standard — https://ghgprotocol.org/corporate-standard
13. GHG Protocol Scope 3 Standard — https://ghgprotocol.org/scope-3-standard
14. GHG Protocol Scope 2 Guidance — https://ghgprotocol.org/scope_2_guidance
15. Bhagavathula et al. (2024). Understanding Implications of Uncertainty in Embodied Carbon Models. HotCarbon 2024.
16. Lyu et al. (2023). Myths and Misconceptions Around Reducing Carbon Embedded in Cloud Platforms. HotCarbon 2023.
17. Simon et al. (2024). BoaviztAPI: A Bottom-Up Model to Assess Environmental Impacts of Cloud Services. HotCarbon 2024.