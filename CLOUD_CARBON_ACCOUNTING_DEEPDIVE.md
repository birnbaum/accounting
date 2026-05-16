# Cloud Carbon Accounting — Methodology Deep-Dive

Companion to `CLOUD_CARBON_ACCOUNTING_INVENTORY.md`.
Compiled 2026-05-16.

Scope: all cloud providers in §1–§7 of the inventory, including **Big-3 hyperscalers (AWS / Azure / GCP)**, the non-Big-3 hyperscalers (Oracle, IBM, Alibaba, Huawei, Tencent), and all §2–§7 providers.
Out of scope: colocation providers; adjacent open-source tools (§8 of inventory).
Big-3 section relies on `HYPERSCALER_CARBON_ACCOUNTING.md` (May 2026, agent-ready) as primary source; this file folds those findings into the unified Tier-A schema.
Depth is **hierarchical** — Tier A (per-customer tool) gets the full schema; Tier B (corporate disclosure only) gets a short summary; Tier C (claim/none) gets one line.

## Tiering rule

- **Tier A** — provider exposes a per-customer carbon dashboard, API, or report. Data usable as Scope-3 customer input.
- **Tier B** — provider publishes corporate-level scope-1/2/3 data, but no customer-allocated number. Not usable as Scope-3 customer input under rSCI.
- **Tier C** — only marketing-level renewable/PUE claims, or nothing at all.

---

## Tier-A matrix

| Provider | Surface | Scopes | Embodied HW | Energy model | Allocation key | Standards | Assurance | Multi-criteria | Methodology doc |
|---|---|---|---|---|---|---|---|---|---|
| **OVHcloud** — Environmental Impact Tracker | Customer report (PDF), monthly + yearly | S1, S2 LBM+MBM, S3 (broad: freight, buildings, water, waste, business travel, employee commuting, IT licences, employee devices, backbone, internal IT) | **Yes** — component-level LCA with published factors (Rack/CPU/RAM/SSD/HDD) | Per-server **physical-config** model; usage = energy × PUE × electricity EF; Smart PDU rollout in progress, default 100%-24/7 workload | **Dedicated**: full server footprint to customer. **Mutualized (Public Cloud)**: instance-template-weight × reservation-hours; storage by GB × duration; mgmt/orchestration pro-rata. | GHG Protocol; **Bilan Carbone®** | **IJO + Cost House (2024 methodological review)**; certification letter for Bilan Carbone® compliance | **Water (WUE measured per DC)**; abiotic + land-use planned | [Methodology PDF v2.0 (Apr 2025)](https://corporate.ovhcloud.com/sites/default/files/2025-07/environmental_impact_tracker_-_methodology.pdf) |
| **Scaleway** — Environmental Footprint Calculator | Console + API; monthly/yearly reports | S1, S2, S3 (S3 ~80% of total per Scaleway) | Yes — via Boavizta LCA models | LCA + ADEME generic factors; per-product calculations (Bare Metal, Instances, Block/Object Storage, LB, K8s, DBs) | Per-resource calculations | ADEME PCR for DC/Cloud; co-developed with IJO | None disclosed | **Water consumption** included; multi-criteria | [Concepts](https://www.scaleway.com/en/docs/environmental-footprint/concepts/) · [Calculation breakdown](https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator/) |
| **Exoscale** — CloudAssess-based calculator | Console + API; hourly/daily/monthly | Multi-criteria (specific scope breakdown not published) | Yes — LCA-based | LCA per ISO 14040/44 | Not explicitly disclosed | ISO 14040/44; ADEME; ISO 50001 EnMS (in implementation) | None disclosed | Multi-criteria (multicriteria balance sheet) | [Sustainability page](https://www.exoscale.com/sustainability/) |
| **Akamai** — Carbon Calculator | Akamai Control Center (all delivery-product customers); 400 days history | Reported as **Scope 3 Cat 8** (upstream leased assets) for the customer | Not disclosed in customer report | Byte-utilization + machine-utilization → DC energy → emissions | DC energy & emissions allocated by byte + machine utilization | GHG Protocol; Cat-8 mapping for customer Scope 3 | Corporate emissions externally reported; tool itself not separately assured | None disclosed | [Carbon Calculator blog](https://www.akamai.com/blog/culture/akamai-carbon-calculator-supply-chain-emissions) · [Customer reporting blog (2025)](https://www.akamai.com/blog/sustainability/2025/may/what-akamai-is-doing-for-customer-reporting) |
| **Cloudflare** — Carbon Impact Report | Dashboard; all plans | Scope 3 (customer's indirect emissions from using Cloudflare) | Not included | Data-transfer-based: bytes × per-request energy | Per-customer data-transfer share | No formal alignment cited; emission factors from EPA / DEFRA / IEA | None for the customer tool | None | [Methodology blog](https://blog.cloudflare.com/understand-and-reduce-your-carbon-impact-with-cloudflare/) |
| **Fastly** — Sustainability Dashboard | Control panel + API + CSV | **No Scope 1.** S2 LBM+MBM. S3 Cat 3 (FERA) + Cat 8 (non-IT in leased assets). | **Not included** | CPU-time apportionment across processes; no fleet-utilization or time/HW power model | Delivery: network-transfer volume. Compute: request-time. Shared: distributed as overhead. | GHG Protocol Scope 2 Guidance; BSR Future of Internet Power | Operator-substantiated renewable evidence; no independent audit cited | None | [Methodology page](https://www.fastly.com/documentation/guides/account-info/sustainability/our-sustainability-dashboard-methodology/) |

Quick read: every Tier-A tool aligns to GHG Protocol at the surface, but only OVHcloud, Scaleway, and Exoscale do real LCA-based embodied accounting.
Akamai uses real DC-utilization allocation but doesn't publish equations.
Cloudflare and Fastly are bytes-/CPU-time-based at the edge; Fastly explicitly excludes embodied hardware and Scope 1.
None publishes a third-party ISO 14064-3 / ISAE 3410 assurance statement for the customer-allocated number specifically.

---

## Tier-A — provider details

### OVHcloud — Environmental Impact Tracker

Successor (2025) to the 2023 Carbon Calculator.
Methodology v2.0 dated 04/06/2025; v1.0 was October 2024.
Customer report is generated as a monthly + yearly PDF.

- **Products covered (v2.0)**: Bare Metal (since May 2023), Hosted Private Cloud (hosts since Aug 2023), **Public Cloud Compute (since Jan 2025)**. Public Cloud Storage (Block + Object) and Web Hosting are flagged as coming soon.
- **Geography**: all locations **except the USA** (Vint Hill in the per-DC table appears to be in scope but USA is explicitly excluded in §1.2 — the table covers EU, Canada, India, Singapore, Australia).
- **Three reporting pillars** (mapped to GHG Protocol): **Manufacturing** (~27% of OVHcloud's 2024 footprint), **Usage** (~49% — supply of electricity), **Operations** (~24% — everything else).
- **Scopes 1+2+3 included.** Scope 1 = backup-generator combustion, owned vehicles, HFC HVAC leaks. Scope 3 categories enumerated: domestic + non-domestic fuel consumption, energy T&D + WTT, power for factories/offices, water, waste, fixed assets of buildings, infrastructure deployment, network equipment purchases, backbone, IT licences, consumables, employee devices, freight (air/sea/road), business travel, employee commuting, customer-side xDSL/VoIP equipment.

**Manufacturing.** Equation: `Σ components (U×Rack_EF + cores×CPU_EF + GPU_EF + GB×RAM_EF + TB×SSD_EF + TB×HDD_EF)`. Published emission factors (Table 1, IJO 2022):
- Rack: 1U = 200, 2U = 250, 4U = 350 kgCO₂eq.
- CPU: 1.5 kgCO₂eq / physical core.
- RAM: 2 kgCO₂eq / GB.
- SSD: 60 kgCO₂eq / TB.
- HDD: 25 kgCO₂eq / TB.
- GPU: derived from the *Green Cloud Computing* 2021 LCA study, summed across 5 elements (graphics processor, memory, PCB, computer bus, heat dissipation).

Refurbishment is netted in via per-range ratios updated each fiscal year (Equation 2).
5-year depreciation period for amortising embodied carbon across the server lifetime.

**Usage.** `Footprint_usage = Electricity_server × PUE_datacenter × electricity-mix-EF_country`.
- Smart PDUs are being deployed to directly measure per-server power; **until rollout completes, the model assumes 100% load 24/7** — i.e. customer numbers are conservative / over-estimated relative to real utilization. A workload-scaling curve is published (Fig. 6: 0–100% over the day) to let customers translate the worst-case figure to their own duty cycle.
- PUE: measured per-DC where available (Table 2: ranges 1.21–1.39 in OVH-owned DCs, 1.30–1.72 in co-locations); fallback default **PUE = 1.6** when not measurable.
- Emission factors: **Electricity Maps 2024-yearly country data** (Open Database License, CC-BY-SA-ODbL) for location-based; market-based factors since November 2023 reflecting OVHcloud's low-carbon energy contracts.
- WUE published per DC.
- 2024 fleet CUE: 0.16 kgCO₂e/kWh-IT.

**Operations.** Aggregate of everything not in manufacturing or usage. Allocated by **equal distribution across all customer-dedicated servers** — explicitly flagged as a simplification (alternative approaches "can be imagined" but Operations is a small share so equal distribution suffices for now). Internal IT is allocated the same way.

**Allocation to customer.**
- **Dedicated products** (Bare Metal, Hosted Private Cloud): full footprint of the customer's server(s) is attributed, broken down by DC and service (Equation 4: Σ_server (Manuf + Usage + Ops)).
- **Mutualized products** (Public Cloud Compute):
  - Reference template defined per range — e.g. *b3-8* is the unit (2 vCPU / 8 GB / 50 GB), *b3-64* = 8× weight, *b3-640* = 80×. Customer share is computed from `Σ(template-weight × billed hours)`.
  - Total range capacity is calculated as the smaller of CPU-bound or RAM-bound packing per host, summed across hosts.
  - Average per-template-instance-hour footprint = (Σ server footprints in range) / (range instance capacity).
  - Management & orchestration servers: pro-rata share by customer's instance volume.
- **Storage** (Public Cloud Block + Object, "coming soon" in v2.0 doc): footprint per GB × duration of service use; replication factor (×2/×3/erasure coding) accounted in capacity calculation.

**Standards & assurance.**
- GHG Protocol; **Bilan Carbone®** (ADEME-derived French national standard).
- IJO (green IT) + Cost House (economic performance) commissioned 2024 to perform methodological review.
- Certification letter issued — methodology compliant with Bilan Carbone® and GHG Protocol; described as "adapted to OVHcloud's activities, presenting a high level of accuracy".

**Multi-criteria.**
- Water: WUE measured per DC, present in the methodology tables.
- Abiotic resources + land-use: flagged as planned (in line with the launch press materials but not yet in v2.0 equations).

**Replicability.** **High by Tier-A standards.** Embodied factors are tabulated, electricity factors are sourced to a public open-licensed dataset (Electricity Maps), allocation rules are stated as equations. A diligent customer could reconstruct ~80% of the number from public data; the only opaque pieces are refurbishment ratios per range and the exact composition of Operations.

**Known limitations (self-disclosed).**
- 100%-24/7 workload assumption until full Smart-PDU coverage.
- Operations allocated equally across servers rather than usage-weighted.
- USA out of scope.
- Storage products not yet live in v2.0.

### Scaleway — Environmental Footprint Calculator

Calculator surfaces in the Scaleway console, with monthly/yearly reports and API.

- **Products covered**: Bare Metal, Instances, Block Storage, Object Storage, Load Balancer, Kubernetes, Managed Databases (each with its own per-product methodology page).
- **Scopes**: 1, 2, 3. Scaleway reports Scope 3 at >80% of total service emissions.
- **Embodied hardware**: yes — LCA via partnership with **Boavizta**, a French association that maintains open LCA impact models for hardware, including older servers that suppliers don't characterise themselves.
- **Energy model**: LCA-based for embodied, ADEME generic factors (per m² datacenter) for construction where site-specific data is missing.
- **Allocation to customer**: per-resource calculations exposed (each product has its own page).
- **Standards**: ADEME's PCR (Product Category Rules) for datacenter and cloud services — the French national ecological agency's standardized framework. Co-developed with the IJO consultancy.
- **Multi-criteria**: **water consumption** is included alongside carbon — uncommon among providers.
- **Assurance**: none disclosed.
- **Open methodology**: [Concepts](https://www.scaleway.com/en/docs/environmental-footprint/concepts/), [Calculation breakdown](https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator/), [Calculation reference values](https://www.scaleway.com/en/docs/environmental-footprint/additional-content/calculation-values-reference/).
- **Acknowledged uncertainty**: data-center-construction factors carry high uncertainty; non-IT impacts updated annually from personnel statistics to avoid seasonal distortion. Methodology is described as "actively evolving".
- **Replicability**: per-product calculation pages + reference values page intended to support customer recompute; quality of disclosure is among the best in this set.

### Exoscale — CloudAssess-based calculator

CloudAssess is an LCA engine co-developed with **Resilio** and **Kleis**; Exoscale exposes it as a customer-facing calculator.

- **Surface**: console + API; hourly, daily, and monthly granularity.
- **Standards**: ISO 14040 / ISO 14044 (LCA); ADEME; ISO 50001 Energy Management System in implementation.
- **Multi-criteria**: yes — described as "multicriteria impact analysis" beyond carbon (water/abiotic not enumerated publicly).
- **Energy mix per DC**: published carbon-intensity figures for 2024 sourced from electricitymaps.com (42 g CO₂e/kWh CH → 126 g AT).
- **Scope coverage detail**: not publicly enumerated in scope-1/2/3 terms.
- **Allocation key**: not publicly disclosed.
- **Embodied hardware**: yes — by virtue of LCA / ISO 14040 alignment.
- **Assurance**: none disclosed; ISO 50001 audit targeted.
- **Open methodology**: [Sustainability page](https://www.exoscale.com/sustainability/), [Academy intro](https://community.exoscale.com/academy/intro_sus/). Underlying CloudAssess methodology is partner-owned and not fully public.
- **Replicability**: low — calculator is exposed but the engine is third-party.

### Akamai — Carbon Calculator (Akamai Control Center)

Per-customer report inside the Control Center; available to **all delivery-product customers**; supports up to 400 days of history with year-over-year comparison.

- **Customer scope mapping**: reported as **Scope 3 Category 8** (upstream leased assets) for the customer — so the number is structured to plug directly into a customer's own Scope 3 inventory.
- **Allocation key**: byte utilization and machine utilization per DC are used to allocate the appropriate proportion of a data center's energy use and emissions to a customer.
- **Energy model**: real DC energy use × utilization weighting; not bytes-only.
- **Embodied hardware**: not separately disclosed in the customer report.
- **Scopes 1 and 2 for Akamai itself**: published in the corporate sustainability report.
- **Standards**: GHG Protocol; customer report is explicitly Cat-8-compatible.
- **Assurance**: Akamai's corporate emissions are externally reported; the customer-allocated report itself is not separately assured.
- **Replicability**: low — equations not published; customer relies on Akamai's allocation.

### Cloudflare — Carbon Impact Report

Available to all plans, including free.

- **Frame**: presented as a **Scope 3** report from the customer's perspective; primary narrative is "carbon saved by using Cloudflare vs. average network".
- **Allocation**: per-customer data-transfer (bytes) × per-request energy factor.
- **Energy factor**: derived from public DC-energy benchmarks plus internal Cloudflare PoP-level emission scores; IEA, EPA, DEFRA used for emission-factor sources.
- **Embodied hardware**: not included.
- **Granularity**: account-level; no per-service breakdown described.
- **Standards**: no formal GHG-Protocol scope-3-category alignment cited.
- **Assurance**: none for the customer tool; corporate emissions reported under SBTi commitment.
- **Open methodology**: blog-level only — [methodology blog](https://blog.cloudflare.com/understand-and-reduce-your-carbon-impact-with-cloudflare/), [SBTi/savings blog](https://blog.cloudflare.com/switching-cloudflare-cut-your-network-carbon-emissions-sbti/), [Impact Reports 2021](https://www.cloudflare.com/resources/assets/slt3lc6tev37/1vmmNMaaktXDk5iHxxDdCj/ebe40635588eaafa15ab89944ff9a36b/Cloudflare_Impact_Report_2021.pdf) / [2023](https://cf-assets.www.cloudflare.com/slt3lc6tev37/3Z7xOV53lGEIAwCqw5SncT/69eaca7bd5d2395ee0274b15e7854dd6/2023_Impact_Report.pdf).
- **Replicability**: low — the per-request factor and PoP-specific scores are not tabulated publicly.

### Fastly — Sustainability Dashboard

Surfaces in the Fastly control panel, plus API and CSV download.

- **Products covered**: Fastly Delivery and Compute. Excludes third-party cloud hosting (Compute@Edge backends) and Fastly's own corporate emissions.
- **Scopes**: **no Scope 1**; Scope 2 LBM+MBM (IT-equipment electricity in colocated facilities); Scope 3 Cat 3 (FERA — upstream fuel-and-energy, T&D losses, well-to-tank) and Cat 8 (non-IT equipment in leased assets — cooling, building).
- **Embodied hardware**: **explicitly excluded** — material extraction, transport, manufacturing, construction, end-of-life all out of scope.
- **Energy model**: power apportioned by CPU-time across processes; does not account for variation in fleet CPU utilization, time-based, or hardware-based power-consumption modeling. A 25% adjustment is applied to cache-server electricity when PDU-data discrepancies occur (infrastructure overhead).
- **Allocation key**: Delivery → network-transfer volume; Compute → request-time; shared processes → distributed as overhead to customers.
- **Renewable accounting**: location-based (no renewables) vs. market-based (includes EAC procurement; Fastly 100% EAC commitment from Jan 2025).
- **Standards**: GHG Protocol Scope 2 Guidance; BSR Future of Internet Power Report methodology.
- **Assurance**: facility operators must substantiate their renewable energy procurement via contracts/attestations/EACs; no independent audit of the dashboard cited.
- **Granularity**: daily, at facility / country / state-or-region / global levels.
- **Update lag**: PUE, renewable percentages, and emission factors are "only ever available for the previous year".
- **Open methodology**: [methodology page](https://www.fastly.com/documentation/guides/account-info/sustainability/our-sustainability-dashboard-methodology/), [2024 Sustainability Report PDF](https://investors.fastly.com/files/doc_governance/2025/Nov/26/2024-Fastly-Sustainability-Report-290db1.pdf).
- **Replicability**: methodology is the most explicit in this set — both the apportionment rule and the 25% overhead correction are stated; reference factors not fully tabulated though.

---

## Tier-B — corporate disclosure only

For these providers a corporate emissions report exists but there is no per-customer allocation.
Numbers cannot be plugged into a customer's Scope 3 inventory directly under rSCI — only as a top-down provider total to potentially benchmark against.

### Rackspace
SBTi-validated net-zero targets (50% by 2032, 90% by 2045).
Third-party-audited Scope 1/2/3 baseline.
80% renewable across global DCs.
Customer-facing offering is consulting (Workload Aware Modernization), not a carbon dashboard.
Refs: [2025 Sustainability Report](https://www.rackspace.com/newsroom/rackspace-technology-releases-2025-sustainability-report), [SBTi approval press](https://www.rackspace.com/newsroom/rackspace-receives-sbti-approval-net-zero-targets).

### DigitalOcean (+ Paperspace)
Publishes ESG microsite; no per-customer carbon data, no SBTi or CDP participation.
PUE-only operational disclosure (~1.15).
Inherits energy mix from colocation partners (e.g. Equinix) — explicitly does not state per-region energy policy.
Refs: [Impact page](https://www.digitalocean.com/impact), [IR ESG](https://investors.digitalocean.com/esg/esg-overview/default.aspx).

### UpCloud
First ESG report published 2024.
70% of DCs on renewable electricity; remainder mixed-grid + offsetting.
ISO 14001 (energy management) and ISO 27001.
Green Web Foundation verified.
Identified own largest emissions source as DC hardware purchases.
Refs: [2024 year-in-review](https://upcloud.com/2024-year-in-review/), [Green Web Provider blog](https://upcloud.com/blog/were-a-green-web-provider/).

### GleSYS
2024 sustainability report with CSRD-aligned baseline.
100% renewable electricity; market-based Scope 2 = 0.22 tCO₂e from district heating; total 1,956 tCO₂e (2024).
Energy Reuse Factor 84% (recovered heat into Falkenberg district heating, 4.8 GWh).
PUE 1.28 group-wide.
Targets: -99% Scope 1 by 2030, fossil-free backup by 2030.
Refs: [Sustainability](https://glesys.com/sustainability/), [2024 report announcement](https://glesys.com/blog/glesys-releases-2024-sustainability-report-and-establishes-csrd-aligned-baseline-edited/).

### Crusoe
First ESG report 2022 (covers 2022 data).
Business model is the disclosure: Digital Flare Mitigation diverts otherwise-flared gas into compute — reports volumetric methane / flared-gas avoidance (~5.4 Bcf flared gas avoided, ~8,500 t methane avoided, ~635,000 MWh generated in 2023).
Per-GPU reduction claim of ~4.4 tCO₂e/yr.
No per-customer allocated emissions tool.
Refs: [2022 ESG Report PDF](https://crusoe-public.s3.us-east-2.amazonaws.com/Crusoe_ESG+Report_2023.05.10.pdf), [resources blog](https://www.crusoe.ai/resources/blog/crusoe-tallys-law-leading-energy-transition).

### Nebius
2024 Sustainability Report.
Claims 94% low-carbon electricity, 0.04 tCO₂e/MWh market-based intensity.
Finland DC reportedly provides 65% of local municipality heating via heat reuse.
Iceland / Paris / UK sites stated as 100% renewable.
Scope 3 and water consumption reportedly absent from the disclosure (flagged externally as a transparency gap).
Refs: [Sustainability hub](https://nebius.com/sustainability), [2024 report announcement](https://nebius.com/newsroom/nebius-group-2024-sustainability-report-highlights-importance-of-sustainability-to-long-term-value-creation-in-ai-infrastructure).

### Verne (Iceland/Finland)
2024 Iceland-campus emissions: 556.25 tCO₂e total (S1 9.1%, S2 80.4%, S3 10.4%).
100% renewable power on the Iceland campus; three Finland DCs on renewable power.
No per-customer tool.
Refs: [Sustainability](https://www.verne.co/about-us/sustainability), [Main site](https://www.verne.co/).

### Infomaniak
ISO 14001:2015 (SGS-audited annually) and ISO 50001.
Scope includes raw materials, production, transport, waste, **employee commute**.
PUE 1.06 (air-cooled, no water cooling).
200% offset via Myclimate Foundation (gap from internal reductions).
Server lifetime extended to 15 years.
No per-customer carbon dashboard.
Refs: [Ecology page](https://www.infomaniak.com/en/ecology), [200% offset blog](https://news.infomaniak.com/en/infomaniak-offsets-twice-as-many-co-emissions/), [Eco-design FAQ](https://www.infomaniak.com/en/support/faq/1160/eco-design-to-reduce-carbon-footprint).

### Salesforce / Heroku
Carbon-neutral corporate cloud claim.
Internal KPI "Carbon to Serve" (DC emissions ÷ application work done); reported -26% since 2020.
Hyperforce positioned as 100% renewable architecture.
No per-app or per-account customer emissions surface on Heroku — only inheritance of the corporate-level claim.
Refs: [Sustainability hub](https://www.salesforce.com/company/sustainability/), [Net Zero Cloud product](https://www.salesforce.com/products/sustainability-cloud/overview/), [Green Code initiative](https://www.salesforce.com/news/stories/green-code-software/), [Heroku KB](https://help.heroku.com/2163BDDI/is-my-app-carbon-neutral).

### Leafcloud
Operational metrics published with concrete numbers: PUE 1.02, ERE ~0.15, ~85% heat capture.
Heat-reuse model places servers inside buildings that need heat (pools, apartments, nursing homes).
No per-customer carbon dashboard surfaced.
Refs: [Truly Green landing](https://leaf.cloud/truly-green), [Green-cloud explainer](https://leaf.cloud/blog/green-cloud-energy-use-and-residual-heat-what-actually-makes-a-cloud-sustainable).

### Open Telekom Cloud (T-Systems / Deutsche Telekom)
Climate Neutral Data Centre Pact signatory.
100% green-electricity purchase for DCs (Biere/Magdeburg PUE 1.28; Aalsmeer/Almere 1.46/1.40).
Deutsche Telekom corporate CR report covers Scopes 1/2/3.
No per-customer cloud carbon tool surfaced.
Refs: [Sustainability page](https://www.open-telekom-cloud.com/en/benefits/sustainability), [Telekom CR report 2024 PDF](https://report.telekom.com/cr-report/2024/_assets/downloads/env-environment-dtag-cr24.pdf).

### atNorth
Sustainability strategy + Nordic-grid-mix disclosure.
No first-party emissions report at provider level surfaced; no per-customer tool.
Refs: [Sustainability strategy](https://www.atnorth.com/sustainability/sustainability-strategy/).

---

## Tier-C — claim only / nothing found

These providers offer marketing-level statements (renewable %, PUE, ambitions) but no methodology and no per-customer accounting.
Listed for completeness; none are usable as Scope-3 customer input under rSCI.

| Provider | Category | What's published | Source |
|---|---|---|---|
| Hetzner | Tier-2 | "100% renewable" (hydropower DE/FI); PUE ~1.13; EMAS-certified DE sites; building own solar via HT Clean Energy | [Sustainability](https://www.hetzner.com/unternehmen/nachhaltigkeit) |
| Vultr | Tier-2 | Net-zero-by-2029 ambition; Sabey hydropower DC partnership | [Sabey press](https://www.businesswire.com/news/home/20240305527534/en/Vultr-Expands-Footprint-with-New-NVIDIA-Cloud-GPU-Capacity-Using-Clean-Renewable-Hydropower-in-Sabey-Data-Centers) |
| STACKIT | Sovereign EU | Green-electricity DCs in DE/AT; DC10 Ostermiething PUE 1.1; Schwarz Group net-zero-by-2050 | [Sustainability](https://stackit.com/en/learn/knowledge/cloud/sustainability) |
| GreenGeeks | Niche green | REC-based "300% renewable" via Bonneville Environmental Foundation; US EPA Green Power Partner since 2009 | [Going green](https://www.greengeeks.com/going-green) |
| Krystal | Niche green | Direct renewable PPAs preferred over RECs; Gold-Standard projects; tree-planting via Veritree | [Green hosting](https://krystalhosting.com/green) |
| CoreWeave | AI/GPU | Sustainability strategy stated (clean energy, efficiency, recycling); Scope 1/2 measurement "in progress"; no formal targets or methodology | [About](https://www.coreweave.com/about-us), [FY25 10-K](https://s205.q4cdn.com/133937190/files/doc_financials/2025/q4/CoreWeave-Inc-FY25-10-K-7.pdf) |
| Lambda | AI/GPU | Marketing references to "zero-emissions energy standards" at Mountain View; no report or methodology | [Site](https://lambda.ai/) |
| Hyperstack (NexGen) | AI/GPU | 100% renewable marketing claim; Tier-3 DC partnerships; AQ Compute "net-zero AI supercloud" | [Site](https://www.hyperstack.cloud/), [AQ Compute blog](https://www.hyperstack.cloud/blog/company-news/nexgen-cloud-and-aq-compute-advance-towards-net-zero-ai-supercloud) |
| DataCrunch | AI/GPU | Helsinki + Iceland sites; waste-heat reuse claim; no formal report | [Clusters](https://datacrunch.io/clusters), [TechCrunch](https://techcrunch.com/2024/10/21/datacrunch-wants-to-be-europes-first-ai-cloud-hyperscaler-powered-by-renewable-energy/) |
| RunPod | AI/GPU | Nothing found | n/a |
| Paperspace | AI/GPU | Acquired by DigitalOcean — inherits DO Tier-B | n/a |
| Together AI | AI/GPU | Nothing found | n/a |
| Fireworks AI | AI/GPU | Nothing found | n/a |
| Replicate | AI/GPU | Nothing found | n/a |
| Vercel | PaaS | "Green energy policy" KB only; emissions inherited from underlying cloud providers | [KB](https://vercel.com/kb/guide/what-is-vercel-green-energy-policy) |
| Netlify | PaaS | "Jamstack/CDN is intrinsically lower-emission" narrative; no per-customer accounting | [Sustainability](https://www.netlify.com/sustainability/) |
| Fly.io | PaaS | Community thread only | [Thread](https://community.fly.io/t/carbon-emissions/4345) |
| Render | PaaS | Inherits AWS/GCP — no first-party disclosure | [Thread](https://community.render.com/t/does-render-use-green-energy/912) |

---

## Patterns and gaps

**On surface availability.** Customer-facing tools cluster in two camps: French/Swiss EU providers anchored to ADEME/LCA standards (OVHcloud, Scaleway, Exoscale), and edge-network providers (Akamai, Cloudflare, Fastly).
None of the AI/GPU clouds, the GPU-niche-green providers, or the PaaS layer publish a per-customer tool today — even where the underlying infrastructure is genuinely low-carbon (Crusoe DFM, Verne, Nebius).
This means workloads in the fastest-growing segment (GPU-AI) currently have no first-party Scope-3 input — the rSCI residual question matters most exactly where the data is sparsest.

**On scope coverage.** Among Tier-A tools, only OVHcloud and Scaleway claim Scope 1+2+3 with embodied hardware.
Fastly explicitly excludes Scope 1 and all embodied hardware — a structurally smaller number that is not directly comparable with the others.
Cloudflare excludes embodied and reports only a savings-framed Scope-3 number.
Akamai reports a Scope-3-Cat-8-framed customer number, structurally complementary to a customer's own GHG-Protocol inventory.

**On allocation key.** The Tier-A tools split cleanly:
- **Utilization-allocated** (real DC energy × utilization share): Akamai, OVHcloud.
- **Bytes/request-allocated** (CPU-time or transfer volume): Cloudflare, Fastly.
- **LCA-modeled per-resource**: Scaleway, Exoscale.

These three families won't reconcile against each other or against a top-down hyperscaler total without explicit residual decomposition.

**On replicability.** OVHcloud is the highest in the set after a real read of the methodology PDF: tabulated component emission factors, public open-licensed electricity factors (Electricity Maps), and stated allocation equations.
Fastly has the most explicit allocation rule (transfer-volume / request-time / overhead apportionment with a stated 25% PDU correction).
Scaleway's modular per-product methodology pages are the closest equivalent on the EU-LCA side.
The others are either opaque (Akamai, Cloudflare) or partner-engine (Exoscale via CloudAssess).

**On assurance.** None of the Tier-A customer-allocated numbers carries third-party ISO 14064-3 / ISAE 3410 assurance.
IJO benchmark recognition (OVHcloud) and consultancy partnerships (Scaleway with IJO; Exoscale with Resilio/Kleis) are methodology-level, not data-level.
Corporate Scope 1/2/3 numbers are externally audited at several providers (Akamai, Rackspace), but that audit doesn't extend to the customer-allocated dashboard.

**On multi-criteria.** Water + abiotic + heat-reuse / ERE are emerging differentiators.
Scaleway and OVHcloud (planned) include water; GleSYS, Leafcloud, Nebius, Infomaniak publish ERE/ERF or heat-reuse percentages.
None of this is in any hyperscaler tool today (deferred to the §1 deep-dive).

**Candidates for a second pass before paper integration.**
- ~~OVHcloud 2025 methodology PDF~~ — **done** (v2.0, 04/06/2025; see provider section above).
- Scaleway per-product calculation pages and "Calculation reference values" — likely the Tier-A provider closest to OVHcloud on customer recompute; worth verifying via direct read.
- Akamai customer-reporting blog (May 2025) — confirm exactly how Cat-8 numbers are exposed to customers.
- Crusoe — the DFM "avoided emissions" framing sits awkwardly against rSCI's residual model; worth a focused note even though there's no per-customer tool.
- Nebius — the externally-flagged Scope 3 / water gap is worth a paragraph as a case where the corporate disclosure is *better* than the actual measurement reality.

---

# Hyperscalers (excl. AWS / Azure / GCP)

Five providers self-identify or are commonly grouped as hyperscalers: **Oracle Cloud (OCI), IBM Cloud, Alibaba Cloud, Huawei Cloud, Tencent Cloud**.
Big-3 (AWS / Azure / GCP) are deferred to a separate file.
This section applies the same Tier-A schema used above.

## Hyperscaler matrix

| Provider | Surface | Scopes | Embodied HW | Energy model | Allocation key | Standards | Assurance | Multi-criteria | Methodology doc |
|---|---|---|---|---|---|---|---|---|---|
| **Oracle Cloud (OCI)** — Carbon Emissions Analysis | OCI Console + Usage API; 7 default reports | S2 LBM + S2 MBM (EU MBM = 0 by design); S1/S3 not explicit | **No** (operational only) | Two modes: **Power-based** (kWh × regional EF; only for some services) or **Spend-based** ($ × regional EF; broader service coverage) | Power-based: allocates DC energy across dedicated + shared hardware per resource. Spend-based: pre-discount spend × regional EF. | GHG Protocol; EU/UK regulatory alignment | **None disclosed for the customer tool** | None | [Emissions Management docs](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/emissions-management.htm) · [Technical guidance PDF](https://www.oracle.com/a/ocom/docs/corporate/technical-carbon-calculation-guidance.pdf) |
| **IBM Cloud Carbon Calculator** | Console + REST API; integrates into IBM Envizi (separate licence) | Scope 1 + Scope 2 (LBM); Scope 3 / embodied **excluded** | **No** (excluded — explicitly out of scope) | `Electricity_service,location × PUE_location × CEF_location` | Per service × location × client account; ML/anomaly detection layered on top | GHG Protocol | **None disclosed**; "client responsible for confirming accuracy" footnote | None | [Methodology v3 PDF](https://cloud.ibm.com/media/docs/downloads/account/carbon-calc-method-v3.pdf) · [API docs](https://cloud.ibm.com/apidocs/carbon-calculator) |
| **Alibaba Cloud** — Energy Expert | Console (Energy Expert platform) | S1 (direct ops); S2 (purchased electricity); **S3 (leased computer rooms)** | Not addressed in public docs | Per-IDC PUE × resource sales × green-power-usage ratio × technical carbon-reduction measures | Three-level allocation: IDC → cloud product → cloud account → tenant usage | GHG Protocol Corporate Standard; **ISO 14064-3:2019**; CEC procedures | **Bureau Veritas** (Beijing) — "first enterprise in China to pass carbon-accounting-services-for-cloud evaluation" (July 2023); TÜV Rheinland certification for customer outputs | None | [Cloud product carbon footprint docs](https://www.alibabacloud.com/help/en/energy-expert/support/cloud-product-carbon-footprint) |
| **Huawei Cloud** — Huella Cloud (partner SaaS via KooGallery) | Third-party SaaS purchased in marketplace; not first-party | Account-level cloud consumption; specific scope mapping not public | Not addressed | Multi-provider consumption analysis by provider / region / service / energy characteristics | Per-account monthly attribution | "Verified Carbon Standard (VCS)" referenced for offset side; methodology built with quantification + cloud experts | **None** | None | [Marketplace listing](https://marketplace.huaweicloud.com/intl/contents/8e3ba722-ba1e-46ac-8b52-9ea15f85ba40) |
| **Tencent Cloud** | **n/a** — no per-customer cloud carbon tool | Corporate Scope 1/2/3 reporting only | n/a | n/a | n/a | GHG Protocol (corporate) | n/a | n/a | [Sustainability page](https://www.tencentcloud.com/global-infrastructure/sustainability) (Tier B — corporate disclosure only) |

Quick read: Oracle and IBM both ship real, methodology-backed tools with published equations and (in IBM's case) a versioned PDF + API.
Alibaba is the only one in this set that has carried out a **third-party data assurance** (Bureau Veritas) of the cloud-customer accounting — stronger on that axis than any Tier-A provider in §1.
Neither Oracle nor IBM includes embodied hardware (vs OVH/Scaleway which do).
Huawei outsources the dashboard to a marketplace partner — methodologically thin.
Tencent is corporate-only.

---

## Hyperscaler details

### Oracle Cloud (OCI) — Carbon Emissions Analysis

Surfaces in the OCI Console under "Emissions Management" and via the Usage API.
Available to all paying commercial OCI tenancies; requires IAM `carbon-emission-reports` read/manage policy.

- **Two calculation modes**:
  - **Power-based** — tracks the kWh consumed by service workloads in OCI data centers and allocates that energy "considering both dedicated and shared hardware across customers". Available only for a subset of OCI native (Gen_2) services.
  - **Spend-based** — `customer pre-discount spend × regional carbon emission factor`. Broader service coverage (effectively any service that produces a usage record). Documented as the "less exact" mode.
- **Default reports (7)**: location-based / market-based footprint by service; by service-and-description; by service-and-SKU; LBM/MBM by region; cumulative footprint by region.
- **Scope mapping**: aligned to GHG Protocol; the docs describe LBM and MBM explicitly. Scope 1 and Scope 3 are not separately surfaced in the customer report.
- **EU regions are reported as zero MBM** by design (Oracle's renewable contracts produce zero market-based emissions in European regions).
- **Embodied hardware**: not included; power-based mode is explicitly operational only.
- **Filters / granularity**:
  - **Temporal**: monthly (default) or daily; standard or cumulative.
  - **Resource**: date range, compartment, region, service, tag, tenant; spend-based mode adds availability domain, platform (Gen_1/Gen_2), product description, subscription ID.
- **Emission factors**: regional grid mix; specific factor values not documented publicly. Tied to the Oracle Clean Cloud OCI Data Sheet.
- **Standards**: GHG Protocol; alignment with EU/UK regulatory requirements cited.
- **Assurance**: none disclosed for the customer-facing tool. Oracle's corporate sustainability disclosure is separate.
- **Important caveat from Oracle's own docs**: "Carbon Emissions Analysis isn't intended to be used as a developer tool to reduce emissions. All customer carbon emissions provided … are estimates."
- **Replicability**: medium. Allocation logic is described qualitatively but emission factors and per-service energy intensities are not tabulated.

### IBM Cloud Carbon Calculator

Surfaces in the IBM Cloud console and via REST API; output can be piped into the separately-licensed IBM Envizi ESG suite.

- **Service coverage**: launched in beta with **Cloud Object Storage, IBM Kubernetes Service, Virtual Server for VPC and Classic**; "more service coverage planned quarterly".
- **Scope**: Scope 1 + Scope 2 emissions associated with IBM Cloud data center operations — IT/network equipment operated by IBM Cloud plus cooling and support infrastructure operated by co-location landlords where assigned to IBM Cloud.
- **Embodied hardware**: **explicitly excluded** — "raw material and manufacturing of equipment, including servers, racks, and networking equipment, is out of scope".
- **Formula**: `total electricity consumption per service × PUE_location × CEF_location`, then summed across service / location / client account.
- **Emission factors**: per-location Carbon Emission Factor (CEF) and per-location PUE.
- **Layered analytics**: ML / "advanced algorithms" cited for pattern + anomaly detection on top of the base electricity model.
- **Granularity**: month / quarter / year; service-level.
- **Standards**: GHG Protocol formatting; "client is responsible for confirming accuracy" disclaimer in the press release footnote.
- **Assurance**: none disclosed for the calculator itself.
- **Methodology document**: versioned ([v3 PDF](https://cloud.ibm.com/media/docs/downloads/account/carbon-calc-method-v3.pdf)). The existence of a v3 implies an iteration history — useful signal that IBM is treating this as a maintained product rather than a one-shot disclosure.
- **API**: a dedicated [Carbon Calculator API](https://cloud.ibm.com/apidocs/carbon-calculator) is published.
- **Replicability**: medium. The formula is explicit and the API is documented, but per-service / per-location PUE and CEF values would need to be cross-referenced from external sources.

### Alibaba Cloud — Energy Expert

Platform-level surface — Energy Expert is itself a paid product, not a built-in console feature of every Alibaba Cloud account. It also serves customers measuring their own (non-cloud) operations.

- **Scope coverage (per Alibaba's docs)**: **Scope 1** (direct ops), **Scope 2** (purchased electricity for production), **Scope 3 (leased computer rooms)** — i.e. emissions where Alibaba Cloud itself is a leaseholder.
- **Energy model**: per-IDC PUE × resource sales × green-power-usage ratio × technical carbon-reduction measures.
- **Allocation chain (explicit, three-stage)**:
  1. IDC level
  2. cloud product level
  3. cloud account level — final attribution to tenants is by the actual amount of cloud resources used.
- **Service coverage**: computing, storage, network, database, CDN; further products planned.
- **Standards**: GHG Protocol Corporate Standard; **ISO 14064-3:2019** (verification / GHG statement inventory guidelines); CEC procedures (China Environment United Certification Center).
- **Assurance**: this is the differentiating point — third-party verification by **Bureau Veritas (Beijing)** for the cloud-customer methodology, plus TÜV Rheinland certification for customer outputs. Alibaba claims "first enterprise in China to pass the evaluation of carbon accounting services for cloud services" (July 2023).
- **Embodied hardware**: not addressed in public docs.
- **Multi-criteria**: none.
- **Methodology document**: surface docs available; full quantification methodology behind the Energy Expert product is not fully public.
- **Replicability**: low–medium. Allocation chain is described but emission factors and per-service intensities are not published.

### Huawei Cloud — Huella Cloud (KooGallery marketplace SaaS)

Important caveat upfront: **Huella Cloud is delivered by a partner via the Huawei Cloud KooGallery marketplace**, not as a native Huawei Cloud sustainability dashboard.
This means Huella is methodologically more comparable to a third-party tool (like DitchCarbon or Cloud Carbon Footprint) than to AWS CCFT or GCP Carbon Footprint.

- **Coverage**: multi-cloud — explicitly markets as covering "the main Cloud Services Providers", with attribution by provider, region, service, and energy-consumption characteristics of customer applications.
- **Modules**: Quantification, Reporting, Reduction (recommendations), Compensation (offset tiles of 1 / 5 / 10 tCO₂e via VCS-certified projects).
- **Granularity**: monthly per-account.
- **Standards / assurance**: VCS (Verified Carbon Standard) for the offset projects; no third-party assurance of the quantification methodology itself.
- **Scope mapping**: not publicly enumerated in Scope 1/2/3 terms.
- **Embodied hardware**: not addressed.
- **Customer-input usability**: weak — because the calculator is multi-cloud and partner-built, the per-Huawei-Cloud allocation is not auditable against Huawei's own emission factors.
- **Replicability**: low.

### Tencent Cloud — *Tier B (no per-customer tool)*

Tencent Cloud publishes corporate sustainability data only; no per-customer cloud carbon dashboard surfaced.

- DC PUE trajectory: 1.8 → 1.2 across DC generations (target PUE < 1.2 in latest builds).
- Energy mix: hydro, wind, biogas, waste-to-energy in site selection; rooftop PV 8–13 MW/campus.
- Specific renewable percentage of total mix not disclosed publicly.
- No third-party certifications cited (ISO 50001, SBTi etc. absent).
- The "Tnebula" internal carbon-management platform exists but is for Tencent's own DC operations, not exposed to customers.

---

## Hyperscaler patterns

**Two methodology families.** Oracle and IBM both follow the "electricity × PUE × emission-factor" pattern that is closest to the Big-3 lineage (AWS CCFT, GCP Carbon Footprint use the same skeleton). Alibaba's three-stage IDC → product → account allocation is also in this family but explicit about the chain.
Huella is in a different category — a third-party multi-cloud overlay rather than a first-party tool.
Tencent doesn't have a tool.

**Embodied hardware is absent except in Alibaba (and even Alibaba doesn't address it publicly).** Both Oracle and IBM explicitly exclude embodied — making their numbers structurally smaller than OVHcloud / Scaleway / AWS-CCFT-post-2024.

**Assurance.** The strongest assurance posture in this entire deep-dive (Tier-A providers across §1 and §2 combined) is **Alibaba's**, with Bureau Veritas data assurance under ISO 14064-3. Methodologically this matters: it's the only customer-facing cloud carbon tool where an independent auditor has verified the *data* (not just the methodology document).

**Scope-3 treatment.**
- Oracle: not explicit at the customer level (LBM/MBM only).
- IBM: explicitly Scope 1+2 only.
- Alibaba: includes "Scope 3 — leased computer rooms" — narrow but the most-named Scope-3 category in this set.
- Huawei (via Huella): not enumerated.

**rSCI implication.** Three of the five non-Big-3 hyperscalers either explicitly exclude embodied hardware (Oracle, IBM) or do not address it (Huawei). This means the customer-attributed numbers from these tools are by construction *smaller* than the provider's true Scope-3 footprint, leaving a residual that is, for these providers, the entire embodied-carbon stream. The rSCI residual decomposition is a natural fit precisely for this gap.

**Notable caveats / honesty markers.**
- Oracle: "isn't intended to be used as a developer tool to reduce emissions" — i.e. Oracle is on record that the tool is for reporting, not workload-shaping.
- IBM: "client is responsible for confirming accuracy" footnote.
- Both of these are useful in the paper as direct provider acknowledgement that the published number is an estimate.

## Notable cross-cutting observations from the OVHcloud read

A few methodology choices in the OVHcloud PDF are worth lifting into the rSCI discussion because they directly shape the residual:

- **100% / 24/7 baseline.** Without per-server power telemetry, customer numbers are *over-estimates*. This is the opposite direction of most hyperscaler tools, which tend to under-report. The implication for rSCI: residual decomposition has to handle both signs of bias depending on provider modelling choice.
- **Operations allocated equally per dedicated server.** Customer-specific Operations share is independent of usage — a flat per-server overhead. This is honest about the limitation and is exactly the kind of "burden into customer / kept on provider / omitted" split that rSCI's overhead-treatment dimension is meant to surface.
- **Mutualized vs dedicated split.** OVHcloud applies fundamentally different allocation rules to its dedicated and public-cloud products. Two customers with the same workload but different procurement model will get carbon numbers built from different equations — relevant when reconciling across product lines.
- **Per-DC electricity factors from a public open-licensed dataset (Electricity Maps).** This is replicable by anyone; combined with the published per-DC PUE/WUE table, it means OVHcloud is closer to "auditable in public" than any of the other Tier-A providers.

---

# Big-3 Hyperscalers (AWS / Azure / GCP)

Primary source: `HYPERSCALER_CARBON_ACCOUNTING.md` (May 2026), built from each provider's latest methodology document (AWS CCFT Model 3.0 Oct 2025; Azure Emissions Methodology Jan 2026 + CHEM whitepaper 2026; GCP Carbon Footprint methodology docs + Schneider & Mattia 2024).
This section folds those findings into the same Tier-A schema used above.

## Big-3 matrix

| Provider | Surface | Scopes | Embodied HW | Energy model | Allocation key | Standards | Assurance | Multi-criteria | Methodology doc |
|---|---|---|---|---|---|---|---|---|---|
| **AWS** — Sustainability Console (built on CCFT, launched 31 Mar 2026) | **AWS Sustainability Console** + REST API (`get-estimated-carbon-emissions`) + SDK + CLI + filterable CSV export; standalone IAM permissions (no Billing access needed); 38-mo retention; data back to Jan 2022; ≤21-day lag; monthly granularity; fiscal-year configurable | S1, S2 LBM+MBM, **S3 Cat 2 (full incl. buildings + non-IT)**, S3 Cat 3 (FERA), S3 Cat 4 (upstream transport). Cat 5/6/7/9/12 excluded. | **Yes** — component-level hybrid LCA (4-pathway waterfall: PLCA-Eng → Extrap. → RCA-LCA → Component-EIO-LCA). Buildings added Oct 2025. IT 6 yr, buildings 50 yr; zero past amortization. | **Foundational services**: instance-hours (described as physical); **non-foundational services**: equivalent-revenue (economic allocation). List of non-foundational services not published. | Instance-hours per service × region × account; revenue-proportional for non-foundational; filterable by Region/service/account/Scope | GHG Protocol Corporate + Scope 3; Scope 2 Guidance; ISO 14064-1:2018 | **Apex Companies LLC** — ISO 14064-3:2019 limited assurance, ±5% materiality; covers Scope 3 Cat 2/3/4 methodology; **Scope 1, Scope 2, and tool implementation not in assurance boundary** | None | [Sustainability Console landing](https://aws.amazon.com/sustainability/tools/console/) · [Launch blog (Mar 2026)](https://aws.amazon.com/blogs/aws/announcing-the-aws-sustainability-console-programmatic-access-configurable-csv-reports-and-scope-1-3-reporting-in-one-place/) · [Methodology PDF (Model 3.0, Oct 2025)](https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-methodology.pdf) · [Assurance statement](https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf) |
| **GCP** — Carbon Footprint | Console + **BigQuery export API**; unlimited retention; ~15-day lag | S1, S2 LBM+MBM (hourly internal), **S3 Cat 2 (full incl. buildings)**, S3 Cat 3 (FERA), **Cat 6 (business travel)**, **Cat 7 (employee commuting)**. Cat 5/9/12 excluded. End-of-life excluded. | **Yes** — component-level LCA, Fraunhofer IZM critical review. IT **4 yr** (financial accounting), buildings included; zero past amortization. | **Two-stage**: (1) internal — machine-level Borg power telemetry; dynamic power proportional to GCU usage, idle power (~60%) allocated by resource-weighted shares. (2) customer — vCPU-hours × **price-proportional** SKU factor (list price; CUDs/SUDs excluded). Non-electricity Scope 3 by **customer-electricity / total-electricity ratio**. | vCPU-hours per SKU × region × project; proportional ratio for non-electricity Scope 3 | GHG Protocol Corporate + Scope 3; Scope 2 Guidance | **Fraunhofer IZM critical review** (ISO 14040/14044) of LCA methodology only; **no formal ISO 14064-3 GHG assurance**; tool not audited | None at customer surface; per-region hourly **CFE %** reported separately | [Methodology docs](https://docs.cloud.google.com/carbon-footprint/docs/methodology) · [Schneider & Mattia 2024 (arXiv:2406.09645)](https://arxiv.org/abs/2406.09645) |
| **Azure** — Emissions Impact Dashboard (EID) + Carbon Optimization (CO) | Power BI / Microsoft Fabric (EID, ≤60-mo retention); Azure portal + **REST API** (CO, 12-mo retention); ~19-day lag | S1, S2 LBM+MBM, **S3 Cat 1 (purchased goods)**, Cat 2 (IT only — **buildings excluded**), Cat 4 (upstream transport), **Cat 5 (waste)**, **Cat 9 (downstream transport)**, **Cat 12 (end-of-life)**. **FERA (Cat 3) excluded.** | **Yes** — CHEM whitepaper (process-based LCA, PDM/FMD data, Makersite mapping, imec SSTS for semis, ecoinvent). IT 6 yr; **buildings excluded; end-of-life included (uniquely)**. | **"Usage" — undisclosed parameters.** 2021 whitepaper: "normalized cost metric… normalized to exclude discounts". 2025 docs: "compute/storage/data-transfer time". Internal derivation not disclosed. | Service category × region × subscription (EID) or resource_group × resource (CO) | GHG Protocol Corporate + Scope 3 | **WSP USA** — covers Scope 3 methodology document only; tool implementation not audited. Microsoft explicitly acknowledges that **the customer-facing methodology differs from corporate disclosure** and has not reconciled the two. | None | [Azure emissions calculation methodology (Jan 2026)](https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology) · [CHEM whitepaper (2026)](https://datacenters.microsoft.com/wp-content/uploads/2026/01/Whitepaper_Cloud-hardware-emissions-methodology.pdf) · [Carbon Optimization](https://learn.microsoft.com/en-us/azure/carbon-optimization/overview) |

Quick read at the rSCI level:
- **None of the Big-3 reflects compute utilization in the customer-reported number** — a VM at idle and a VM at full load produce the same carbon for the same SKU × duration. This is the single most important practical finding for rSCI.
- **GCP is the most transparent** (hourly internal telemetry, published two-stage methodology, peer-reviewed in Schneider & Mattia 2024), but exposes only monthly data at the customer surface.
- **AWS is the only Big-3 provider with formal GHG assurance** (Apex, ISO 14064-3:2019 limited) — but the assurance boundary is Scope 3 methodology only; Scopes 1 & 2 and the tool implementation are outside it.
- **Azure's customer tool is on record as not reconciling with Microsoft's corporate disclosure** (2021 Scope 3 Whitepaper, footnote 2) — this is a direct, provider-acknowledged residual.

---

## Big-3 details (compact)

Detail is in `HYPERSCALER_CARBON_ACCOUNTING.md`. The compact takes below reframe the highlights in rSCI-relevant terms.

### AWS — Sustainability Console (Model 3.0 methodology)

- **March 2026 launch of the Sustainability Console** is the material recent change.
  CCFT continues to exist; the Sustainability Console is a unified replacement experience with **a real public API** (`get-estimated-carbon-emissions`), AWS SDK + CLI access, filterable CSV exports (Region / service / account / Scope), preset monthly and annual reports, fiscal-year configuration, and independent IAM permissions decoupled from Billing.
  Data back to January 2022; emissions returned in MTCO₂e with LBM and MBM in parallel.
- **Allocation tiering**: foundational services ("dedicated server racks") get usage allocation (instance-hours); non-foundational services ("no dedicated server racks") get **revenue-proportional** allocation. The list of non-foundational services is **not published**, nor is the share of total CCFT emissions under economic allocation.
- **Embodied carbon waterfall**: PLCA-Eng → ML-extrapolation → Representative Category Average LCA (K-NN) → Component-EIO-LCA (cost-based fallback, NAICS sector factors). Pathway distribution across the fleet not disclosed.
- **Lifetimes**: IT 6 yr; buildings 50 yr; zero past amortization. A 30-yr building assumption would raise annual building embodied carbon by ~67% (arithmetic identity).
- **EAC matching**: not disclosed; assumed annual.
- **What's missing for rSCI**: foundational/non-foundational service split, EAC temporal matching, share of fleet on each LCA pathway. Cat 5/6/7/9/12 excluded without published materiality assessment.

### GCP — Carbon Footprint

- **Internal model**: machine-level Borg power telemetry; dynamic vs idle decomposition; idle power (~60% of average server energy) allocated by resource-weighted shares of GCU/RAM.
- **Customer model**: energy per usage unit is **proportional to list price**, with usage measured in vCPU-hours / GiB-months. Schneider & Mattia (§3.6) explicitly note: customers do not receive a signal about how switching SKUs reduces *actual* emissions, only *allocated* emissions based on list prices.
- **Non-electricity Scope 3**: proportional to customer-electricity / total-electricity ratio — assumes embodied/FERA/transport tracks electricity consumption, which doesn't hold across CPU vs GPU workload mixes.
- **Lifetimes**: IT **4 yr** (financial accounting; GCP acknowledges real lifetimes are longer); produces 50% higher annual amortized embodied carbon than AWS/Azure 6-yr for the same hardware.
- **Hourly CFE % per region** is the only sub-monthly carbon signal published by any Big-3 to customers.
- **Assurance**: Fraunhofer IZM critical review on LCA only; no formal ISO 14064-3 engagement for the tool.

### Azure — EID + Carbon Optimization

- **Two surfaces, different granularity**: EID is subscription × service × region (Power BI); Carbon Optimization is resource_group × resource (12-mo retention, REST API, Azure Advisor recommendations with estimated carbon + cost savings).
- **Usage factor ambiguity**: 2021 whitepaper defines usage as a "normalized cost metric" (economic); 2025 docs describe it as "compute/storage/data-transfer time" (resource-time). Unclear whether evolution or terminology shift. Per-region usage-factor derivation not disclosed.
- **Scope 3 breadth, but key gaps**: 6 categories (Cat 1, 2, 4, 5, 9, 12) — broadest count in the Big-3 — but **excludes FERA (Cat 3) and building embodied carbon**. Uniquely includes Cat 12 end-of-life.
- **Recasting**: 12-month window only — too short for GHG Protocol base-year recalculation on methodology change. EID's 60-month retention mitigates trend analysis but not the recast scope.
- **Microsoft explicitly acknowledges** the customer-tool methodology differs from corporate disclosure (Scope 3 Whitepaper, footnote 2). The two numbers have not been reconciled.
- **CHEM** shifted Microsoft's embodied-carbon modeling from financial proxies to process-based LCA — a methodology track separate from customer-level allocation.

---

## Big-3 cross-cutting patterns

The eight observations in `HYPERSCALER_CARBON_ACCOUNTING.md §15` are largely directly portable into the unified rSCI framing. The ones most load-bearing here:

1. **All three use usage-time allocation at the customer surface, none reflects compute utilization.** This is the single most important practical finding. A VM at 5% CPU and a VM at 95% CPU report the same carbon for the same SKU × duration. The rSCI residual is precisely the gap between this allocation and a utilization-honest one.
2. **Verification claims are narrower than they appear.** AWS Apex covers Scope 3 methodology Cat 2/3/4 only at limited assurance. Azure WSP covers methodology document only. GCP Fraunhofer covers LCA methodology only. **No Big-3 has its customer-facing tool independently audited end-to-end.**
3. **GHG Protocol is under-specified for cloud.** Allocation of shared infrastructure, equipment lifetime, building embodied carbon inclusion, EAC temporal matching — all under-specified. The interpretive divergence across AWS/GCP/Azure is therefore *not* protocol violation; it's protocol ambiguity. The rSCI framework should treat this as a feature, not a bug, of the gap to be reconciled.
4. **All three report zero embodied carbon past amortization window** (AWS/Azure 6 yr, GCP 4 yr). Fleet-wide monthly Scope 3 mechanically decreases as fleet ages past the assumed lifetime — independent of any actual change in environmental impact.

---

# Schema adaptations the Big-3 read forces

The deep-dive's §9 schema (from `CLOUD_CARBON_ACCOUNTING_INVENTORY.md`) needs the following adjustments before it can faithfully capture both the Big-3 and the rest. Each item below is a dimension the current schema either lacks, conflates, or under-specifies.

1. **Split "energy model" into internal vs customer-facing.** The current schema has one "energy model" cell. But GCP measures power physically at the machine level internally, then re-aggregates by price-proportional SKU factors at the customer boundary. Folding both into one column obscures the most consequential thing about GCP. *Proposed columns:* `internal_energy_model` and `customer_facing_energy_model`.
2. **Add "compute-utilization-reflected" (boolean).** None of the Big-3 reflects actual CPU/GPU utilization in the customer number, and neither does OVHcloud (100%-24/7 baseline). This deserves its own column rather than being buried in "allocation key". *Proposed:* `reflects_compute_utilization: y/n + brief explanation`.
3. **Add "economic-allocation share / disclosed?".** AWS's foundational-vs-non-foundational split applies revenue-proportional allocation to an undisclosed fraction of customers' bills. The share is the single biggest opacity in CCFT. Worth being a first-class dimension. *Proposed:* `economic_allocation_share` and `economic_allocation_disclosed: y/n`.
4. **Split "assurance" into methodology-level and tool-implementation-level.** AWS Apex covers Model 3.0 methodology; Azure WSP covers the Scope 3 methodology document; GCP Fraunhofer covers LCA only. **None covers tool implementation.** Conflating these in one cell hides exactly the thing that matters for rSCI. *Proposed:* `methodology_assurance`, `tool_implementation_assurance`, `assurance_standard`, `assurance_level`.
5. **Add "reconciles with corporate Scope-1/2/3 disclosure?".** Azure is on record that its customer tool does **not** reconcile with Microsoft's corporate disclosure. None of the others has reconciled either. This is **literally the rSCI residual question** — should be the headline schema dimension. *Proposed:* `reconciles_with_corporate_disclosure: y/n + delta`.
6. **Add "post-amortization treatment".** All Big-3 (and OVHcloud) zero out embodied past the lifetime window. This is a fleet-wide mechanical decrease that has nothing to do with actual environmental impact. Belongs in the schema. *Proposed:* `post_amortization_treatment: zero / continue / not-applicable`.
7. **Split temporal granularity into internal and customer-facing.** GCP runs hourly internally, exposes monthly to customers. Fastly is daily. OVHcloud is monthly. This is an information-loss step distinct from update lag. *Proposed:* `internal_temporal_granularity` and `customer_facing_temporal_granularity`.
8. **Add "historical recasting policy".** Azure's 12-month recast window is a GHG-Protocol-level problem; AWS recasts to Jan 2020; GCP recasts unlimited via BigQuery. The current schema does not capture this. *Proposed:* `recast_scope` and `retention`.
9. **Add "materiality assessment for excluded categories".** GHG Protocol requires that exclusions be justified by materiality assessment. **No provider publishes one.** Worth tracking explicitly because it's a universal gap. *Proposed:* `materiality_assessment_published: y/n`.
10. **Add "EAC/PPA temporal matching" as its own dimension.** Currently buried under Block D as one bullet. The difference between annual EACs (AWS/Azure assumed) and hourly CFE matching (GCP) is the gap between GHG-Protocol-acceptable and GSF-Real-Time-Energy-Carbon-Standard-aligned. *Proposed:* `eac_matching_granularity: annual / monthly / hourly / not-disclosed`.
11. **Add "API access" as a first-class column** (not just a free-text channel description). AWS Sustainability Console (since 31 Mar 2026) ships a first-class REST API + SDK + CLI + filterable CSV — the most ergonomic in the Big-3; GCP exports to BigQuery (powerful but requires customer-side setup); Azure has a REST API for Carbon Optimization + Power BI for EID. Within this set, OVHcloud and Akamai have customer-facing reports but no public API. This dimension affects whether a customer can mechanise rSCI computations.
12. **Reconsider "Scope 3 categories named" as a count plus a category-mask.** Current schema treats S3 as a text field. For comparison, what we actually want is the 15-bit category mask (Cat 1–15 each y/n/excluded). The Big-3 already differ on which categories they include, and the differences aren't visible without explicit per-category status. *Proposed:* a per-Cat boolean array.

The non-rSCI implication of these adaptations: the schema as it stood would have hidden the most important Big-3 finding (Azure's deliberate non-reconciliation with corporate disclosure) in the assurance column.
After these changes the schema is cleaner *and* directly answers the rSCI residual question for every provider.
