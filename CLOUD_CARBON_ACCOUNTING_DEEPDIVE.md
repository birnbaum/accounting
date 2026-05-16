# Cloud Carbon Accounting — Methodology Deep-Dive (Non-Hyperscaler)

Companion to `CLOUD_CARBON_ACCOUNTING_INVENTORY.md`.
Compiled 2026-05-16.

Scope: every non-hyperscaler provider in §2–§7 of the inventory.
Out of scope: hyperscalers (§1, deferred to a separate file), colocation providers, adjacent open-source tools (§8).
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

## Notable cross-cutting observations from the OVHcloud read

A few methodology choices in the OVHcloud PDF are worth lifting into the rSCI discussion because they directly shape the residual:

- **100% / 24/7 baseline.** Without per-server power telemetry, customer numbers are *over-estimates*. This is the opposite direction of most hyperscaler tools, which tend to under-report. The implication for rSCI: residual decomposition has to handle both signs of bias depending on provider modelling choice.
- **Operations allocated equally per dedicated server.** Customer-specific Operations share is independent of usage — a flat per-server overhead. This is honest about the limitation and is exactly the kind of "burden into customer / kept on provider / omitted" split that rSCI's overhead-treatment dimension is meant to surface.
- **Mutualized vs dedicated split.** OVHcloud applies fundamentally different allocation rules to its dedicated and public-cloud products. Two customers with the same workload but different procurement model will get carbon numbers built from different equations — relevant when reconciling across product lines.
- **Per-DC electricity factors from a public open-licensed dataset (Electricity Maps).** This is replicable by anyone; combined with the published per-DC PUE/WUE table, it means OVHcloud is closer to "auditable in public" than any of the other Tier-A providers.
