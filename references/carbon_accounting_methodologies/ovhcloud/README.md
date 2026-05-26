# OVHcloud — Environmental Impact Tracker (EIT)

**Customer tool:** Environmental Impact Tracker (successor to the 2023 Carbon Calculator). Customer report is a monthly + yearly PDF.

## Authoritative sources in this folder

- `ovh-eit-methodology-v2-2025.pdf` — **methodology v2.0**, dated 04/06/2025. Current authoritative reference.
- `ovh-carbon-calc-v1-2023.pdf` — **methodology v1.0** (Oct 2024 doc, covers earlier Carbon Calculator). Useful for version comparisons.

## Provider URLs

- Product landing: https://www.ovhcloud.com/en/about-us/environmental-impact-tracker/
- Launch press: https://corporate.ovhcloud.com/en/newsroom/news/environmental-impact-tracker/
- Methodology v2.0 PDF (in folder): https://corporate.ovhcloud.com/sites/default/files/2025-07/environmental_impact_tracker_-_methodology.pdf
- Methodology v1.0 (legacy calculator) PDF (in folder): https://corporate.ovhcloud.com/sites/default/files/2023-11/methodo_carboncalc-en.pdf

## Methodology summary (verify against `ovh-eit-methodology-v2-2025.pdf` before quoting)

### Surface
- Customer report generated as monthly + yearly PDF (not an interactive dashboard).

### Service coverage (v2.0, Apr 2025)
- **Covered**: Bare Metal (since May 2023), Hosted Private Cloud hosts (since Aug 2023), **Public Cloud Compute (since Jan 2025)**.
- **Coming soon**: Public Cloud Block Storage, Public Cloud Object Storage, Web Hosting.
- **Geography**: all locations **except the USA**. Table 2 of methodology covers EU, Canada, India, Singapore, Australia.

### Three reporting pillars (mapped to GHG Protocol)
- **Manufacturing** (~27% of OVHcloud's 2024 footprint).
- **Usage** (~49% — electricity supply).
- **Operations** (~24% — everything else).

### Scope coverage
- **Scope 1**: included — backup-generator combustion, owned vehicles, HFC HVAC leaks.
- **Scope 2**: LBM + MBM. MBM since November 2023, reflecting OVHcloud's low-carbon energy contracts.
- **Scope 3**: broad list — domestic + non-domestic fuel consumption, energy T&D + WTT, power for factories/offices, water, waste, fixed assets of buildings, infrastructure deployment, network equipment purchases, backbone, IT licences, consumables, employee devices, freight (air/sea/road), business travel, employee commuting, customer-side xDSL/VoIP equipment.

### Embodied carbon — Manufacturing equation
```
Σ_components ( U×Rack_EF + cores×CPU_EF + GPU_EF + GB×RAM_EF + TB×SSD_EF + TB×HDD_EF )
```
**Published emission factors** (Table 1, IJO 2022):
- Rack: 1U = 200, 2U = 250, 4U = 350 kgCO₂eq
- CPU: 1.5 kgCO₂eq / physical core
- RAM: 2 kgCO₂eq / GB
- SSD: 60 kgCO₂eq / TB
- HDD: 25 kgCO₂eq / TB
- GPU: from *Green Cloud Computing 2021 LCA study* (5-element decomposition)

Refurbishment netted via per-range ratios updated each fiscal year (Equation 2).
**5-year depreciation period** for amortising embodied carbon across the server lifetime.

### Usage (electricity)
`Footprint_usage = Electricity_server × PUE_datacenter × electricity-mix-EF_country`

- **Smart PDUs** being deployed to measure per-server power directly. **Until rollout completes, the model assumes 100% load 24/7** — customer numbers are conservative / over-estimated relative to real utilization. A workload-scaling curve is published (Fig. 6) to let customers translate the worst-case figure to their own duty cycle.
- PUE: measured per-DC where available (Table 2 ranges: 1.21–1.39 in OVH-owned DCs, 1.30–1.72 in colocations). Fallback default **PUE = 1.6** when not measurable.
- Emission factors: **Electricity Maps 2024-yearly country data** (Open Database License). Same source for both LBM and MBM.
- WUE published per DC.
- 2024 fleet CUE: 0.16 kgCO₂e/kWh-IT.

### Operations
Aggregate of everything not in Manufacturing or Usage. Allocated by **equal distribution across all customer-dedicated servers** — explicitly flagged as a simplification ("alternative approaches can be imagined, but Operations is a small share so equal distribution suffices for now"). Internal IT allocated the same way.

### Allocation to customer
- **Dedicated products** (Bare Metal, Hosted Private Cloud): full footprint of customer's server attributed (Eq. 4: `Σ_server (Manuf + Usage + Ops)`).
- **Mutualized products** (Public Cloud Compute):
  - Reference template per range — e.g., *b3-8* (2 vCPU / 8 GB / 50 GB) is the unit; *b3-64* = 8× weight; *b3-640* = 80×.
  - Customer share computed from `Σ (template-weight × billed hours)`.
  - Range capacity = min(CPU-bound, RAM-bound packing per host), summed across hosts.
  - Per-template-instance-hour footprint = `(Σ server footprints in range) / (range instance capacity)`.
  - Management & orchestration servers: pro-rata share by customer's instance volume.
- **Storage** (Block + Object, "coming soon"): per GB × duration; replication factor (×2/×3/erasure coding) accounted in capacity.

### Standards & assurance
- GHG Protocol + **Bilan Carbone®** (ADEME-derived French national standard).
- **IJO + Cost House** commissioned 2024 to perform methodological review; certification letter issued — methodology compliant with Bilan Carbone® + GHG Protocol; "adapted to OVHcloud's activities, presenting a high level of accuracy."

### Multi-criteria
- **Water** (WUE measured per DC) included.
- **Abiotic resources + land use** flagged as planned (in line with launch press but not yet in v2.0 equations).

### Replicability — *high by customer-tool standards*
- Embodied factors tabulated.
- Electricity factors sourced to public open-licensed dataset (Electricity Maps).
- Allocation rules stated as equations.
- A diligent customer could reconstruct ~80% of the number from public data. Opaque pieces: refurbishment ratios per range, exact composition of Operations.

### Known limitations (self-disclosed)
- 100%/24/7 workload assumption until full Smart-PDU coverage.
- Operations allocated equally across servers rather than usage-weighted.
- USA out of scope.
- Storage products not yet live in v2.0.

## rSCI-relevant cross-cutting observations
- **100% / 24/7 baseline** = customer numbers are *over-estimates*. Opposite direction of Big-3 tools. Residual decomposition has to handle both signs of bias.
- **Operations allocated equally per dedicated server** = a flat per-server overhead independent of usage. Exactly the "burden into customer / kept on provider / omitted" split rSCI's overhead-treatment dimension surfaces.
- **Mutualized vs dedicated split** = different allocation equations for the same physical resource depending on procurement model.
- **Per-DC electricity factors from a public open-licensed dataset (Electricity Maps)** = replicable by anyone; combined with the published per-DC PUE/WUE table, OVHcloud is closer to "auditable in public" than any other per-customer-tool provider.
