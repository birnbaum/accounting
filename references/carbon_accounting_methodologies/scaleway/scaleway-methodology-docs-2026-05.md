# Scaleway Environmental Footprint — Compiled Methodology Documentation

**Compiled from Scaleway public documentation and GitHub docs-content repository.**
**Fetch date:** 2026-05-22
**Primary sources:**
- https://www.scaleway.com/en/docs/environmental-footprint/concepts/
- https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator/
- https://www.scaleway.com/en/docs/environmental-footprint/additional-content/calculation-values-reference/
- https://www.scaleway.com/en/docs/environmental-footprint/additional-content/bare-metal-env-footprint/
- https://www.scaleway.com/en/docs/environmental-footprint/additional-content/instances-env-footprint/
- https://www.scaleway.com/en/docs/environmental-footprint/additional-content/block-storage-env-footprint/
- https://www.scaleway.com/en/docs/environmental-footprint/how-to/environmental-footprint-dashboard/
- https://www.scaleway.com/en/docs/environmental-footprint/how-to/track-monthly-footprint/
- https://www.scaleway.com/en/docs/environmental-footprint/faq/
- https://www.scaleway.com/en/blog/overcoming-the-challenges-of-cloud-environmental-impact-measurement/
- GitHub source: https://github.com/scaleway/docs-content/tree/main/pages/environmental-footprint/

**Note:** Scaleway docs are JavaScript-rendered; page bodies were retrieved from the public GitHub repository (`scaleway/docs-content`) where available. Content below represents verbatim MDX source unless otherwise noted. Page validation dates are taken from MDX frontmatter.

---

## 1. Concepts and Terminology

*Source: `pages/environmental-footprint/concepts.mdx` — validation date not retrieved; content extracted via WebFetch from GitHub.*

Key terms as defined by Scaleway:

- **DDV_DC (Data center Lifespan):** Scaleway uses a 25-year estimate for data center lifespan.
- **dU (Duration of use):** Duration of equipment use in the study period. Referenced in ADEME PCR standards.
- **Emission factor (FE):** CO₂e per kWh from a given electricity mix.
- **Energy mix:** The proportion of energy sources (nuclear, renewable, fossil) in a country's electricity supply. Varies significantly between countries.
- **Environmental impact:** Carbon emissions (kgCO₂e) plus water consumption (liters).
- **Life Cycle Analysis (LCA):** End-to-end analysis from raw material extraction through disposal; forms the basis of Boavizta's hardware impact models.
- **PUE (Power Usage Effectiveness):** Ratio of total data center energy to IT equipment energy. PUE = Total energy consumed / IT equipment energy consumed.
- **WUE (Water Usage Effectiveness):** Total water used (liters) divided by total IT energy consumption (kWh).

---

## 2. Calculation Breakdown (Main Methodology)

*Source: `pages/environmental-footprint/additional-content/environmental-footprint-calculator.mdx` — retrieved via WebFetch/WebSearch.*
*Methodology developed with IJO consultancy; based on ADEME PCR for Datacenter and Cloud services.*

### 2.1 Overview

The calculation covers the full lifecycle of cloud services and is aligned with ADEME Product Category Rules (PCR) for Datacenter and Cloud services.
The methodology measures:
- Carbon emissions across **Scope 1, Scope 2, and Scope 3**
  - Scope 1: ~1% of total
  - Scope 2: ~24% of total
  - Scope 3: ~75% of total (Scaleway notes Scope 3 ≈ over 80% in blog)
- Water consumption (WUE-based)

Lifecycle stages considered:
1. DC & Technical Environment (construction/manufacturing of datacenters)
2. Network (manufacturing + operational energy of network equipment)
3. Customer Servers (manufacturing + operational energy)
4. Cross-IT Equipment & Stock (transversal tools, monitoring infrastructure)
5. Non-IT Cross-Functional Elements (offices, employee transport, cafeteria)

### 2.2 DC and Technical Environment

The environmental impact of the datacenter building and physical infrastructure is allocated per resource using:

```
DC&TEenv = (dU / DDV_DC) × (PuissEqt / PuissCommDC) × ManufacturingImpact_DC
```

Variables:
- `dU` — duration of use (hours)
- `DDV_DC` — datacenter lifespan (25 years = 219,000 hours)
- `PuissEqt` — rated power of the equipment (watts)
- `PuissCommDC` — total power reserved by customers in the datacenter (watts)
- `ManufacturingImpact_DC` — total manufacturing impact of the datacenter (kgCO₂e)

**Example:** Elastic Metal server, 110 W power, 100 hours use, in 2000 m² datacenter with 3,000 kW total customer power, 25-year lifespan, 3.3×10⁶ kgCO₂e manufacturing impact:

```
DC&TEenv = (100 / 219,000) × (110 / 3,000,000) × 3,300,000 = 0.055 kgCO₂e
```

### 2.3 Network

Network manufacturing impact is amortized over the network equipment's entire lifespan and then allocated to resources based on their proportional energy consumption.
Manufacturing estimates use the **Boavizta database**; operational energy emission factors use the **Ember** electricity data.

### 2.4 Customer Servers

Allocation rules are product-specific (see per-product sections below).
Covers:
- Server manufacturing impact (prorated by lifespan)
- Operational energy consumption (actual or proxy-based, multiplied by energy mix emission factor × PUE)

### 2.5 Cross-IT Equipment & Stock

Manufacturing impact of transversal infrastructure tools (control plane, monitoring, load balancers, etc.) is:
- Aggregated over the duration of customer usage
- Allocated based on the proportional electrical power consumed

Stock impact = sum of manufacturing impact of all hardware / total number of servers.

### 2.6 Non-IT Cross-Functional Elements

Includes: office facilities, employee transportation, company cafeteria.
Allocation: proportional to resource power consumption relative to total power consumption.
Non-IT impacts are **updated annually** (from personnel statistics) rather than monthly, to avoid seasonal distortion.

### 2.7 Water Consumption

```
Water Consumption (liters) = Energy Consumption (kWh) × WUE (liters/kWh)
```

**Example:** 500 kWh × 0.014 liters/kWh = 7 liters/month

---

## 3. Calculation Reference Values

*Source: `pages/environmental-footprint/additional-content/calculation-values-reference.mdx` — validation: 2025-06-09, posted: 2025-06-09.*

### 3.1 Energy Mix

| Country | Energy Mix (kgCO₂e/kWh) |
|---------|-------------------------|
| France | 0.044 |
| Netherlands | 0.253 |
| Poland | 0.615 |
| Italy | 0.284 |

**Source:** [Ember](https://ember-climate.org/) Electricity Data Explorer.

*Note: The example in bare-metal-env-footprint.mdx uses 0.056 kgCO₂e/kWh for France, and block-storage-env-footprint.mdx uses 0.065 kgCO₂e/kWh. The reference-values table (0.044) represents the current authoritative value; earlier examples may reflect an older energy mix snapshot.*

### 3.2 Datacenter PUE and WUE

| Datacenter | PUE  | WUE  |
|------------|------|------|
| fr-par-1   | 1.45 | 0.009 |
| fr-par-2   | 1.16 | 0.25 |
| fr-par-3   | 1.44 | 0.001 |
| nl-ams-1   | 1.38 | 0.85 |
| nl-ams-2   | 1.4  | N/A |
| nl-ams-3   | 1.2  | N/A |
| pl-waw-1   | 1.50 | N/A |
| pl-waw-2   | 1.24 | N/A |
| pl-waw-3   | 1.5  | N/A |

Sources: FR-PAR-1: https://pue.dc2.opcore.eu/en/ ; FR-PAR-2: https://pue.dc5.opcore.eu/en/

### 3.3 Lifespans

| Component | Lifespan |
|-----------|----------|
| Hardware (servers) | 6 years (52,560 hours) |
| Data Center | 25 years (219,000 hours) |
| Network Hardware Equipment | 10 years |

---

## 4. Bare Metal Footprint Calculation

*Source: `pages/environmental-footprint/additional-content/bare-metal-env-footprint.mdx` — validation: 2025-05-27, posted: 2025-05-27.*

### 4.1 Scope

Bare Metal category includes:
- Apple Silicon servers
- Elastic Metal servers
- Dedibox servers

### 4.2 Allocation Rule

For bare metal servers, allocation is **1:1** — the full environmental impact of a server is attributed entirely to the single user who operates it.
No multi-tenant allocation is needed.

### 4.3 Manufacturing Impact

Prorated by usage duration / server lifespan using **Boavizta LCA estimates** for server manufacturing impact.

**Formula:**
```
ServerManufacturing = (dU / DDV) × ManufacturingImpact_server
```

**Example:** Elastic Metal server, 6-year lifespan (52,560 hours), 110 W power, 100 hours use, Boavizta manufacturing impact = 850 kgCO₂e:

```
ServerManufacturing = (100 / 52,560) × 850 = 1.62 kgCO₂e
```

### 4.4 Usage Impact

**Formula:**
```
UsageFootprint = Power_kW × dU × EmissionFactor × PUE
```

**Example** (using French energy mix and fr-par-2 PUE):
```
UsageFootprint = 0.110 kW × 100 h × 0.056 kgCO₂e/kWh × 1.16 = 0.715 kgCO₂e
```

### 4.5 GPU Servers — Known Gap

GPU manufacturing impact is **not currently included** for Elastic Metal GPU servers due to insufficient data from manufacturers.
CPU, RAM, disk, and energy consumption are included.
Scaleway acknowledges figures are underestimates; will update when reliable GPU manufacturing data is available.

---

## 5. Instances Footprint Calculation

*Source: `pages/environmental-footprint/additional-content/instances-env-footprint.mdx` — validation: 2025-10-01, posted: 2025-05-27.*

### 5.1 Calculation Aspects

- **Hypervisor resources** — CPU, GPU, RAM, disk of the physical hypervisor
- **Instance offer resources** — vCPU, GPU, RAM, disk allocated to the VM
- **Manufacturing impact** — hypervisor manufacturing prorated by Instance resource share and usage duration
- **Operational impact** — hypervisor energy × PUE × energy mix emission factor
- **Usage impact** — resource share-based electricity calculation (CPU proxy-based for CPU Instances)
- **Indirect emissions** — cross-functional services (network, shared storage)

### 5.2 Allocation: Instance Consumption Ratio (`Resources_Used_VM`)

The Instance's share of the hypervisor is calculated as:

```
Resources_Used_VM = (vCPU / total_pCPU) + (RAM_instance / RAM_hypervisor) + (Storage_instance / Storage_hypervisor)
```

This ratio is applied to every step of the calculation (except Cross-IT equipment & stock).

**Example:**

| Resource | Instance | Hypervisor | Allocation |
|----------|----------|------------|------------|
| CPU | 4 vCPU | 16 cores | 4/16 = 0.25 |
| RAM | 8 GB | 64 GB | 8/64 = 0.125 |
| Storage | 50 GB | 1,000 GB | 50/1000 = 0.05 |
| **Total Share** | | | **0.25 + 0.125 + 0.05 = 0.425** |

### 5.3 Manufacturing Impact Example

```
ManufacturingImpact_Instance = (dU / DDV) × ManufacturingImpact_hypervisor × Resources_Used_VM
```

Using the example above (100 hours, 6-year lifespan = 52,560 h, 100 kgCO₂e hypervisor manufacturing, Resources_Used_VM = 0.425):

```
(100 / 52,560) × 100 kgCO₂e × 0.425 = 0.080 kgCO₂e
```

### 5.4 Electricity Consumption: Boavizta Consumption Profiles

Instead of measuring exact power draw, Scaleway uses CPU usage as a proxy.
The relationship between CPU usage and power consumption is non-linear; Scaleway uses the **[Boavizta consumption profiles](https://doc.api.boavizta.org/Reference/routes/#consumption-profile-routes)** for CPUs used in Scaleway Instances.

- **Estimation mode** (pre-order): assumes 30% CPU usage as theoretical baseline.
- **Monthly report mode**: uses actual CPU consumption for highest accuracy.

Boavizta consumption profiles are currently only available for CPU Instances.
GPU Instances use average consumption of the GPU offers.

---

## 6. Block Storage Footprint Calculation

*Source: `pages/environmental-footprint/additional-content/block-storage-env-footprint.mdx` — validation: 2025-07-10, posted: 2025-07-10.*

### 6.1 Calculation Aspects

Total estimated impact integrates:
- **Dedicated manufacturing impact** — physical servers hosting storage volumes
- **Related manufacturing impact** — control plane, monitoring, internal load balancers
- **Energy usage impact** — storage servers + service management servers (Control and Data planes)

### 6.2 Allocation: `bls_ratio`

```
bls_ratio = VOLsto / VolstoPool
```

- `VOLsto` — reserved volume per user (×3 for replication, since data is replicated three times across multiple nodes for availability)
- `VolstoPool` — total storage volume reserved for Block Storage

**Example:** VOLsto = 600 GB, VolstoPool = 1,000 GB:
```
bls_ratio = 600 / 1,000 = 0.6
```

### 6.3 Manufacturing Impact

Same formula as Bare Metal server manufacturing, with `bls_ratio` applied:

```
VolumeManufacturingImpact = (dU / DDV) × ManufacturingImpact_server × bls_ratio
```

**Example** (6-year lifespan = 52,560 h, 110 W server, 100 hours, Boavizta estimate = 850 kgCO₂e, bls_ratio = 0.6):
```
VolumeManufacturingImpact = (100 / 52,560) × 850 × 0.6 = 0.97 kgCO₂e
```

### 6.4 Usage Impact

```
UsageImpact = Power_kW × EmissionFactor × dU × bls_ratio
```

Using French energy mix (0.065 kgCO₂e/kWh) and fr-par-2 PUE (1.16), electrical consumption 600 Wh, 100 hours, bls_ratio = 0.6:

```
UsageImpact = (0.600 × 0.065) × 100 × 0.6 = 2.34 kgCO₂e
```

*Note: The PUE does not appear explicitly in the published formula; the 0.065 factor likely already incorporates PUE. The 0.065 value may be an older energy mix snapshot (current reference table gives France = 0.044).*

---

## 7. Environmental Footprint Dashboard

*Source: `pages/environmental-footprint/how-to/environmental-footprint-dashboard.mdx` — validation: 2026-01-23, posted: 2026-01-23.*

### 7.1 Access

Available in Scaleway console under **Cost & Impact Management > Environmental Footprint**.

### 7.2 TEMPORAL GRANULARITY — RESEARCH FLAG

**This is the key finding for the research question.**

From the MDX source verbatim:

> "Data is generated daily and becomes visible the day after product activation."

> **Period filter behavior:**
> - **Single month selected → dashboard displays DAILY data**
> - **Multiple months selected → dashboard displays MONTHLY data**

This confirms **daily granularity is available** in the Scaleway dashboard, making it a rare provider offering sub-monthly resolution.

### 7.3 Available Filters

- **Period** — filter by month; single-month selection triggers daily view
- **Service Category** — type of service (e.g., Compute, Storage)
- **Product Category** — specific product type
- **Project** — one or more projects in the organization
- **Locality** — regions or availability zones

Deleted Projects appear as "Deleted".

### 7.4 Data Coverage

Overview shows previous and current month (carbon + water by product category).
Detailed dashboard provides per-product consumption list.
Data also retrievable via the Environmental Footprint API.

---

## 8. Monthly/Yearly Reports

*Source: `pages/environmental-footprint/how-to/track-monthly-footprint.mdx` — retrieved via WebFetch.*

- Reports available in **PDF format** for current and past periods (monthly and yearly toggle).
- **Data is generated daily.**
- If an Elastic Metal server is started on the 15th of the month, the data is calculated for 15 days of use — not the full month.
- Monthly report uses **actual CPU consumption** (not the 30% theoretical estimate used for pre-order estimation).
- Report breakdowns: by Project, geographic location (region/AZ), individual product.

---

## 9. Understanding Environmental Footprint Estimation (Pre-Order)

*Source: `pages/environmental-footprint/additional-content/environmental-footprint-calculator-estimation.mdx` — validation: 2025-05-13, posted: 2024-10-30.*

When ordering a product integrating the Environmental Footprint Calculator, customers see estimated impact before ordering.

**AZ Footprint Estimation:** Displayed as gCO₂e/kWh — based on energy mix and datacenter PUE.
Example: PAR-2 each kWh consumed ≈ 0.065 kgCO₂e.

**Offer Footprint Estimation:** Combines AZ-specific data with manufacturing impacts, network, cross-IT, and non-IT elements. Shown as gCO₂e/hour or gCO₂e/month depending on billing method.
Also shown as real-world equivalents, e.g. "≈ 35 km by car."

**Leaf icon system:**
- 3 dark green leaves = lowest impact AZ
- 2 dark green leaves = low impact
- 1 dark green leaf = higher impact

---

## 10. FAQ

*Source: `pages/environmental-footprint/faq.mdx` — retrieved via WebFetch.*

**Q: How is environmental footprint calculated?**
Methodology developed with IJO (green IT consultancy), based on ADEME Product Category Rules for Datacenters and Cloud services.
Ensures "consistency, transparency, and comparability in the assessment of environmental footprints."

**Q: Why does environmental impact data vary over time?**
Updates reflect: changes in energy mix at datacenter locations, PUE adjustments, and methodology enhancements.
Updates ensure "reports reflect the most accurate and up-to-date information."

**Q: Is hardware equipment recycled at Scaleway?**
- All equipment tested and repaired when possible.
- Over 45,000 disks tested in 2024 with ~30% reuse rate.
- Partnership with Loxy for recycling electronic waste.
- Compliance with European WEEE directive.
- Uses Trackdéchets platform for regulatory reporting.

---

## 11. Methodology Blog: Overcoming the Challenges of Cloud Environmental Impact Measurement

*Source: https://www.scaleway.com/en/blog/overcoming-the-challenges-of-cloud-environmental-impact-measurement/*

Key points:
- Scope 3 represents over 80% of the carbon footprint of their services.
- Obtaining supplier data proved difficult, particularly for older hardware (over a decade in use).
- **Boavizta** used to fill data gaps: developed "impact models based on emission factors and the average life cycle analysis (LCA) of hundreds of types of hardware."
- **Data center construction:** relies on "generic emission factors provided by ADEME" due to absent construction-specific data; uncertainty documented.
- Non-IT impacts updated annually from personnel statistics.
- Scaleway participates in ADEME's PCR standards working group.
- Hardware inventory challenges: heterogeneous equipment across multiple suppliers; "progressive data collection" for internal infrastructure servers lacking comprehensive specifications.

---

## 12. Research Flags Summary

### FLAG 1: Temporal Granularity — DAILY data available

Dashboard shows **daily granularity** when a single month is selected.
Data is generated daily (visible the day after activation).
Monthly reports use actual (not estimated) CPU consumption.
This places Scaleway ahead of most Big-3 providers, which offer monthly-only data.

### FLAG 2: Per-Product Formulas

**Bare Metal:**
- Manufacturing: `(dU / 52,560 h) × 850 kgCO₂e` (Boavizta estimate)
- Usage: `Power_kW × dU × EmissionFactor × PUE`
- Allocation: 1:1 (single-tenant, direct attribution)

**Instances:**
- Allocation via `Resources_Used_VM` = weighted sum of (vCPU/pCPU) + (RAM_vm/RAM_host) + (Storage_vm/Storage_host)
- Manufacturing: `(dU / DDV) × ManufacturingImpact_hypervisor × Resources_Used_VM`
- Electricity: Boavizta CPU consumption profiles (non-linear CPU-to-power model); 30% CPU theoretical for estimation, actual CPU for monthly report
- GPU Instances: average GPU offer consumption (no Boavizta profile yet)

**Block Storage:**
- Allocation via `bls_ratio = VOLsto / VolstoPool` (with ×3 replication factor on VOLsto)
- Manufacturing: `(dU / DDV) × ManufacturingImpact_server × bls_ratio`
- Usage: `Power_kW × EmissionFactor × dU × bls_ratio`

### FLAG 3: Boavizta Integration

Used for:
1. Server manufacturing LCA estimates (hardware impact models covering hundreds of server types)
2. CPU consumption profiles for Instances electricity calculation (non-linear workload-to-power model)

URL: https://doc.api.boavizta.org/

### FLAG 4: ADEME PCR

Scaleway's methodology is based on the **ADEME Product Category Rules (PCR) for Datacenter and Cloud services**.
This is the French national ecological agency's standardized framework for LCA of data center operations.
Covers: energy consumption, GHG emissions, resource usage, and other environmental impacts from raw material extraction through end-of-life.
Scaleway participates in ADEME's PCR standards working group.
No equivalent international standard (e.g., ISO, GHG Protocol) explicitly cited; ADEME PCR is the governing standard.

### FLAG 5: Allocation Methods

| Product | Allocation Rule |
|---------|----------------|
| Bare Metal | 1:1 direct (single tenant) |
| Instances | `Resources_Used_VM` = weighted vCPU + RAM + Storage ratio vs. hypervisor |
| Block Storage | `bls_ratio` = reserved volume / total pool (×3 for replication) |
| DC & TE | Proportional to equipment power / total customer power |
| Network | Proportional to energy consumption over equipment lifespan |
| Cross-IT | Proportional to electrical power consumed |
| Non-IT | Proportional to power consumption vs. total power |

---

## 13. Known Gaps and Limitations

- GPU manufacturing impact excluded from Elastic Metal GPU servers (insufficient supplier data).
- Boavizta consumption profiles only available for CPU Instances; GPU Instances use averages.
- Data center construction impacts use ADEME generic factors (m²-based), not site-specific LCA.
- Non-IT impact updated annually, not in real-time.
- No third-party assurance disclosed.
- Methodology spread across multiple web pages; no single citable PDF artifact.
- Energy mix values in examples appear to use older snapshots (0.056 and 0.065 kgCO₂e/kWh for France) while the current reference table gives 0.044 kgCO₂e/kWh — suggesting the methodology is actively updated and example values may lag.
