# Cloud Provider Carbon Accounting Inventory

Comprehensive inventory of customer-facing carbon accounting offerings across cloud providers.
Sources collected for later methodology comparison.
No judgement applied yet — providers are grouped by market position, not by quality of disclosure.

Status legend (rough first pass, refine later):
- **Tool** — provider exposes per-customer emissions data in a console/dashboard/API.
- **Report** — provider publishes corporate-level sustainability/ESG report only, no per-customer tool.
- **Claim** — only marketing-level renewable-energy or PUE claims found, no quantitative customer-facing data.
- **None** — nothing customer-facing found.

---

## 1. Hyperscalers

### AWS — Customer Carbon Footprint Tool (CCFT)
Status: **Tool**.
- Landing page: https://aws.amazon.com/sustainability/tools/aws-customer-carbon-footprint-tool/
- Console docs: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/what-is-ccft.html
- Overview & coverage: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-overview.html
- Estimation method: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-estimation.html
- Methodology PDF (v3.0): https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-methodology.pdf
- Methodology assurance PDF: https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf
- Amazon-wide carbon methodology: https://sustainability.aboutamazon.com/carbon-methodology.pdf
- Release notes: https://docs.aws.amazon.com/ccft/latest/releasenotes/what-is-ccftrn.html
- Scope-3 expansion blog: https://aws.amazon.com/blogs/aws/aws-customer-carbon-footprint-tool-now-includes-scope-3-emissions/
- Methodology-update blog: https://aws.amazon.com/blogs/aws-cloud-financial-management/updated-carbon-methodology-for-the-aws-customer-carbon-footprint-tool/
- New AWS Sustainability console (CSV / Scope 1–3 / API): https://aws.amazon.com/blogs/aws/announcing-the-aws-sustainability-console-programmatic-access-configurable-csv-reports-and-scope-1-3-reporting-in-one-place/

Notes: third-party assured by Apex; default view is market-based, LBM toggleable; includes FERA.

### Microsoft Azure — Emissions Impact Dashboard (EID)
Status: **Tool**.
- Product page: https://www.microsoft.com/en-us/sustainability/emissions-impact-dashboard
- Power BI connector (Azure): https://learn.microsoft.com/en-us/power-bi/connect-data/service-connect-to-emissions-impact-dashboard
- Power BI connector (M365): https://learn.microsoft.com/en-us/power-bi/connect-data/service-connect-emissions-impact-dashboard-microsoft-365
- Marketplace listing: https://marketplace.microsoft.com/en-us/product/power-bi/coi-sustainability.emissions_impact_dashboard?tab=overview
- Reference architecture: https://learn.microsoft.com/en-us/industry/well-architected/sustainability/emissions-impact-dashboard-architecture
- Monitoring guidance: https://learn.microsoft.com/en-us/industry/well-architected/sustainability/emissions-impact-dashboard-centralized-monitoring
- Sustainability Manager connector: https://learn.microsoft.com/en-us/industry/sustainability/sustainability-manager-import-data-emissions-impact-dashboard-connector
- Azure emissions calculation methodology (Learn): https://learn.microsoft.com/en-us/power-bi/connect-data/azure-emissions-calculation-methodology
- Carbon Optimization (separate, in-console): https://learn.microsoft.com/en-us/azure/carbon-optimization/overview
- Carbon Optimization data view: https://learn.microsoft.com/en-us/azure/carbon-optimization/view-emissions
- Well-Architected sustainability methodology: https://learn.microsoft.com/en-us/azure/well-architected/sustainability/sustainability-design-methodology
- Empowering cloud sustainability (blog): https://azure.microsoft.com/en-us/blog/empowering-cloud-sustainability-with-the-microsoft-emissions-impact-dashboard/
- 2018 Microsoft cloud carbon study PDF (Stanford-validated baseline): https://download.microsoft.com/download/7/3/9/739BC4AD-A855-436E-961D-9C95EB51DAF9/Microsoft_Cloud_Carbon_Study_2018.pdf
- Cloud Hardware Emissions Methodology (CHEM) whitepaper PDF: https://datacenters.microsoft.com/wp-content/uploads/2026/01/Whitepaper_Cloud-hardware-emissions-methodology.pdf
- Carbon-aware computing whitepaper PDF: https://msftstories.thesourcemediaassets.com/sites/418/2023/01/carbon_aware_computing_whitepaper.pdf
- "GreenSKU" research paper (ISCA 2024): https://www.microsoft.com/en-us/research/wp-content/uploads/2024/03/2024-GreenSKU-ISCA2024.pdf
- Sustainability/Net-zero ebook PDF: https://download.microsoft.com/download/7/2/8/72830831-5d64-4f5c-9f51-e6e38ab1dd55/Azure_Sustainability_Carbon_IT_e-book.pdf

Notes: EID covers Scopes 1/2/3; Feb-2024 update introduced finer attribution for Global/Null regions; methodology aligned to GHG Protocol, third-party verified per ISO 14064-3.

### Google Cloud — Carbon Footprint
Status: **Tool**.
- Product page: https://cloud.google.com/carbon-footprint
- Methodology: https://docs.cloud.google.com/carbon-footprint/docs/methodology
- View data: https://docs.cloud.google.com/carbon-footprint/docs/view-carbon-data
- Release notes: https://docs.cloud.google.com/carbon-footprint/docs/release-notes
- Per-region carbon-free energy %: https://cloud.google.com/sustainability/region-carbon
- Architecture-framework sustainability section: https://docs.cloud.google.com/architecture/framework/sustainability/continuously-measure-improve
- Sustainability hub: https://cloud.google.com/sustainability

Notes: customer-allocated Scopes 1/2/3 of Google Cloud; semi-annual methodology revisions; third-party review statement linked from methodology page.

### Oracle Cloud (OCI) — Carbon Emissions Analysis
Status: **Tool**.
- Docs entry: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/emissions-management.htm
- Viewing carbon emissions reports: https://docs.oracle.com/en-us/iaas/Content/General/Tasks/carbon-analysis-viewreports.htm
- Power-based calculation release note: https://docs.public.content.oci.oraclecloud.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm
- How-to-enable KB: https://support.oracle.com/knowledge/Oracle%20Cloud/3000157_1.html
- Technical carbon calculation guidance PDF: https://www.oracle.com/a/ocom/docs/corporate/technical-carbon-calculation-guidance.pdf
- Renewable energy guidance PDF: https://www.oracle.com/a/ocom/docs/renewable-energy-guidance.pdf
- Clean Cloud OCI data sheet (FY25): https://www.oracle.com/a/ocom/docs/corporate/citizenship/clean-cloud-oci.pdf
- Green Cloud landing: https://www.oracle.com/sustainability/green-cloud/
- Sustainability hub: https://www.oracle.com/sustainability/

Notes: available to all paying commercial OCI customers globally; requires `read`/`manage carbon-emission-reports` policy statements at the tenancy; reports are filterable by compartment, region, service, tag, tenancy; European-region usage reports zero market-based emissions (100% renewable); supports both power-based and spend-based calculations; CSV export; visualization in OCI console.

### IBM Cloud — Cloud Carbon Calculator + Envizi
Status: **Tool** (Carbon Calculator) + ESG reporting suite (Envizi).
- Product news: https://newsroom.ibm.com/2023-07-26-IBM-Cloud-Carbon-Calculator-Helps-Organizations-Advance-Sustainability-Objectives-and-Address-Greenhouse-Gas-Emissions
- Envizi product: https://www.ibm.com/products/envizi
- Envizi Scope 1/2: https://www.ibm.com/products/envizi/scope-1-2-ghg-accounting-reporting
- Envizi emissions management: https://www.ibm.com/products/envizi/emissions-management
- Press analysis: https://www.esgtoday.com/ibm-launches-solution-to-track-emissions-from-cloud-computing/

Notes: AI-informed dashboard; integration path into Envizi for ESG reporting.

### Alibaba Cloud — Energy Expert
Status: **Tool**.
- Product page: https://www.alibabacloud.com/en/product/energy-expert
- Sustainability solutions: https://www.alibabacloud.com/en/solutions/sustainability
- Cloud product carbon footprint docs: https://www.alibabacloud.com/help/en/energy-expert/support/cloud-product-carbon-footprint
- Launch blog: https://www.alibabacloud.com/blog/alibaba-cloud-launches-carbon-management-solution-energy-expert_599071
- Press release: https://www.alibabacloud.com/press-room/alibaba-cloud-launches-carbon-management-solution
- TÜV Rheinland certification press: https://www.tuv.com/press/en/press-releases/alibabacloud-energyexpert.html
- Customer-focused emission targets blog: https://www.alibabacloud.com/blog/alibaba-cloud%E2%80%99s-energy-expert-helps-companies-meet-emission-targets_600035

Notes: based on PAS 2060 and ISO 14064; covers customer's own products + cloud usage.

### Tencent Cloud
Status: **Report** (no per-customer cloud carbon tool surfaced in English or Chinese sources).
- Tencent Cloud global-infrastructure sustainability page: https://www.tencentcloud.com/global-infrastructure/sustainability
- Environment landing: https://www.tencent.com/en-us/esg/environment.html
- Environmental policy: https://www.tencent.com/en-us/esg/environment/policy.html
- Carbon neutrality factsheet PDF: https://www.tencent.com/attachments/carbon-neutrality/tencent-carbon-neutrality-factsheet.pdf
- Carbon neutrality target & roadmap PDF: https://static.www.tencent.com/attachments/TencentCarbonNeutralityTargetandRoadmapReport.pdf
- 2024 ESG report PDF: https://static.www.tencent.com/uploads/2025/04/08/00ef711d9596ce09344c0260b14cda7e.pdf

Notes: 2030 net-zero (ops + supply chain) goal; "Tnebula" carbon-management platform exists but is internal to Tencent's own DC operations, not customer-facing; no first-party customer console identified.

### Huawei Cloud — Huella Cloud (KooGallery SaaS)
Status: **Tool** (third-party-built SaaS on the marketplace; not a first-party customer dashboard).
- Marketplace listing: https://marketplace.huaweicloud.com/intl/contents/8e3ba722-ba1e-46ac-8b52-9ea15f85ba40
- Huawei sustainability reports hub: https://www.huawei.com/en/sustainability/sustainability-report
- Green Management White Paper PDF: https://www.huawei.com/minisite/otf2023/file/Green_Management_White_Paper.pdf
- Reducing Carbon Emissions page: https://www.huawei.com/en/sustainability/environment-protect/reducing-carbon-emissions
- Huawei Digital Power sustainability report PDF: https://digitalpower.huawei.com/attachments/index/95edfbcab6cc42f0bda5f59f01b7f475.pdf

Notes: Huella Cloud is delivered by a partner via KooGallery; covers quantification, reduction recommendations, reporting, and VCS-certified offset modules.

---

## 2. Tier-2 / Regional Hyperscalers

> Methodology deep-dive for §2–§7 lives in `CLOUD_CARBON_ACCOUNTING_DEEPDIVE.md`.

### OVHcloud — Environmental Impact Tracker (formerly Carbon Calculator)
Status: **Tool**.
- Product landing: https://www.ovhcloud.com/en/about-us/environmental-impact-tracker/
- Launch press: https://corporate.ovhcloud.com/en/newsroom/news/environmental-impact-tracker/
- Methodology PDF (2025, tracker): https://corporate.ovhcloud.com/sites/default/files/2025-07/environmental_impact_tracker_-_methodology.pdf
- Methodology PDF (2023, legacy calculator): https://corporate.ovhcloud.com/sites/default/files/2023-11/methodo_carboncalc-en.pdf

Notes: LCA-based; covers Scopes 1/2/3 plus water and abiotic-resource depletion; audited by IJO; both LBM and MBM per datacenter.

### Scaleway — Environmental Footprint Calculator
Status: **Tool**.
- Calculator landing: https://www.scaleway.com/en/environmental-footprint-calculator/
- Concepts doc: https://www.scaleway.com/en/docs/environmental-footprint/concepts/
- Estimation doc: https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator-estimation/
- Calculation breakdown: https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator/
- Dashboard how-to: https://www.scaleway.com/en/docs/environmental-footprint/how-to/environmental-footprint-dashboard/
- Monthly footprint how-to: https://www.scaleway.com/en/docs/environmental-footprint/how-to/track-monthly-footprint/
- Methodology blog: https://www.scaleway.com/en/blog/overcoming-the-challenges-of-cloud-environmental-impact-measurement/
- CSRD positioning blog: https://www.scaleway.com/en/blog/scaleways-environmental-footprint-calculator-your-best-partner-for-csrd-reporting/
- Environmental leadership page: https://www.scaleway.com/en/environmental-leadership/
- 2024 Impact Report PDF: https://www-uploads.scaleway.com/Impact_Report2024_A4_EN_9a7bd88445.pdf

Notes: ADEME Datacenter & Cloud PCR-aligned; co-developed with IJO; includes water consumption; emphasises Scope 3 dominance.

### Hetzner
Status: **Claim** (operational metrics published, no per-customer carbon tool).
- Corporate sustainability: https://www.hetzner.com/unternehmen/nachhaltigkeit
- Docs — sustainability at Hetzner: https://docs.hetzner.com/general/company-and-policy/sustainability-at-hetzner/
- Sustainability FAQ: https://docs.hetzner.com/general/others/sustainability-faqs/
- Solar venture press: https://www.hetzner.com/pressroom/ht-clean-energy/

Notes: 100% renewable claim (hydropower DE/FI); PUE ~1.13; EMAS-certified German sites; no per-customer dashboard.

### DigitalOcean (incl. Paperspace)
Status: **Report** (ESG microsite, no per-customer carbon tool).
- Impact overview: https://www.digitalocean.com/impact
- IR ESG page: https://investors.digitalocean.com/esg/esg-overview/default.aspx
- Community thread on environmental impact: https://www.digitalocean.com/community/questions/environmental-impact-of-digitalocean-hosting

Notes: PUE-only disclosure; no SBTi/CDP participation reported; relies on colo providers (e.g., Equinix) so per-region energy mix is opaque.

### Akamai (incl. Linode / Akamai Connected Cloud)
Status: **Tool**.
- Sustainability hub: https://www.akamai.com/company/corporate-responsibility/sustainability
- Carbon Calculator blog: https://www.akamai.com/blog/culture/akamai-carbon-calculator-supply-chain-emissions
- Customer Scope 3 Cat-8 reporting blog (2025): https://www.akamai.com/blog/sustainability/2025/may/what-akamai-is-doing-for-customer-reporting
- Carbon Calculator 400-day-data blog: https://www.akamai.com/blog/sustainability/new-carbon-calculator-report-supports-400-days-data
- Carbon Calculator changelog (techdocs): https://techdocs.akamai.com/reporting/changelog/mar-31-2022-new-report-carbon-calculator
- Environmental sustainability PDF: https://www.akamai.com/content/dam/sdl-content/us/en/multimedia/documents/sustainability/environmental-sustainability-at-akamai.pdf

Notes: per-customer Carbon Calculator inside Akamai Control Center; allocation via byte + machine utilization; framed as customer Scope 3 Cat 8.

### Vultr
Status: **Claim**.
- Press release (Sabey hydro expansion): https://www.businesswire.com/news/home/20240305527534/en/Vultr-Expands-Footprint-with-New-NVIDIA-Cloud-GPU-Capacity-Using-Clean-Renewable-Hydropower-in-Sabey-Data-Centers

Notes: stated net-zero-by-2029 ambition; no first-party ESG/sustainability report, methodology document, or customer-facing carbon tool found.

### Rackspace
Status: **Report**.
- Corporate responsibility: https://www.rackspace.com/about/responsibility
- 2025 sustainability report newsroom: https://www.rackspace.com/newsroom/rackspace-technology-releases-2025-sustainability-report
- SBTi net-zero approval press: https://www.rackspace.com/newsroom/rackspace-receives-sbti-approval-net-zero-targets

Notes: SBTi-validated; no per-customer cloud carbon tool; offers consulting through Workload Aware Modernization.

### Open Telekom Cloud (T-Systems / Deutsche Telekom)
Status: **Claim** (carbon-neutral marketing, no per-customer cloud carbon tool).
- Sustainability page: https://www.open-telekom-cloud.com/en/benefits/sustainability
- Telekom CR report 2024 (environment) PDF: https://report.telekom.com/cr-report/2024/_assets/downloads/env-environment-dtag-cr24.pdf

Notes: 100% green-electricity-purchased; signatory of Climate Neutral Data Centre Pact.

---

## 3. Sovereign / EU-Focused

### Exoscale (A1 Digital)
Status: **Tool**.
- Sustainability hub: https://www.exoscale.com/sustainability/
- INTRO Sustainability academy doc: https://community.exoscale.com/academy/intro_sus/
- Compliance academy doc: https://community.exoscale.com/academy/intro_cpl/

Notes: live customer impact calculator built on CloudAssess (developed with Resilio and Kleis); hourly/daily/monthly granularity; API-accessible for invoice/dashboard integration; ISO 14040/14044- and ADEME-aligned; ISO 50001 EnMS; CSRD-2025 framing.

### UpCloud
Status: **Report**.
- Year-in-review 2024: https://upcloud.com/2024-year-in-review/
- Green Web Foundation provider blog: https://upcloud.com/blog/were-a-green-web-provider/

Notes: 70% renewable DCs (2024 figure); ISO 14001; first ESG report 2024; offsetting used for the gap.

### Leafcloud
Status: **Claim** (radical heat-reuse model; methodology articulated, but no per-customer carbon dashboard surfaced).
- Truly green landing: https://leaf.cloud/truly-green
- Green cloud explainer blog: https://leaf.cloud/blog/green-cloud-energy-use-and-residual-heat-what-actually-makes-a-cloud-sustainable
- Launch announcement: https://www.leaf.cloud/blog/leafcloud-launches-first-truly-green-public-cloud
- Case study (Milieudefensie): https://leaf.cloud/blog/how-milieudefensie-cut-carbon-emissions-and-deployment-times
- New Leaf site (households) blog: https://leaf.cloud/blog/new-leaf-site-provides-heat-to-over-250-households

Notes: distributes servers into buildings that need heat (pools, apartments, etc.); reports PUE 1.02, ERE ~0.15.

### Infomaniak
Status: **Report** (corporate-level only; no per-customer cloud tool surfaced).
- Ecology hub: https://www.infomaniak.com/en/ecology
- "We pollute" honesty post: https://news.infomaniak.com/en/we-pollute/
- 200% offset announcement: https://news.infomaniak.com/en/infomaniak-offsets-twice-as-many-co-emissions/
- Eco-design FAQ: https://www.infomaniak.com/en/support/faq/1160/eco-design-to-reduce-carbon-footprint

Notes: scope covers life cycle including employee commute; SGS-audited under ISO 14001:2015; ISO 50001; servers used for 15 years; 200% offset via Myclimate.

### GleSYS
Status: **Report**.
- Sustainability landing: https://glesys.com/sustainability/
- Policy: https://glesys.com/policies/sustainability-policy/
- 2024 sustainability report announcement: https://glesys.com/blog/glesys-releases-2024-sustainability-report-and-establishes-csrd-aligned-baseline-edited/

Notes: 100% renewable electricity; ERF 84% via district-heating reuse in Falkenberg; CSRD-aligned baseline established 2024.

### STACKIT (Schwarz Group)
Status: **Claim**.
- Sustainability in cloud computing: https://stackit.com/en/learn/knowledge/cloud/sustainability

Notes: green-electricity DCs in DE/AT; PUE 1.1 at DC10 Ostermiething; Schwarz Group net-zero-by-2050 target; no per-customer carbon dashboard surfaced.

---

## 4. "Sustainable-First" / Niche Green Providers

### GreenGeeks
Status: **Claim**.
- Going-green page: https://www.greengeeks.com/going-green

Notes: REC-based "300% renewable" model via Bonneville Environmental Foundation; US EPA Green Power Partner since 2009.

### Krystal (UK)
Status: **Claim**.
- Green hosting page: https://krystalhosting.com/green

Notes: direct renewable PPAs preferred over RECs; Gold Standard-certified projects; Veritree tree-planting counter.

### Verne (formerly Verne Global)
Status: **Report**.
- About / sustainability: https://www.verne.co/about-us/sustainability

Notes: 100% renewable Iceland/Finland campuses; published 2024 emissions ~556 tCO2e at Iceland site.

### atNorth
Status: **Report**.
- Sustainability strategy: https://www.atnorth.com/sustainability/sustainability-strategy/

Notes: Nordic colocation/cloud; geothermal+hydro grid mix.

---

## 5. AI / GPU-Specialist Clouds

### CoreWeave
Status: **Claim** (no published per-customer carbon data; Scope 1/2 measurement reportedly in progress).
- About: https://www.coreweave.com/about-us
- FY25 10-K (sustainability discussion inside): https://s205.q4cdn.com/133937190/files/doc_financials/2025/q4/CoreWeave-Inc-FY25-10-K-7.pdf

Notes: heat-recapture pilots mentioned; no formal SBTi target / methodology surfaced.

### Lambda
Status: **None** (no dedicated sustainability disclosure surfaced).
- Main site: https://lambda.ai/

Notes: marketing references to "zero-emissions energy standards" at Mountain View facility; no methodology or report found.

### Crusoe
Status: **Report**.
- Resources / "leading energy transition" blog: https://www.crusoe.ai/resources/blog/crusoe-tallys-law-leading-energy-transition
- 2022 ESG Report PDF: https://crusoe-public.s3.us-east-2.amazonaws.com/Crusoe_ESG+Report_2023.05.10.pdf
- First-ever ESG report announcement: https://crusoe.ai/blog/crusoe-first-ever-esg-report/
- HBS podcast on carbon-intensity reduction: https://www.hbs.edu/environment/podcast/Pages/podcast-details.aspx?episode=7817491047

Notes: Digital Flare Mitigation business model; reports volumetric methane / flared-gas avoidance metrics rather than customer-allocated emissions.

### Nebius (formerly Yandex international)
Status: **Report**.
- Sustainability hub: https://nebius.com/sustainability
- 2024 sustainability report announcement: https://nebius.com/newsroom/nebius-group-2024-sustainability-report-highlights-importance-of-sustainability-to-long-term-value-creation-in-ai-infrastructure

Notes: claims 0.04 tCO2e/MWh market-based intensity; Finnish DC heat reuse (65% local heating); Scope 3 / water reportedly absent — flagged as a transparency concern by third-party analysis (https://www.computing.co.uk/research/2026/sustainability-mirage-heart-of-neocloud).

### Hyperstack (NexGen Cloud)
Status: **Claim**.
- Main site: https://www.hyperstack.cloud/
- AQ Compute net-zero AI supercloud announcement: https://www.hyperstack.cloud/blog/company-news/nexgen-cloud-and-aq-compute-advance-towards-net-zero-ai-supercloud

Notes: 100% renewable marketing claim; Tier-3 DC partnerships; no methodology PDF or per-customer accounting surface found.

### DataCrunch
Status: **Claim**.
- Clusters page (sustainability framing): https://datacrunch.io/clusters
- TechCrunch coverage: https://techcrunch.com/2024/10/21/datacrunch-wants-to-be-europes-first-ai-cloud-hyperscaler-powered-by-renewable-energy/

Notes: Helsinki + Iceland sites; waste-heat reuse claim; no formal sustainability report, methodology PDF, or per-customer accounting surface published as of this inventory.

### RunPod
Status: **None** (no sustainability page or report surfaced).
- Provider list (third-party context): https://www.runpod.io/articles/guides/top-cloud-gpu-providers

### Paperspace
Status: **None** (acquired by DigitalOcean — falls under DO disclosure).

### Together AI / Fireworks AI / Replicate
Status: **None**.
- Fireworks AI: https://fireworks.ai/
- Together AI / Replicate: no dedicated sustainability page or report surfaced.

Notes: as inference platforms, emissions inherited from underlying GPU clouds; no first-party data exposed to customers.

---

## 6. Edge / CDN Clouds

### Cloudflare
Status: **Tool**.
- Impact landing: https://www.cloudflare.com/impact/
- Sustainability blog tag: https://blog.cloudflare.com/tag/sustainability/
- Carbon-impact tool methodology blog: https://blog.cloudflare.com/understand-and-reduce-your-carbon-impact-with-cloudflare/
- SBTi commitment & savings: https://blog.cloudflare.com/switching-cloudflare-cut-your-network-carbon-emissions-sbti/
- 2023 Impact Report PDF: https://cf-assets.www.cloudflare.com/slt3lc6tev37/3Z7xOV53lGEIAwCqw5SncT/69eaca7bd5d2395ee0274b15e7854dd6/2023_Impact_Report.pdf

Notes: per-customer Carbon Impact Report in dashboard; emission factors from US EPA / UK DEFRA / IEA; per-PoP factors.

### Fastly — Sustainability Dashboard
Status: **Tool**.
- Product landing: https://www.fastly.com/products/sustainability-dashboard
- Dashboard docs: https://www.fastly.com/documentation/guides/account-info/account-management/about-the-sustainability-dashboard/
- Methodology: https://www.fastly.com/documentation/guides/account-info/sustainability/our-sustainability-dashboard-methodology/
- 2024 Sustainability Report PDF: https://investors.fastly.com/files/doc_governance/2025/Nov/26/2024-Fastly-Sustainability-Report-290db1.pdf

Notes: per-customer usage→kWh→GHG model across the Fastly PoP network; API + CSV access; 100% renewable target.

---

## 7. PaaS / Serverless (Generally Opaque)

### Vercel
Status: **Claim**.
- Green energy policy KB: https://vercel.com/kb/guide/what-is-vercel-green-energy-policy

Notes: emissions inherited from underlying cloud providers (AWS-heavy); no per-customer carbon tool.

### Netlify
Status: **Claim**.
- Sustainability landing: https://www.netlify.com/sustainability/
- Sustainable-transformation blog: https://www.netlify.com/blog/from-legacy-to-leading-edge-sustainable-success-with-netlify/
- Community thread on transparency: https://answers.netlify.com/t/could-netlify-provide-more-transparent-information-on-its-sustainability-credentials-such-as-renewable-energy-percent/45851

Notes: argues Jamstack/CDN architecture is intrinsically lower-emission; no per-customer accounting.

### Fly.io
Status: **None** (only community thread and a carbon-aware-demo customer surfaced).
- Community thread: https://community.fly.io/t/carbon-emissions/4345

### Render
Status: **None** (inherits AWS / GCP).
- Community thread: https://community.render.com/t/does-render-use-green-energy/912

### Heroku (Salesforce)
Status: **Report** (corporate net-zero claim inherited from Salesforce; no per-app or per-account customer surface).
- Heroku carbon-neutral help article: https://help.heroku.com/2163BDDI/is-my-app-carbon-neutral
- Salesforce sustainability hub: https://www.salesforce.com/company/sustainability/
- Net Zero Cloud product (separate ESG SaaS, not a Heroku tool): https://www.salesforce.com/products/sustainability-cloud/overview/
- Salesforce environment whitepaper PDF: https://www.salesforce.com/content/dam/web/en_us/www/assets/pdf/datasheets/sustainability-wp-wsp-salesforce-environment.pdf
- "Green Code" initiative: https://www.salesforce.com/news/stories/green-code-software/

Notes: Salesforce claims globally net-zero ops and a carbon-neutral cloud; "Carbon to Serve" is an internal KPI (data-center emissions ÷ application work done) introduced 2020, reported as a corporate metric rather than published as a customer methodology; -26% claimed since baseline; Hyperforce positioned as 100% renewable architecture.

---

## 8. Adjacent Open-Source / Independent References

These are not providers but are routinely cited methodologically and should be tracked alongside provider tools.

- Cloud Carbon Footprint (open-source tool): https://www.cloudcarbonfootprint.org/docs/methodology/
- Green Web Foundation — green-power evidence policy: https://www.thegreenwebfoundation.org/what-we-accept-as-evidence-of-green-power/
- DitchCarbon provider directory (third-party emissions estimates): https://ditchcarbon.com/
- Carbone 4 — analysis of hyperscaler footprints: https://www.carbone4.com/en/analysis-carbon-footprint-cloud
- Computing.co.uk neocloud sustainability analysis: https://www.computing.co.uk/research/2026/sustainability-mirage-heart-of-neocloud

---

## 9. Proposed Schema for Methodology Deep-Dive

When we move from inventory to comparison, we should evaluate each `Tool`-status provider (and probably the better `Report`-status ones) against a fixed set of dimensions.
The dimensions below are ordered by relevance to the rSCI framework — i.e. how well a customer-attributed number can be reconciled against provider-reported scopes.

### Block A — Surface and access
- **Delivery channel**: console UI, API, CSV/export, Power BI / 3rd-party dashboard only, partner SaaS.
- **Pricing/access**: free for all customers, paid tier, enterprise-only, partner-gated.
- **Update cadence**: monthly with N-month lag, daily, near-real-time.
- **Granularity (temporal)**: hourly / daily / monthly.
- **Granularity (resource)**: account / service / per-resource / per-region / per-AZ.

### Block B — Scope coverage
- **Scope 1**: included y/n.
- **Scope 2 — location-based**: included y/n.
- **Scope 2 — market-based**: included y/n; default shown.
- **Scope 3 categories**: which of the 15 GHG-Protocol categories are allocated to the customer (e.g. cat. 1 purchased goods/services, cat. 2 capital goods, cat. 3 fuel-and-energy-related activities, cat. 11 use of sold products).
- **Embodied hardware**: cradle-to-gate LCA y/n; component-level vs rack-level.
- **Excluded items**: explicitly disclosed exclusions (e.g. business travel, office overhead, employee commute).

### Block C — Calculation model
- **Energy model**: measured/metered, modeled-from-utilization (CPU%, GPU%, network bytes), spend-based, hybrid.
- **Power → energy mapping**: actual PUE, fleet-average PUE, regional default.
- **Emission-factor source**: IEA, EPA eGRID, DEFRA, AIB residual mix, provider-specific PPA mix, supplier-specific.
- **Allocation key (usage → customer)**: kWh-proportional, spend-proportional, request-proportional, hybrid.
- **Treatment of idle / overhead**: how unattributed footprint (idle capacity, control plane, shared services) is handled — burdened into customer, kept on provider, or omitted.

### Block D — Renewable-energy accounting
- **REC/EAC use**: y/n; market vs. bundled.
- **PPA disclosure**: contract list / counterparties / vintage.
- **Hourly carbon-free energy**: reported y/n (only Google does this today).
- **Geographic matching**: same grid region required, or anywhere-globally?

### Block E — Standards and assurance
- **Standards alignment**: GHG Protocol Corporate, GHG Product, ISO 14064-1/-2/-3, ISO 14040/44, ISO 14067, PAS 2060, ADEME PCR for DC/Cloud, ICT Sector Guidance.
- **Third-party assurance**: assurer, assurance level (limited / reasonable), assurance standard (ISO 14064-3 / ISAE 3410).
- **Methodology versioning**: published change-log, version number, deprecation policy.

### Block F — Multi-criteria and adjacent metrics
- **Water (WUE / m³)**: included y/n.
- **Abiotic resource depletion**: included y/n (OVH, Scaleway only).
- **E-waste / circularity**: reported y/n.
- **Heat reuse / ERE / ERF**: reported y/n.

### Block G — Replicability and transparency
- **Public methodology document**: PDF/page, depth (overview vs. equations).
- **Raw factor disclosure**: are emission factors / kWh-per-unit tables published?
- **Customer can recompute**: realistically reproducible from the provider's disclosures?
- **Differences across regions**: which regions report 0 due to PPA structure (creates the residual that rSCI is designed to surface).

The minimum subset I'd use for a first comparison table (single row per provider) is:
`tool? · scope coverage · embodied? · model (measured/modeled/spend) · standards · assurance · cadence · granularity · multi-criteria? · methodology PDF?`

That collapses to ~10 columns and is the right granularity to show every provider on one page.

## Resolved open questions

- **Tencent Cloud**: no customer-facing tool found in English or Chinese sources; internal "Tnebula" platform is for Tencent's own DC operations.
- **Oracle Carbon Emissions Analysis**: generally available to all paying commercial OCI tenancies in all regions; access gated only by IAM policies (`carbon-emission-reports` read/manage); European regions report market-based zero by design.
- **Hyperstack, DataCrunch, Vultr**: no first-party methodology PDFs exist as of this inventory; only marketing/PR pages.
- **Exoscale**: CloudAssess-based calculator is in production (not beta), with hourly/daily/monthly granularity and API access.
- **Salesforce "Carbon to Serve"**: internal corporate KPI (DC emissions ÷ application work), not a published customer-facing methodology; Heroku per-app accounting therefore inherits Salesforce's corporate net-zero claim rather than exposing per-customer numbers.
- **Colocation providers**: deliberately out of scope for this inventory (focus is cloud-service providers).
