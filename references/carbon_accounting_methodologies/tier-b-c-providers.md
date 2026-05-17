# Tier-B / Tier-C providers — no customer-facing carbon tools

Providers without per-customer carbon dashboards. Listed for inventory completeness; **not directly usable as Scope-3 customer input** under rSCI. Sourced from the deleted `CLOUD_CARBON_ACCOUNTING_INVENTORY.md` plus the per-provider sections of `CLOUD_CARBON_ACCOUNTING_DEEPDIVE.md`.

## Tier B — corporate disclosure only

Provider publishes corporate-level Scope 1/2/3 data, but no customer-allocated number.

### Rackspace
- Status: **Report** (corporate-level).
- SBTi-validated net-zero targets (50% by 2032, 90% by 2045).
- Third-party-audited Scope 1/2/3 baseline.
- 80% renewable across global DCs.
- Customer-facing offering is consulting (Workload Aware Modernization), not a carbon dashboard.
- Refs: [2025 Sustainability Report](https://www.rackspace.com/newsroom/rackspace-technology-releases-2025-sustainability-report), [SBTi approval press](https://www.rackspace.com/newsroom/rackspace-receives-sbti-approval-net-zero-targets).

### DigitalOcean (+ Paperspace)
- Status: **Report**.
- Publishes ESG microsite; no per-customer carbon data, no SBTi or CDP participation.
- PUE-only operational disclosure (~1.15).
- Inherits energy mix from colocation partners (e.g. Equinix); does not state per-region energy policy.
- Refs: [Impact page](https://www.digitalocean.com/impact), [IR ESG](https://investors.digitalocean.com/esg/esg-overview/default.aspx).

### UpCloud
- Status: **Report**.
- First ESG report published 2024.
- 70% of DCs on renewable electricity; remainder mixed-grid + offsetting.
- ISO 14001 (energy management) and ISO 27001.
- Green Web Foundation verified.
- Identified own largest emissions source as DC hardware purchases.
- Refs: [2024 year-in-review](https://upcloud.com/2024-year-in-review/), [Green Web Provider blog](https://upcloud.com/blog/were-a-green-web-provider/).

### GleSYS
- Status: **Report**.
- 2024 sustainability report with CSRD-aligned baseline.
- 100% renewable electricity; market-based Scope 2 = 0.22 tCO₂e from district heating; total 1,956 tCO₂e (2024).
- Energy Reuse Factor 84% (recovered heat into Falkenberg district heating, 4.8 GWh).
- PUE 1.28 group-wide.
- Targets: -99% Scope 1 by 2030, fossil-free backup by 2030.
- Refs: [Sustainability](https://glesys.com/sustainability/), [2024 report](https://glesys.com/blog/glesys-releases-2024-sustainability-report-and-establishes-csrd-aligned-baseline-edited/).

### Crusoe
- Status: **Report**.
- First ESG report 2022.
- Business model is the disclosure: Digital Flare Mitigation diverts otherwise-flared gas into compute — reports volumetric methane / flared-gas avoidance (~5.4 Bcf flared gas avoided, ~8,500 t methane avoided, ~635,000 MWh generated in 2023).
- Per-GPU reduction claim of ~4.4 tCO₂e/yr.
- No per-customer allocated emissions tool.
- Refs: [2022 ESG Report PDF](https://crusoe-public.s3.us-east-2.amazonaws.com/Crusoe_ESG+Report_2023.05.10.pdf), [resources blog](https://www.crusoe.ai/resources/blog/crusoe-tallys-law-leading-energy-transition).
- *Note for rSCI*: the DFM "avoided emissions" framing sits awkwardly against rSCI's residual model.

### Nebius (formerly Yandex international)
- Status: **Report**.
- 2024 Sustainability Report.
- Claims 94% low-carbon electricity, 0.04 tCO₂e/MWh market-based intensity.
- Finland DC reportedly provides 65% of local municipality heating via heat reuse.
- Iceland / Paris / UK sites stated as 100% renewable.
- Scope 3 and water consumption reportedly absent from disclosure (flagged externally as a transparency gap).
- Refs: [Sustainability hub](https://nebius.com/sustainability), [2024 report announcement](https://nebius.com/newsroom/nebius-group-2024-sustainability-report-highlights-importance-of-sustainability-to-long-term-value-creation-in-ai-infrastructure).

### Verne (Iceland/Finland)
- Status: **Report**.
- 2024 Iceland-campus emissions: 556.25 tCO₂e total (S1 9.1%, S2 80.4%, S3 10.4%).
- 100% renewable power on Iceland campus; three Finland DCs on renewable power.
- No per-customer tool.
- Refs: [Sustainability](https://www.verne.co/about-us/sustainability).

### Infomaniak
- Status: **Report**.
- ISO 14001:2015 (SGS-audited annually) and ISO 50001.
- Scope includes raw materials, production, transport, waste, employee commute.
- PUE 1.06 (air-cooled, no water cooling).
- 200% offset via Myclimate Foundation (gap from internal reductions).
- Server lifetime extended to 15 years.
- No per-customer carbon dashboard.
- Refs: [Ecology page](https://www.infomaniak.com/en/ecology), [200% offset blog](https://news.infomaniak.com/en/infomaniak-offsets-twice-as-many-co-emissions/), [Eco-design FAQ](https://www.infomaniak.com/en/support/faq/1160/eco-design-to-reduce-carbon-footprint).

### Salesforce / Heroku
- Status: **Report**.
- Carbon-neutral corporate cloud claim.
- Internal KPI "Carbon to Serve" (DC emissions ÷ application work done); reported -26% since 2020.
- Hyperforce positioned as 100% renewable architecture.
- No per-app or per-account customer emissions surface on Heroku — only inheritance of the corporate-level claim.
- Refs: [Sustainability hub](https://www.salesforce.com/company/sustainability/), [Net Zero Cloud product](https://www.salesforce.com/products/sustainability-cloud/overview/), [Green Code initiative](https://www.salesforce.com/news/stories/green-code-software/), [Heroku KB](https://help.heroku.com/2163BDDI/is-my-app-carbon-neutral).

### Leafcloud
- Status: **Claim** (operational metrics + heat-reuse model; no per-customer dashboard).
- PUE 1.02, ERE ~0.15, ~85% heat capture.
- Heat-reuse model places servers inside buildings that need heat (pools, apartments, nursing homes).
- Refs: [Truly Green landing](https://leaf.cloud/truly-green), [Green-cloud explainer](https://leaf.cloud/blog/green-cloud-energy-use-and-residual-heat-what-actually-makes-a-cloud-sustainable).

### Open Telekom Cloud (T-Systems / Deutsche Telekom)
- Status: **Claim**.
- Climate Neutral Data Centre Pact signatory.
- 100% green-electricity purchase for DCs (Biere/Magdeburg PUE 1.28; Aalsmeer/Almere 1.46/1.40).
- Deutsche Telekom corporate CR report covers Scopes 1/2/3.
- No per-customer cloud carbon tool surfaced.
- Refs: [Sustainability page](https://www.open-telekom-cloud.com/en/benefits/sustainability), [Telekom CR report 2024 PDF](https://report.telekom.com/cr-report/2024/_assets/downloads/env-environment-dtag-cr24.pdf).

### atNorth
- Status: **Report**.
- Sustainability strategy + Nordic-grid-mix disclosure.
- No first-party emissions report at provider level surfaced; no per-customer tool.
- Refs: [Sustainability strategy](https://www.atnorth.com/sustainability/sustainability-strategy/).

### Tencent Cloud
- Status: **Report** (corporate-only).
- DC PUE trajectory: 1.8 → 1.2 across DC generations (target PUE < 1.2 in latest builds).
- Energy mix: hydro, wind, biogas, waste-to-energy in site selection; rooftop PV 8–13 MW/campus.
- Specific renewable percentage of total mix not disclosed publicly.
- No third-party certifications cited.
- The "Tnebula" internal carbon-management platform exists but is for Tencent's own DC operations, not exposed to customers.
- Refs: [Sustainability page](https://www.tencentcloud.com/global-infrastructure/sustainability), [2024 ESG report](https://static.www.tencent.com/uploads/2025/04/08/00ef711d9596ce09344c0260b14cda7e.pdf).

## Tier C — marketing claims only

Marketing-level renewable/PUE statements; no methodology and no per-customer accounting. Listed for completeness only.

| Provider | Category | Published | Source |
|---|---|---|---|
| Hetzner | Tier-2 | Solar-generation shift (HT clean energy GmbH 2025); CSRD reporting from 2026; PUE 1.13 | [Sustainability](https://www.hetzner.com/unternehmen/nachhaltigkeit) |
| Vultr | Tier-2 | Net-zero 2029; 2026 focus on GPU orchestration (NVIDIA Rubin) and silicon efficiency | [Impact](https://www.vultr.com/about/sustainability/) |
| STACKIT | Sovereign EU | Green-electricity DCs in DE/AT; DC10 Ostermiething PUE 1.1; Schwarz Group net-zero-by-2050 | [Sustainability](https://stackit.com/en/learn/knowledge/cloud/sustainability) |
| GreenGeeks | Niche green | REC-based "300% renewable" via Bonneville Environmental Foundation; US EPA Green Power Partner since 2009 | [Going green](https://www.greengeeks.com/going-green) |
| Krystal | Niche green | Direct renewable PPAs preferred over RECs; Gold-Standard projects; tree-planting via Veritree | [Green hosting](https://krystalhosting.com/green) |
| CoreWeave | AI/GPU | Sustainability strategy stated (clean energy, efficiency, recycling); Scope 1/2 measurement "in progress"; no formal targets or methodology | [About](https://www.coreweave.com/about-us), [FY25 10-K](https://s205.q4cdn.com/133937190/files/doc_financials/2025/q4/CoreWeave-Inc-FY25-10-K-7.pdf) |
| Lambda | AI/GPU | Marketing references to "zero-emissions energy standards" at Mountain View; no report or methodology | [Site](https://lambda.ai/) |
| Hyperstack (NexGen) | AI/GPU | 100% renewable marketing claim; Tier-3 DC partnerships; AQ Compute "net-zero AI supercloud" | [Site](https://www.hyperstack.cloud/), [AQ Compute blog](https://www.hyperstack.cloud/blog/company-news/nexgen-cloud-and-aq-compute-advance-towards-net-zero-ai-supercloud) |
| DataCrunch | AI/GPU | Helsinki + Iceland sites; waste-heat reuse claim; no formal report | [Clusters](https://datacrunch.io/clusters), [TechCrunch](https://techcrunch.com/2024/10/21/datacrunch-wants-to-be-europes-first-ai-cloud-hyperscaler-powered-by-renewable-energy/) |
| RunPod | AI/GPU | Nothing found | n/a |
| Paperspace | AI/GPU | Acquired by DigitalOcean — inherits DO Tier-B | n/a |
| Together AI / Fireworks AI / Replicate | AI/GPU | Nothing found | n/a |
| Vercel | PaaS | "Green energy policy" KB only; emissions inherited from underlying cloud providers | [KB](https://vercel.com/kb/guide/what-is-vercel-green-energy-policy) |
| Netlify | PaaS | "Jamstack/CDN is intrinsically lower-emission" narrative; no per-customer accounting | [Sustainability](https://www.netlify.com/sustainability/) |
| Fly.io | PaaS | Community thread only | [Thread](https://community.fly.io/t/carbon-emissions/4345) |
| Render | PaaS | Inherits AWS/GCP — no first-party disclosure | [Thread](https://community.render.com/t/does-render-use-green-energy/912) |

## Adjacent open-source / independent references

Not providers, but routinely cited methodologically:

- Cloud Carbon Footprint (open-source tool): https://www.cloudcarbonfootprint.org/docs/methodology/
- Green Web Foundation — green-power evidence policy: https://www.thegreenwebfoundation.org/what-we-accept-as-evidence-of-green-power/
- DitchCarbon provider directory (third-party emissions estimates): https://ditchcarbon.com/
- Carbone 4 — analysis of hyperscaler footprints: https://www.carbone4.com/en/analysis-carbon-footprint-cloud
- Computing.co.uk neocloud sustainability analysis: https://www.computing.co.uk/research/2026/sustainability-mirage-heart-of-neocloud
