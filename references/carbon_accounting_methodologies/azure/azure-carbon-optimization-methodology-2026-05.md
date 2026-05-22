# Azure Carbon Optimization — Methodology Compilation

**Compiled:** 2026-05-22
**Source URLs crawled:**
1. https://learn.microsoft.com/en-us/azure/carbon-optimization/overview (page last updated: 2025-10-07, git commit 2025-12-16)
2. https://learn.microsoft.com/en-us/azure/carbon-optimization/view-emissions (page last updated: 2025-10-07)
3. https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology (page last updated: 2025-10-01, git commit 2026-01-01)
4. https://learn.microsoft.com/en-us/azure/carbon-optimization/emissions-terminology (page last updated: 2025-10-07) — followed as linked sub-page

---

## 1. Overview (`/azure/carbon-optimization/overview`)

### Service description

Carbon optimization helps organizations measure and minimize the carbon impact of their Azure footprint.
Features include:

- Track and analyze emissions across Azure resources and subscriptions.
- Access carbon emissions data and insights via REST APIs and CSV exports.
- Optimize resource utilization to lower emissions and costs.

### Resource coverage

> Carbon optimization tracks emissions for all Azure resource types, based on billing and usage.

### Calculation methodology

> It uses the same methodology as the Emissions Impact Dashboard. For more information, see the [calculation methodology](https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology) page. The calculation methodology ensures consistency and transparency across Microsoft's sustainability offerings.

### Data availability / granularity

- **Emissions data is updated monthly**, with a 12-month retention period.
- Data for the previous month is available by day 19 of the current month (e.g., February emissions available by March 19).
- The API provides access to up to 12 months of emissions data; the UI displays the last two months in table view.
- For historical data beyond 12 months, the Emissions Impact Dashboard offers up to five years of historical data.

### Scope coverage (as surfaced in UI)

The Emissions Trends page provides a breakdown by emissions type:

> Information is provided for **Scope 1, Scope 2 Market, and Scope 3**.

Note: the label "Scope 2 Market" (i.e., MBM) appears explicitly in the portal view.

### Dimension granularity

Emissions data is available broken down by:

- Subscription
- Resource group
- Resource
- Resource type
- Location

### Microsoft sustainability offerings comparison

| Offering | Purpose | Target users | Access |
| --- | --- | --- | --- |
| Microsoft Sustainability Manager | Broad sustainability management (carbon, water, waste) across the entire supply chain beyond cloud usage | ESG teams | Paid |
| Emissions Impact Dashboard | Organization-wide Azure emissions tracking and reporting | Central IT sustainability teams | Power BI Pro license required |
| Carbon optimization | Granular emissions tracking and optimization for IT teams | IT pros and developers | Available in the Azure portal (no additional cost) |

### Pricing

> Carbon optimization is available at no cost for all Azure customers.

---

## 2. View Emissions (`/azure/carbon-optimization/view-emissions`)

### Emissions Trends page

- **Monthly Trends** — View emissions trends over the last 12 months.
- **Breakdown by emissions type** — Hover over a bar in the chart to see emissions categorized by scope. Information is provided for **Scope 1, Scope 2 Market, and Scope 3**.
- **Breakdown by Resource type and Location** — Analyze emissions based on Azure resource type and location to identify major emitters and opportunities for reduction.
- **Top reduction opportunities** — AI-driven recommendations based on resource utilization.

### Emissions Details page

- **Breakdown by Categories** — View emissions data organized by Subscription, Resource Group, Resource, Resource Type, and Location.
- **Monthly change tracking** — Compare latest month's emissions with the previous month.
- **Data Export** — Download emissions data as a CSV file.

### Service/Resource Type taxonomy note

> The **Service** dimension was replaced by **Resource Type** to provide a more accurate view of emissions at the Azure service or product level. The Resource Types tab now groups emissions based on the overall resource you're using, rather than its individual components. For example, previously, emissions from a virtual machine in an Azure Data Explorer resource were categorized under Virtual Machine. Now, they're categorized under Azure Data Explorer, aligning with the actual **Resource Type** in use.

---

## 3. Emissions Calculation Methodology (`/power-bi/connect-data/azure-emissions-calculation-methodology`)

This is the primary methodology page, shared between Carbon Optimization and the Emissions Impact Dashboard.

### Standards basis

> At Microsoft, we segment our greenhouse gas (GHG) emissions into three categories consistent with the [Greenhouse Gas Protocol](https://ghgprotocol.org/), which is a globally recognized standard for the calculation methodology and reporting of Greenhouse Gas (GHG) emissions.

### Scope definitions

- **Scope 1**: Direct emissions — Emissions from stationary and mobile combustion, as well as process and fugitive emissions.
- **Scope 2**: Indirect emissions — Emissions from the consumption of electricity, heat, or steam.
- **Scope 3**: Other indirect emissions — Manufacturing phase and end-of-life emissions (supply chain related). The scope of this tool is **scope 3 categories 1, 2, 4, 5, 9, and 12**.

### Life cycle boundary

> The API calculations are the result of a life cycle evaluation. This evaluation assessed energy use for cloud computing operations and carbon emissions related to the following activities for Azure and Microsoft 365:
> - Manufacturing phase raw materials extraction
> - Component aggregation
> - End of management of materials

### Scope 1 detail

> GHG emissions include emissions from the combustion of diesel fuel and fugitive emissions from the use of refrigerants for cooling of our data centers. Our scope 1 emissions are small compared to our scope 2 emissions, so we combine them for reporting purposes.

### Scope 2 detail

> GHG emissions include emissions from direct power consumption used to power global data centers that Microsoft leases and owns. We invest in renewable energy power purchase agreements (PPAs) globally. We plan to be powered by 100% renewable energy and eliminate fossil fuels from backup power by 2025.

### Scope 3 detail

> GHG emissions include emissions from the following activities for hardware devices. The devices include servers and network equipment used in our leased and owned data centers.
> - Raw material extraction
> - Select component aggregation
> - End-of-life management (for example, recycling, landfill, or composting)

### Scope 1/2 calculation methodology

> Power usage for scope 1 and 2 Azure emissions categories includes storage, compute, or network. Usage time in these categories helps us attribute scope 1 and 2 emissions.

> The full methodology for scopes 1 and 2 is based on a life cycle evaluation conducted for a 2018 Microsoft study, [The carbon benefits of cloud computing: A study on the Microsoft Cloud in partnership with WSP](https://download.microsoft.com/download/7/3/9/739BC4AD-A855-436E-961D-9C95EB51DAF9/Microsoft_Cloud_Carbon_Study_2018.pdf).

The scope 2 methodology considers:

- Data center and server efficiency
- Grid emission factors
- Renewable energy purchases
- Infrastructure power usage

### Scope 3 calculation methodology

The calculation considers:

- Most common materials used to manufacture the IT infrastructure in our data centers
- Most common parts that make up cloud infrastructure (hard disks, FPGA, steel racks)
- Complete inventory of all the assets (as categorized by Microsoft bill of materials) in our data centers by region
- Carbon factors for cloud infrastructure across life stages (raw material extraction, component aggregation, usage, and end-of-life disposal)

### Calculation variables / caveats

> - The equipment lifetime defaults to six years.
> - The methodology doesn't currently include critical infrastructure, such as the data center facility, but might add it as data becomes available.
> - The Microsoft 365 methodology uses proxy usage measures instead of true server-side compute and storage usage to apportion total carbon emissions. It might replace these measures as data becomes available.

### Customer attribution / "usage" definition

> For Azure customers, the methodology allocates emissions based on their relative Azure usage in a given datacenter region. An algorithm calculates a usage factor that provides emissions per unit of customer usage in a specific Azure data center region. The algorithm then uses this factor to directly calculate emissions.

> This methodology of segmentation by customer usage is consistent across scope 1, 2, and 3 carbon calculation.

### Microsoft 365 attribution

> The methodology apportions these emissions values across customers based on proxies for server-side resource consumption, including active usage and data storage in the included Microsoft 365 applications. It computes a *regional usage factor* for each customer in each data center region that represents their usage relative to other customers.

### Billing vs. emissions divergence (verbatim)

> **How does Microsoft calculate usage?**
> Microsoft calculates usage by adding up your company's compute, storage, and data transfer in the Microsoft cloud. Usage for emissions calculations might not match your Microsoft usage for billing purposes.

### Unit of measurement

> Microsoft uses metric tons of carbon dioxide equivalent (MTCO2E).

### Excluded regions

| Geography | Datacenter region |
| --- | --- |
| Azure Government | US DoD Central, US DoD East, US Gov Arizona, US Gov Texas, US Gov Virginia, US Sec East, US Sec West, US Sec West Central |
| China | China East, China East 2, China East 3, China North, China North 2, China North 3 |
| Germany | Germany Central (Sovereign), Germany Northeast (Sovereign) |

### Evolving methodology disclaimer

> Carbon accounting practices are evolving rapidly. We're committed to evolving, revising, and refining our methodologies over time to incorporate science-based, validated approaches as they become available and relevant to assessing the carbon emissions associated with the Azure cloud.

### Assurance reference

> The white paper [A new approach for Scope 3 emissions transparency](https://go.microsoft.com/fwlink/p/?linkid=2161861) includes validation of our methodology.

---

## 4. Emissions Terminology (`/azure/carbon-optimization/emissions-terminology`)

### CO2e

Carbon dioxide equivalents.
A unit of measurement for the warming effect of greenhouse gases.
Kilograms (kgCO2e), metric tons (MTCO2e) are common prefixes to this unit.

### Carbon emissions

> Your company's allocation of Microsoft's cloud carbon emissions, based on your cloud usage. This value includes Microsoft's scopes (1, 2, and/or 3) as indicated and filtered.

### Carbon intensity

> Your company's allocation of Microsoft's carbon emissions divided by your company's cloud usage hours during the selected time period. Usage hours are based on a sum of your company's compute, storage, and data transfer in the Microsoft cloud. Usage for emissions calculations might not equal your Microsoft usage for billing purposes.

### Scope 1, 2, and 3 (terminology page definition)

- Scope 1 — direct greenhouse gas emissions from onsite fuel combustion (generators, vehicle fleet)
- Scope 2 — indirect greenhouse gas emissions such as emissions from electricity provider
- Scope 3 — other indirect greenhouse gas emissions from the value chain

### Emission reductions / emission savings

> The volume of reduced emissions. It doesn't include carbon offsets. Microsoft uses emissions "reductions" and "savings" interchangeably. Both terms describe the level of emissions after an action is taken, where that level is relatively lower than the projected level of emissions without the action.

---

## Key methodology findings summary

### "Usage" definition

Defined in the FAQ on the methodology page as: *"compute, storage, and data transfer in the Microsoft cloud."*
Explicitly stated to diverge from billing: *"Usage for emissions calculations might not match your Microsoft usage for billing purposes."*
The carbon intensity metric is defined as emissions divided by "usage hours" (same components).
Internal derivation of the per-datacenter usage factor is **not disclosed**.

### LBM vs. MBM

The portal UI labels Scope 2 explicitly as **"Scope 2 Market"**, indicating MBM is the displayed value.
The methodology page does not mention location-based method (LBM) or market-based method (MBM) by name.
The 2018/2020 WSP study underpins S1/S2 calculations and accounts for renewable energy purchases (PPAs) — consistent with market-based adjustment.

### Scope 3 categories included

Categories 1, 2, 4, 5, 9, and 12 (six categories).
End-of-life (Cat 12) is explicitly included — unusual among hyperscalers.
Buildings/critical facility infrastructure are **excluded** with a "might add as data becomes available" caveat.
FERA (Cat 3) is not listed.

### Billing vs. emissions divergence

Explicitly acknowledged verbatim: *"Usage for emissions calculations might not match your Microsoft usage for billing purposes."*

### Granularity

Monthly updates; ~19-day lag after month end.
12-month retention in Carbon Optimization portal/API.
Up to 60 months available via Emissions Impact Dashboard (Power BI).
Daily breakdowns are not offered at the customer surface (monthly is the base unit).

### Per-resource formula

No explicit formula is published.
The described approach is: compute a *regional usage factor* (customer's relative usage / total datacenter usage) and multiply by total datacenter-region emissions.
No per-SKU or per-instance power model is exposed to the customer.

### Equipment lifetime assumption

Default: **6 years** for IT equipment.

### Excluded infrastructure

Data center facility / critical infrastructure is excluded from embodied carbon.
