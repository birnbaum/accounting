# Azure Carbon Accounting

**Customer tools:** Emissions Impact Dashboard (EID, Power BI / Microsoft Fabric) + Carbon Optimization (Azure portal + REST API).

## Authoritative sources in this folder

- `azure-chem-2026.pdf` — **Microsoft Cloud Hardware Emissions Methodology (CHEM)** whitepaper, Jan 2026. Process-based LCA for hardware (rack, disk drive, server blades, FPGA, PSU, other). Builds on PDM/FMD data, Makersite material-to-LCI mapping, imec SSTS for semiconductors, ecoinvent LCI database, AI-augmented proxy selection.
- `microsoft-cloud-carbon-study-2018.pdf` — **The carbon benefits of cloud computing, A study on the Microsoft Cloud in partnership with WSP, Updated 2020**. Verified by reading the cover page on 2026-05-17 — this is the 2020 update of the 2018 study, **NOT** the 2021 Scope-3 Whitepaper. The famous "footnote 2" non-reconciliation passage between customer tool and corporate methodology is reportedly in a separate 2021 Scope-3 Whitepaper that is **not yet in this folder**. *Action item for the user*: locate and add the 2021 Scope-3 Whitepaper PDF (or confirm that "footnote 2" appears in this 2020 update, which my reading does not support). Until then, any paper.tex citation of "Microsoft 2021 Scope-3 Whitepaper footnote 2" is unverified.
- `microsoft-carbon-aware-computing-whitepaper.pdf` — 2023 Microsoft whitepaper on carbon-aware computing. Use sparingly; mostly product-marketing rather than methodology.

## Azure-methodology page (web-only — needs manual capture)

The current customer methodology is documented on:
- **Microsoft Learn — Azure emissions calculation methodology** (latest doc version: 2026-01-01, updated 2026-01-01):
  https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology

There is no PDF version. **Action item for the user**: print-to-PDF the live page and add as `azure-methodology-2026-01-snapshot.pdf` so the doc is citable beyond its rolling URL.

Verbatim quote from the live page (snapshot 2026-05-16):
> *"Microsoft calculates usage by adding up your company's compute, storage, and data transfer in the Microsoft cloud. Usage for emissions calculations might not match your Microsoft usage for billing purposes."*

This is the provider-acknowledged billing/emissions divergence cited in `paper/paper.tex` §3.

## Other provider URLs (for fresh verification)

- Product page: https://www.microsoft.com/en-us/sustainability/emissions-impact-dashboard
- Power BI connector (Azure): https://learn.microsoft.com/en-us/power-bi/connect-data/service-connect-to-emissions-impact-dashboard
- Power BI connector (M365): https://learn.microsoft.com/en-us/power-bi/connect-data/service-connect-emissions-impact-dashboard-microsoft-365
- Marketplace listing: https://marketplace.microsoft.com/en-us/product/power-bi/coi-sustainability.emissions_impact_dashboard?tab=overview
- Reference architecture: https://learn.microsoft.com/en-us/industry/well-architected/sustainability/emissions-impact-dashboard-architecture
- Monitoring guidance: https://learn.microsoft.com/en-us/industry/well-architected/sustainability/emissions-impact-dashboard-centralized-monitoring
- Sustainability Manager connector: https://learn.microsoft.com/en-us/industry/sustainability/sustainability-manager-import-data-emissions-impact-dashboard-connector
- Carbon Optimization (in-Azure portal): https://learn.microsoft.com/en-us/azure/carbon-optimization/overview
- Carbon Optimization data view: https://learn.microsoft.com/en-us/azure/carbon-optimization/view-emissions
- Well-Architected sustainability methodology: https://learn.microsoft.com/en-us/azure/well-architected/sustainability/sustainability-design-methodology
- CHEM whitepaper download: https://datacenters.microsoft.com/wp-content/uploads/2026/01/Whitepaper_Cloud-hardware-emissions-methodology.pdf

## Methodology summary (verify against `azure-chem-2026.pdf` + Microsoft Learn page before quoting)

### Surface (two tools)
- **EID** — subscription × service × region; Power BI / Microsoft Fabric; ≤60-month retention.
- **Carbon Optimization (CO)** — resource_group × resource; Azure portal + REST API; 12-month retention; AI-driven reduction recommendations via Azure Advisor.
- ~19-day lag; monthly granularity at the customer surface.

### Scope coverage
- **Scope 1**: included (Microsoft combines S1 with S2 for reporting).
- **Scope 2**: LBM + MBM documented; **exports carry only MBM** (LBM ≈ 0 in customer exports, confirmed empirically on Frankfurt case study).
- **Scope 3**: Cat 1 (purchased goods), Cat 2 (**IT-only — buildings excluded**), Cat 4 (upstream transport), Cat 5 (waste), Cat 9 (downstream transport), Cat 12 (end-of-life).
- **Excluded**: Cat 3 FERA, building embodied carbon.
- **Uniquely includes** Cat 12 end-of-life (AWS, GCP zero out at amortisation window).
- 6 categories total — the broadest **count** among Big-3, but with key gaps (FERA, buildings).

### Region coverage (verified 2026-05-16)
Customer methodology **excludes** the following — these regions do not appear in the dashboard at all:
- Azure Government: US DoD Central, US DoD East, US Gov Arizona, US Gov Texas, US Gov Virginia, US Sec East, US Sec West, US Sec West Central
- China: China East, China East 2, China East 3, China North, China North 2, China North 3
- Germany Sovereign: Germany Central (Sovereign), Germany Northeast (Sovereign)

Coverage is **not uniform across Microsoft's own footprint** — these are regions Microsoft doesn't fully own/operate.

### Embodied carbon (via CHEM)
- Process-based LCA (pLCA); replaces earlier financial-proxy approach.
- Component scope: rack, disk drive, server blades, FPGA, PSU, "other".
- Data sources: Microsoft PDM/FMD; Makersite (automated material→LCI); imec SSTS for semiconductors; ecoinvent LCI; AI-augmented proxy selection.
- Lifetime: 6 yr IT.
- **Buildings excluded**; "might add as data becomes available."
- End-of-life **included** (recycling, landfill, composting) — unique among Big-3.

### Allocation
- Usage allocation via *customer usage factors per datacenter region*, consistent across S1/S2/S3.
- The definition of "usage" has evolved:
  - **2021 Whitepaper**: "normalized cost metric ... normalized to exclude discounts and other variables." → closer to economic allocation.
  - **2025 Carbon Optimization docs**: "compute, storage, and data transfer time." → resource-time allocation.
- It is unclear whether this is a methodology evolution or different terminology for the same approach. **Internal derivation of the usage factor is not disclosed**, limiting independent verification.
- The CHEM 2026 whitepaper explicitly notes Microsoft "shifted from financial proxies to pLCA" for *embodied carbon* — a separate methodology track from customer-level allocation.

### Assurance
- **WSP USA** — covers Scope 3 methodology *document* only.
- Tool implementation **not** in the assurance boundary.
- Microsoft explicitly acknowledges that **the customer-facing methodology differs from corporate disclosure** (2021 Scope 3 Whitepaper footnote 2); the two numbers have not been reconciled.

### Recasting / retention
- EID: ≤60-month retention; CO: 12-month only.
- 12-month window is too short for GHG Protocol base-year recalculation on methodology change.

### Known gaps for rSCI
- "Usage" parameter definitions undisclosed.
- LBM zero-export despite documented LBM.
- FERA and buildings excluded without materiality assessment.
- Tool implementation unaudited.
- 12-month recast window too short.
- Region coverage non-uniform across Microsoft's own footprint.

## Recent verification (2026-05-16)
- Methodology page last updated 2026-01-01 (Microsoft Learn).
- Verbatim billing/emissions disclaimer confirmed.
- Region exclusion list confirmed (Gov + China + Germany Sovereign).
