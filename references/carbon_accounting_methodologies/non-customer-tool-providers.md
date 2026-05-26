# Provider notes — caveats not captured in the appendix table

Companion to the cloud provider survey in `paper/paper.tex` §A.
The appendix is authoritative for cluster, status, and URL; this file holds per-provider methodology context, certifications relevant to the assurance/self-reported boundary, and rSCI-specific caveats.
Last refreshed: 2026-05-26 — aligned with the May~2026 survey rework (5-cluster status taxonomy, "Operational metrics only" collapsed into Self-reported).

## Hyperscalers

### Huawei Cloud — Assured
- Group sustainability reports since 2008; latest is the 2025 Annual Report (released 2026-03-31).
- The third-party Huella Cloud calculator (by SGS Solutions) is sometimes referenced *on* Huawei Cloud but is not a first-party product — excluded from the per-customer-tool list (see paper §3 footnote).

### Tencent Cloud — Self-reported
- "Tnebula" internal carbon-management platform is for Tencent's own DC operations, not exposed to customers.

## Mid-tier and regional IaaS

### Rackspace — Assured
- SBTi-validated net-zero targets; third-party-audited Scope 1/2/3 baseline.
- Customer-facing offering is consulting (Workload Aware Modernization), not a dashboard.

### Infomaniak — Assured
- ISO 14001:2015 (SGS-audited annually) + ISO 50001. PUE 1.06 (air-cooled, no water).

### Exoscale (A1 Digital) — Self-reported
- A console+API CloudAssess calculator is surfaced, but the engine is third-party (CloudAssess by Resilio/Kleis) — methodology not fully public and not auditable against Exoscale's own emission factors. Previously borderline as a per-customer tool; demoted on first-party criterion.

### Hetzner — Self-reported
- EMAS-verified environmental statement at German sites (third-party verified EU scheme, distinct from ISO 14001 self-attestation). PUE 1.10–1.16. Hydropower since 2008 (DE) / 2018 (FI).

### Baidu AI Cloud, JD Cloud — Self-reported (group-level only)
- Coverage via parent ESG reports (Baidu Inc., JD.com). No per-customer cloud surface.
- JD's "Energy & Carbon Management Platform" (能碳管理平台) is an IoT solution for clients' own operations, *not* a JD-Cloud-workload tool.

### Open Telekom Cloud → T Cloud Public — MOVED to per-customer-tool list
- Renamed; per-tenant Sustainability Dashboard launched 2026-02-23. See `t-cloud-public/README.md`.

## Sustainability-positioned regionals

### GleSYS — Assured
- 2024 CSRD-aligned baseline; ERF 84% (heat into Falkenberg district heating).

### atNorth — Assured
- 2024 Sustainability Report carries **Grant Thornton limited assurance under ISAE 3000** over Scope 1/2/3. Pan-Nordic (IS/SE/DK/FI).

### UpCloud — Self-reported
- First ESG report 2024 (Scope 1/2/3 per GHG Protocol Corporate Standard).
- Note: parent ISO 27001; ISO 14001 *not* held (mistakenly listed in older notes).

### Verne — Self-reported
- 2025 unified certification: ISO 27001/45001/9001/14001 + PCI DSS. **ISO 14001 is an environmental-management-system standard, not GHG assurance** (no ISO 14064 / SBTi / external GHG verification).
- Pan-Nordic (Iceland + 3 Finnish DCs; London HQ).

### Leafcloud — Marketing claim
- Heat-reuse model (servers placed inside buildings that need heat). Cites comparative figures but no PUE, no GHG inventory.

## CDN / edge

- Akamai / Cloudflare / Fastly ship per-customer tools (see their own folders). Cloudflare additionally publishes a full Scope 1/2/3 inventory (Impact Report 2025) and is SBTi-committed.
- Gcore, Bunny.net, CDNetworks: no first-party emissions disclosure or per-customer tool. CDNetworks is the international brand of Wangsu Science & Technology (97.82% owned); Sustainalytics rates Wangsu's ESG management as Weak.

## Neocloud (AI/GPU)

### Crusoe — Self-reported
- 2024 Impact Report (released June 2024, successor to the 2022/2023 reports).
- ***rSCI caveat:*** the Digital Flare Mitigation framing reports *avoided* emissions relative to a flaring counterfactual, not operational footprint. Awkward fit with rSCI's residual model — DFM credits sit alongside, not inside, the SCI numerator.

### Nebius — Self-reported
- 2024 Sustainability Report. Scope 3 + water flagged externally as transparency gap.
- Distinct entity from Russian Yandex Cloud — Nebius emerged from the 2024 divestiture of Yandex N.V.'s non-Russian assets.

### Verda (ex-DataCrunch) — Marketing claim
- Rebranded from DataCrunch. Pan-Nordic (Helsinki + Iceland). "100% renewable" + waste-heat reuse claim; no formal report.

### CoreWeave, Lambda, Hyperstack, Paperspace, Together AI, RunPod, Fireworks AI, Replicate
- See appendix for per-provider status. Paperspace was acquired by DigitalOcean — does not inherit any corporate-disclosure status (DigitalOcean is itself Marketing claim).

## PaaS

All current entries (Netlify, Vercel, Fly.io, Railway, Render) are marketing-claim or no-disclosure — no per-account surface; emissions implicitly inherit from underlying IaaS.

Excluded from this row:
- Heroku (sunset under Salesforce).
- Salesforce, Snowflake, Databricks (SaaS / data-platform, not cloud-tenant-facing accounting).

## Adjacent / independent references

Not providers, but routinely cited methodologically:

- Cloud Carbon Footprint (open-source tool): https://www.cloudcarbonfootprint.org/docs/methodology/
- Green Web Foundation — green-power evidence policy: https://www.thegreenwebfoundation.org/what-we-accept-as-evidence-of-green-power/
- DitchCarbon provider directory: https://ditchcarbon.com/
- Carbone 4 — hyperscaler footprint analysis: https://www.carbone4.com/en/analysis-carbon-footprint-cloud
- Computing.co.uk neocloud sustainability analysis: https://www.computing.co.uk/research/2026/sustainability-mirage-heart-of-neocloud