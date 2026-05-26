# Methodology comparison — per-customer carbon tools

**Purpose.**
Consolidate the per-provider methodology evidence (in `carbon_accounting_methodologies/<provider>/`) into a single comparison that uses *one* shared computational template for every per-customer-tool tool, so the real differences between providers are visible on a few orthogonal axes instead of three pseudo-families.

**Scope.**
12 providers shipping first-party per-customer carbon tools, verified 2026-05-26:
AWS, GCP, Azure, Oracle, IBM, Alibaba, OVHcloud, Scaleway, T Cloud Public, Akamai, Cloudflare, Fastly.
T Cloud Public launched its dashboard 2026-02-23; methodology detail is sparse so it appears in the headcount and notes but not in the per-axis tables below.
Exoscale (third-party engine) and Huawei (third-party multi-cloud) excluded — see `carbon_accounting_methodologies/README.md`.

The four-axis decomposition supersedes the "three methodology families" framing previously used in `paper/paper.tex` §3 and in `cross_provider_synthesis.md`.

---

## The shared template

Every per-customer-tool customer tool reports a per-account number that, stripped of marketing, computes as:

```
customer_carbon(account, period) =
    Σ_resources  ( activity_units(account, resource, period)
                   × per_unit_factor(resource)
                   × overhead_multipliers(resource) )
  + flat_overheads(account, period)
```

The provider-to-provider variation lives entirely in:
- which `activity_units` are tallied;
- how `per_unit_factor` is derived;
- whether embodied is folded into the factor, added separately, or excluded;
- how shared/idle/overhead capacity is treated.

**The ideal weighting factor is *measured energy* (kWh consumed by the customer's actual workload).**
How well a usage-unit proxy approximates that depends on whether the unit tracks energy:

- For **network**, energy is approximately linear in throughput (per-packet / per-bit cost dominates), so bytes-delivered is a structurally sound energy proxy. Cloudflare / Fastly-Delivery / Akamai's byte component all sit on this regime.
- For **compute**, energy is highly nonlinear in load (idle ≈ 50–60% of full-load draw at the server). vCPU-hours, instance-hours, and `$`-spend therefore *underweight* heavily loaded workloads and *overweight* idle ones at the same SKU and duration. This is where the customer-surface allocation decouples from physical reality.

**Critical shared property — verified across all 11 documented per-customer-tool providers from primary sources (T Cloud Public excluded; methodology not yet published):**

The four customer-surface allocations that approach energy-direct (in decreasing order of how concretely the source documents the claim):

1. **Scaleway** — *closest to load-direct*. Uses **actual measured CPU consumption** combined with published Boavizta consumption profiles (non-linear CPU%→power) for CPU Instances; a fully-loaded VM and an idle VM at the same SKU receive different allocations in the monthly report. PDF-grounded (per-product calculation pages compiled in `scaleway/scaleway-methodology-docs-2026-05.md`). The strongest published energy-aware customer methodology in the per-customer-tool set, restricted to CPU Instances.
2. **Akamai** — *energy-metered, allocation rule semi-disclosed*. Per-server and per-device kWh metering in colocations; allocated to customers via (byte-share × DC-machine-utilization). PDF-grounded via the 2025 emissions-reporting policy doc and blog compilation, but per-customer equations still not published.
3. **Oracle (power-based)** — *energy-metered, allocation algorithm undisclosed*. Tracks kWh by service workload and allocates from "data center hardware (both dedicated and shared)" via an undisclosed algorithm; multiplied by regional LBM/MBM EF. PDF-grounded via the June-2025 release-note markdown in `oracle/`. Service-coverage list not published; spend-based mode used for everything else.
4. **GCP (internal stage only)** — energy-direct via Borg power telemetry at the internal stage, but the customer-facing step §3.6 deliberately re-projects onto vCPU-hours × list-price. Energy-aware physics on the input side; price-proportional re-projection on the customer side.

Everyone else (AWS, Azure, IBM, Alibaba, OVHcloud-currently, Cloudflare, Fastly) allocates by a usage-unit proxy of varying quality (good for network where energy ≈ linear in bytes; poor for compute where energy is nonlinear in load).[^akamai]

[^akamai]: Akamai's customer methodology blog states allocation uses "byte utilization + machine utilization per DC" and that the calculator uses *"Real DC energy use × utilization weighting; not bytes-only"*. The "machine utilization" is the per-DC aggregate IT-equipment utilization, used to convert DC-total energy into a per-customer share. Equations are not published, so the claim is provider-asserted but unverifiable.

---

## The four axes

| Axis | Values observed |
|---|---|
| **A1 — Activity unit** | instance-hours · vCPU-hours · normalized-instance-hours · GB-month · CPU-time · bytes-delivered · request-count · `$`-spend · server-hours (dedicated) |
| **A2 — Per-unit-factor source** | list-price proportional · revenue/spend proportional · component-LCA × hardware inventory · meter-then-bucket (internal power telemetry, then bucketed to SKUs) · external benchmark (BSR / public DC studies) · undisclosed |
| **A3 — Embodied carbon treatment** | bundled into per-unit factor · separate LCA term · excluded |
| **A4 — Idle / overhead allocation** | proportional to usage · flat-per-server · 100%/24×7 conservative baseline · undisclosed |

A1 governs *what user actions show up at all* (turning off a VM reduces vCPU-hours; reducing CPU% does not).
A2 governs *how cleanly a kWh reduction maps to a kgCO₂e reduction*.
A3 governs whether the tool tracks any non-electricity emissions at the customer surface.
A4 governs whether the per-account number rises when the provider's own utilisation falls.

---

## Provider profiles in the shared template

Each block: A1 · A2 · A3 · A4 · key gap.
Source is the per-provider folder; no claim here is independent of that folder.

### AWS — Sustainability Console (Model 3.0, Oct 2025; bugfix 3.0.1 Apr 2026)

- **Surface update**: AWS docs page (verified 2026-05-22): *"The CCFT will be deprecated on June 30th 2026 in favor of the new AWS Sustainability service which offers additional functionalities and does not require Billing console permissions"* (`docs.aws.amazon.com/sustainability/latest/userguide`). The customer-facing service breakdown shows only EC2, S3, CloudFront broken out; all other services grouped under "Other".
- **A1**: per-rack-type usage units; e.g. *Normalized Instance-Hour (NIH)* for EC2 racks, *GB-month* for S3 racks (`aws/aws-ccft-methodology-model3.pdf` §4.2, Eq 36–37). Customer share at the foundational-service step is `customer-units / cluster-total-units` (§4.3.1, Eq 40–41). Different units per rack type — **there is no single "instance-hours per service" allocation**.
- **A2 (foundational services)**: meter-then-bucket. AWS measures rack-level power, allocates to services by usage-unit share. Whether internal utilization telemetry feeds the per-unit factor is *not disclosed* in the methodology document (§4.2). AWS calls this "physical allocation" (definition table p. 9: `usage-based ("physical allocation")`).
- **A2 (non-foundational services)**: revenue. `eqRevenue`-share allocation (§4.3.2, Eq 42). AWS's own definition: "equivalent revenue is the weighting factor leveraged when applying *economic allocation*" (p. 9).
- **A2 — critical gap (partially closed via web search 2026-05-22)**: AWS docs and blogs name **foundational** services *EC2, S3* and **non-foundational** services *Lambda, AppSync, Athena*. No comprehensive list is published, and the fleet-share allocated by revenue is *not published* in any source surfaced.
- **A3**: bundled into per-unit factor; cradle-to-gate IT 6 yr, buildings 50 yr (added Oct 2025 in Model 3.0), non-IT included, EoL excluded.
- **A4**: documented two-regime rule (§4.2, "Utilization cases", lines following Eq 38–39). *Mature* racks (≥12 mo) — full rack emissions allocated to that rack's services proportionally to usage-unit share, i.e. unused capacity is implicitly absorbed by users of the rack. *Ramp-up* racks (<12 mo) with utilization below mature-fleet average — the *extra* emissions from low utilization are pulled out and **distributed as a global overhead across all services using that rack type at the global level**, "pro rata across services and their users", explicitly to avoid overburdening early-stage customers. AWS cites ICT-sector-guidance ¶ that *"all data center emissions should be allocated to the services that the data center delivers, [including] IT equipment that … serves as reserve capacity."*

### GCP — Cloud Carbon Footprint

- **A1**: usage units per SKU — vCPU-hours, GiB-months, request-counts (`gcp/schneider-mattia-2024-gcp.pdf` §3.6).
- **A2**: two-stage. Stage 1 (internal): meter-then-bucket — Borg machine-level power telemetry, dynamic power allocated by GCU usage, idle power by resource-weighted shares. Stage 2 (customer-facing): *list-price proportional* — per-SKU energy factor scales with SKU list price (§3.6, Eq 10). Schneider & Mattia §3.6 explicitly call this out as a limitation: *"customers do not receive a signal about how switching from SKU A to SKU B can reduce their actual emissions, but rather their allocated emissions based on list prices."*
- **A2 — secondary path**: internal shared services without sufficient usage data use back-charged internal cost (~1/3 of shared-service energy per §3.4.2). Non-electricity Scope 3 allocated by proportional ratio `(customer kWh) / (total GCP kWh)`.
- **A3**: bundled into per-unit factor; cradle-to-gate IT 4 yr (financial-accounting depreciation, shorter than real life), buildings included, EoL excluded.
- **A4**: proportional to usage (idle power explicitly redistributed proportionally).

### Azure — Emissions Impact Dashboard + Carbon Optimization

- **A1 (resolved, Microsoft Learn page fetched 2026-05-22)**: time/volume-based. §"Calculation methodology for scope 1 and 2" verbatim: *"Power usage for scope 1 and 2 Azure emissions categories includes storage, compute, or network. Usage time in these categories helps us attribute scope 1 and 2 emissions."* §"How does Microsoft calculate usage?": *"Microsoft calculates usage by adding up your company's compute, storage, and data transfer in the Microsoft cloud."* This resolves the prior 2021 ("normalized cost metric") vs 2025/26 ambiguity *as Microsoft now phrases it* — the current Learn page is squarely time-based, no cost language. M365 still explicitly uses *"proxy usage measures instead of true server-side compute and storage usage"*; Azure cloud has no equivalent "proxy" hedge.
- **A2 (resolved as meter-then-bucket black-box)**: §"Customer attributions and calculations for carbon emissions" verbatim: *"the methodology allocates emissions based on their relative Azure usage in a given datacenter region. An algorithm calculates a usage factor that provides emissions per unit of customer usage in a specific Azure data center region. The algorithm then uses this factor to directly calculate emissions."* Pattern: `usage_factor = DC_emissions / DC_total_usage_units`, applied to customer usage. Same shape as IBM and Alibaba; the algorithm itself remains undisclosed beyond "compute, storage, data transfer". Customer cannot independently reconstruct the per-unit factor.
- **A3**: bundled into per-unit factor; pLCA via CHEM (`azure/azure-chem-2026.pdf`); IT 6 yr; **buildings excluded** ("might add as data becomes available"); EoL **included** (Cat 12 — unique among Big-3).
- **A4 (still undisclosed, but with structural implication)**: The Microsoft Learn page does not document idle/reserve-capacity treatment. Under the meter-then-bucket pattern in A2, idle DC capacity is *implicitly* absorbed into the per-unit factor — each customer's per-unit charge is inflated by exactly the DC's overall idle fraction. Microsoft does not state this and does not publish DC utilization rates, so customers cannot quantify the implicit overhead.
- **Provider-acknowledged billing↔emissions gap** (verbatim): *"Usage for emissions calculations might not match your Microsoft usage for billing purposes."*
- **Provider-acknowledged gap** (verbatim, live 2026-05-16): *"Usage for emissions calculations might not match your Microsoft usage for billing purposes."*

### Oracle — OCI Carbon Emissions Analysis

- **A1**: two modes (release-note URL fetched 2026-05-22; release note text still not PDF-grounded in `references/`).
  - *Power-based*: *"tracks the amount of power consumed (in kWh) by service workloads"*. Verbatim: *"This method allocates energy consumption from OCI data center hardware (both dedicated and shared) to your resource workloads, then multiplies it by a regional carbon emissions factor based on the power grid mix of renewable and non-renewable energy."* Service list not enumerated: *"Power-based calculations are more exact but are only supported by some OCI services. For other services, use spend-based calculations."* EU regions reported MBM = 0 by design due to PPA portfolio.
  - *Spend-based* (fallback, broader coverage). Customer pre-discount `$`-spend × per-service emission factor. This is the only mode documented in `oracle/oracle-technical-carbon-guidance.pdf` (Feb 2023, v1.0, §"Carbon Footprint Customer Calculation"): *"we publish revenue-based carbon emissions factors to enable our customers to estimate their Scope 3 emissions"*.
- **A2 (spend-based)**: revenue/spend proportional. **A2 (power-based)**: meter-then-bucket — claims energy is allocated from DC hardware (including *shared* hardware) to workloads, then multiplied by regional EF. The shared-hardware allocation algorithm itself is not described in the release note.
- **A3**: **excluded.** Power-based mode is explicitly operational only.
- **A4**: undisclosed. The release note acknowledges shared-hardware energy is included in the allocation but does not describe whether idle/reserve capacity rolls into the per-workload bucket.
- **Provider caveat** (direct quote, OCI docs): *"Carbon Emissions Analysis isn't intended to be used as a developer tool to reduce emissions. All customer carbon emissions provided are estimates."*

### IBM Cloud — Carbon Calculator / Envizi

- **A1**: usage units per service (electricity-per-service input). Service-level granularity only.
- **A2**: meter-then-bucket. `Σ (electricity_per_service × PUE_location × CEF_location)`. Per-service / per-location PUE and CEF not published; cross-referencing required for customer recompute. v5 (2025–2026) adds ML/anomaly layer on top of the same base formula.
- **A3**: v3 excluded embodied entirely. v5 (Apr 2026 Envizi API) claims Cloud Carbon Footprint methodology + IBM ML for hardware manufacturing and EoL (Scope 3). Not yet PDF-grounded in `references/` for v5.
- **A4**: undisclosed. No service inventory published.

### Alibaba Cloud — Energy Expert

- **A1**: "resource sales" — billable cloud-resource units per the three-stage allocation chain (IDC → cloud product → cloud account). Paid product; not a default console feature.
- **A2**: meter-then-bucket. `per-IDC PUE × resource sales × green-power-usage ratio × technical carbon-reduction measures`. Per-service intensities not published.
- **A3**: excluded; embodied not addressed in public docs.
- **A4**: undisclosed.
- **Differentiator**: Bureau Veritas (Beijing) third-party *data* assurance under ISO 14064-3 — the only per-customer-tool tool with data-level (not methodology-level) assurance.

### OVHcloud — Environmental Impact Tracker (v2.0, Apr 2025)

- **A1**: two paths.
  - *Dedicated products* (Bare Metal, Hosted Private Cloud): server-hours — full per-server footprint attributed to the customer (`ovh-eit-methodology-v2-2025.pdf` Eq 4: `Σ_server (Manuf + Usage + Ops)`).
  - *Mutualized* (Public Cloud Compute): template-weighted instance-hours — e.g. `b3-8` = 1×, `b3-640` = 80×; customer share = `Σ (template-weight × billed hours) / range-capacity`.
- **A2**: component-LCA × hardware inventory for manufacturing — published per-component factors (Table 1, IJO 2022): rack 200/250/350 kgCO₂eq per U, CPU 1.5 kgCO₂eq/core, RAM 2 kgCO₂eq/GB, SSD 60 kgCO₂eq/TB, HDD 25 kgCO₂eq/TB, GPU from Green Cloud Computing 2021 LCA. Usage term = `Electricity_server × PUE_DC × EF_country` with Electricity Maps 2024 yearly data + per-DC PUE table (1.21–1.39 owned, 1.30–1.72 colocated, fallback 1.6).
- **A3**: **separate LCA term**, not bundled. Manufacturing (~27% of 2024 footprint), Usage (~49%), Operations (~24%) explicitly decomposed.
- **A4**: *100%/24×7 baseline* until Smart-PDU rollout completes — customer numbers are conservative over-estimates (opposite bias of Big-3). Operations allocated *equally per dedicated server* (flagged as a simplification). Workload-scaling curve (Fig. 6) published so customers can map worst-case to actual duty cycle.

### Scaleway — Environmental Footprint Calculator

(Now PDF-grounded via `scaleway/scaleway-methodology-docs-2026-05.md` — markdown compilation of the per-product calculation pages.)

- **A1**: per-product activity units across 7 products with **published formulas** per product. For Instances: `ManufacturingImpact_Instance = (dU / DDV) × ManufacturingImpact_hypervisor × Resources_Used_VM`, where `Resources_Used_VM` is a vCPU/RAM/Storage share of the hypervisor. For Block Storage: `bls_ratio = VOLsto / VolstoPool` with `×3` replication factor baked in. For Bare Metal: full per-server attribution.
- **A1 — actual CPU consumption** (the differentiator): for the *monthly report*, Scaleway uses **actual measured CPU consumption** combined with **Boavizta consumption profiles** (non-linear CPU%→power model) for CPU Instances. Only the pre-order *estimation* mode uses a flat 30% CPU assumption. Verbatim: *"Monthly report mode: uses actual CPU consumption for highest accuracy."* GPU Instances use average per-offer consumption (not load-tracked). This makes Scaleway, for CPU Instances, one of the two per-customer-tool providers that reflect customer-side compute load in the customer number — though through a published *consumption-profile model* rather than direct kWh metering.
- **A2**: component-LCA × hardware inventory via Boavizta for *manufacturing*; manufacturing prorated by `(customer use duration) / (server lifespan)`. Construction (non-IT) via ADEME generic factors. For *usage*: per-VM-instance `UsageImpact = Power_kW × EmissionFactor × dU × allocation_ratio` (worked example for fr-par-2: PUE 1.16, France EF 0.065 kgCO₂e/kWh). For transversal tools: *"aggregated impact is allocated to each resource based on the electrical power it consumes."*
- **A3**: separate LCA term. Scope 3 ≈ 80% of reported total. Water consumption included alongside carbon.
- **A4**: undisclosed at the global/idle-DC level; non-IT impacts updated annually from personnel stats to avoid seasonal distortion. Within compute, the Boavizta-profile + actual-CPU pipeline means idle vs busy *does* affect the per-VM customer number — a stronger A4 signal than any other per-customer-tool provider documents.
- **Granularity — Scaleway is the most temporally granular per-customer-tool tool.** Verbatim: *"Data is generated daily and becomes visible the day after product activation."* Dashboard switches to **daily breakdown when a single month is selected**, monthly when multiple months are selected.

### Akamai — Carbon Calculator (Control Center)

(Now PDF-grounded via `akamai/akamai-emissions-reporting-policy-2025.pdf` + `akamai-carbon-calculator-blog-compilation-2026-05.md`.)

- **A1**: bytes delivered (delivery products only). Linode/Akamai Connected Cloud Compute *not covered* despite Feb 2022 acquisition — a 4-year coverage gap as of 2026-05-16.
- **A2**: **energy-direct (claimed and now better-grounded)**. Verbatim from compiled Akamai sources: *"Akamai measures the electricity used by every server and network device in global colocation sites, recording kWh consumed exactly when and where."* Allocation rule, verbatim: *"your use in a particular data center is measured by byte utilization and machine utilization. We take that data and allocate the appropriate proportion of that data center's energy use and emissions to your account."* Pattern: measured per-server kWh × per-customer (byte-share × DC-machine-utilization). Full per-customer equations still not published; the kWh-metering claim is provider-asserted but more concrete than my earlier "blog only" framing. Akamai also tracks **Marginal Operating Emissions Rate (MOER)** — a real-time, sub-hourly grid signal — though it's unclear whether MOER feeds the customer number or is reported separately. Customer-output framed as Scope 3 Cat 8 (upstream leased assets).
- **A3**: not separately disclosed in customer report.
- **A4**: implicit. Under the metered-per-server pattern, idle servers in a DC contribute kWh that get allocated across customers via the byte/machine-utilization split. Full equations would be needed to quantify how this distributes.

### Cloudflare — Carbon Impact Report

- **A1**: bytes delivered (account-level only; no per-service breakdown).
- **A2**: external benchmark. `data-transfer (bytes) × per-request energy factor`; factor derived from public DC-energy benchmarks (IEA, EPA, DEFRA) + internal Cloudflare PoP-level emission scores. Per-PoP factors not tabulated publicly.
- **A3**: **excluded.**
- **A4**: n/a (no overhead term).
- **Framing differentiator**: headline is "*carbon saved* vs average network", not absolute emissions.

### Fastly — Sustainability Dashboard

- **A1**: bytes (Delivery), CPU-time (Compute). Methodology page explicitly: *power apportioned by CPU-time across processes; does not account for variation in fleet CPU utilization, time-based variation, or hardware-based power-consumption modeling*.
- **A2**: external benchmark (BSR Future of Internet Power) + per-facility colocated electricity. 25% adjustment applied to cache-server electricity when PDU-data discrepancies occur. PUE / renewable % / EFs only ever available for the *previous year* — ~12-month lag baked in.
- **A3**: **excluded.** Material extraction, transport, manufacturing, construction, EoL all out of scope.
- **A4**: shared-process overhead distributed to customers; no fleet-utilization adjustment.
- **Scope quirk**: no Scope 1 (Fastly is leased colocations only).

---

## State of the practice — breadth of customer-facing carbon accounting

The inventory in `carbon_accounting_methodologies/` covers 48 cloud providers surveyed for the appendix table (May~2026). The disclosure breakdown (status taxonomy mirrors the appendix; see also `non-customer-tool-providers.md`):

| Status | Definition | Count |
|---|---|---|
| Per-customer tool | First-party per-tenant carbon dashboard | **12** |
| Assured GHG report | Externally-assured corporate Scope 1/2/3 inventory; no per-customer surface | **5** |
| Self-reported | Corporate Scope 1/2/3 inventory or substantive operational metrics; no external GHG assurance | **9** |
| Marketing claim | Pledges or qualitative "renewable" / PUE statements only | **8** |
| No disclosure | Nothing surfaced through our search | **14** |

Key observations for the §3 "poor SOTA" paragraph:

- **Roughly 1 in 4 providers gives customers a per-account carbon number at all.** The other ~75% leave customers unable to source even a credible Scope-3 Cat-1 input for the cloud services they purchase.
- **The fastest-growing segment has no tools.** Every AI/GPU "neocloud" surveyed — CoreWeave, Lambda, Hyperstack, Verda (ex-DataCrunch), RunPod, Together AI, Fireworks AI, Replicate, plus DigitalOcean-acquired Paperspace — ships only marketing-grade renewable/PUE claims or no disclosure. Compute capacity for AI training/inference is being built out at the fastest pace in cloud history with the *least* customer carbon transparency.
- **Providers without customer tools publish *corporate* GHG numbers but offer no per-customer allocation.** A customer cannot use a corporate total to compute their share, because there is no allocation rule and no per-account surface. They are reporting in compliance for themselves, not enabling their customers' reporting.
- **PaaS / Jamstack providers inherit-without-disclosing.** Vercel, Netlify, Fly.io, Render run on AWS/GCP underneath but expose neither inherited Big-3 figures nor any first-party number — the upstream allocation is invisible at this layer.
- **The only providers with *third-party-assured customer data* (not just methodology) are at most one.** Alibaba (Bureau Veritas, ISO 14064-3) is the lone per-customer-tool example; everyone else's assurance covers the methodology document, not the per-customer numbers.

Net: customers wanting GHG-Protocol-compliant Scope-3-Cat-1 inputs from their cloud spend have 12 candidate providers; 8 of those (AWS, GCP, Azure, Oracle, IBM, OVHcloud, Scaleway, Alibaba) cover compute meaningfully, and **none of those 8 publishes a tool whose implementation has been independently verified end-to-end**.

---

## Temporal granularity audit (customer-facing)

A separate question from allocation method: at what time resolution does the customer actually see the number? Verified across the 11 documented per-customer tools (T Cloud Public excluded — launch blog does not specify granularity):

| Provider | Customer-facing granularity | Lag | Source |
|---|---|---|---|
| AWS | monthly | ~21 d (15–21 of following month) | `aws-ccft-methodology-model3.pdf` |
| GCP | monthly (internal hourly via Borg + per-region hourly CFE % is separate, not customer-allocated) | ~15 d | Schneider & Mattia §3 |
| Azure | monthly (Carbon Optimization + EID) | ~19 d (data for prev month by day 19 of current) | `azure-carbon-optimization-methodology-2026-05.md` §1 |
| Oracle | not stated explicitly; presumed monthly | n/a | `oracle-power-based-calc-releasenote-2025-06.md` |
| IBM | month / quarter / year | n/a | `ibm-carbon-calc-methodology-v3.pdf` |
| Alibaba | not stated explicitly | n/a | Alibaba docs |
| OVHcloud | monthly + yearly (PDF reports, no interactive sub-monthly) | n/a | `ovh-eit-methodology-v2-2025.pdf` |
| **Scaleway** | **daily** (single-month view) / monthly (multi-month view) | next-day | `scaleway-methodology-docs-2026-05.md` §7.2 |
| Akamai | not stated explicitly; 400-day retention with year-over-year comparison | n/a | Akamai blog compilation |
| Cloudflare | not stated explicitly | n/a | Cloudflare 2023 impact report |
| **Fastly** | **daily** (also facility / country / state-or-region / global aggregations) | ~12-month-old EFs baked in | Fastly methodology page |

**Result: Scaleway and Fastly are the only per-customer-tool providers publishing daily customer-facing emissions data.** Everyone else is monthly. *None publishes hourly customer data.* GCP publishes per-region hourly CFE %, but that's a separate signal from the customer-allocated number — a customer can't read their own hourly emissions from GCP's tool.

The Scaleway and Fastly daily numbers are structurally different from each other:
- *Fastly* uses previous-year PUE/EFs in a daily-resolved usage calculation — the daily resolution comes from usage volume × annual-baked factor.
- *Scaleway* uses *actual CPU consumption* in the daily Boavizta-profile pipeline — the daily number reflects daily load.

Sub-monthly customer-facing granularity is therefore both rare *and* differently meaningful between the two providers that offer it.

---

## Cross-cutting findings

The detailed compliance posture, GHG-Protocol gap matrix, and gold-standard scorecard live in `cross_provider_synthesis.md`. The taxonomy-relevant cross-cuts are:

1. **No per-customer-tool tool publishes a measured-energy customer allocation that we can verify.** The ideal weighting factor — per-customer kWh — is claimed only by Oracle (power-based mode, release-note URL only) and Akamai (blog, no equations); neither is PDF-grounded. GCP measures power physically internally but the customer-facing step re-projects to vCPU-hours × list-price. Every other per-customer-tool provider allocates by usage-units (good proxy for network where energy ≈ linear in bytes; poor proxy for compute where energy is nonlinear in load). This is the practical bound on what carbon-aware computing can change in the *reported* footprint: where the unit is bytes, reducing load reduces the number; where the unit is vCPU-hours/instance-hours/`$`-spend, reducing load *at fixed SKU and duration* does not.

2. **Three A2 patterns dominate, not three families of providers.** *Meter-then-bucket* (AWS-FS, GCP-internal, Oracle-power-based, IBM, Alibaba). *Price- or revenue-proportional* (AWS-nFS, GCP-customer-stage, Azure, Oracle-spend-based). *Component-LCA × inventory* (OVHcloud, Scaleway). Most providers use *more than one* — the per-provider story is a mix, not a single label.

3. **Embodied A3 splits orthogonally to A2.** Big-3 + Oracle + Alibaba bundle embodied into the per-unit factor (or exclude it); OVHcloud + Scaleway publish a separate LCA term with traceable per-component factors; Cloudflare/Fastly exclude entirely.

4. **A4 idle/overhead is undisclosed for almost everyone.** GCP (proportional) and OVHcloud (flat-per-server + 100%/24×7 baseline) are the only providers that document this dimension. Big-3 fleet-monthly embodied therefore mechanically decreases as equipment ages past the amortisation window (4 yr GCP, 6 yr AWS/Azure) — independent of actual environmental impact.

5. **Assurance posture is shallow across the board.** Apex (AWS) covers Model 3.0.x Scope-3 Cat 2/3/4 methodology at limited assurance; WSP (Azure) covers Scope-3 doc only; Fraunhofer (GCP) covers LCA methodology only. No Big-3 has its customer tool end-to-end audited. Alibaba's Bureau Veritas data assurance is the lone exception in the per-customer-tool set.

---

## Inconsistencies found vs `old/Accounting.md` and `old/SCHEMA.md`

These are the substantive places where the old documents diverge from what the primary sources actually say. The merged doc above resolves each.

1. **AWS allocation unit.** `SCHEMA.md` set `usage_allocation_unit: "instance-hours per service"`. The PDF §4.2 (Eq 36–37) shows the unit is *per rack type*, not per service — *NIH* for EC2 racks, *GB-month* for S3 racks, etc. Different services on the same rack share the rack's unit basis. Resolved by the per-rack-type phrasing in the AWS block above.

2. **AWS building embodied — version and date.** `SCHEMA.md` noted "buildings included (added Oct 2024)". The buildings addition shipped with **Model 3.0 in Oct 2025**; Model 3.0.1 (Apr 2026) was a minor bugfix on top. The 2024 date is wrong; the version attribution to 3.0.1 is also imprecise.

3. **AWS non-foundational list.** `SCHEMA.md` named "Lambda, SageMaker, Athena, Redshift" as non-foundational. The methodology PDF does not classify specific services; the named-services list (EC2, S3, EBS, Lambda, SageMaker) is presented in `aws/README.md` as "named as covered services without being classified." `SCHEMA.md` was more confident than the source warrants. Above I leave the classification open.

4. **GCP embodied allocation method.** `SCHEMA.md` set `embodied_carbon_allocation_method: proportional_to_energy` based on the Schneider & Mattia "non-electricity Scope 3 allocated by `(customer electricity)/(total electricity)` ratio". That's correct for non-electricity Scope 3 broadly, but the underlying *customer-electricity* number is itself the price-proportional × vCPU-hour quantity from §3.6. So embodied does *not* track physical hardware, it tracks the price-derived energy proxy. Worth flagging explicitly when discussing per-SKU embodied attribution.

5. **Azure usage definition.** Both old docs flagged the 2021 ("normalized cost metric") vs 2025 ("compute/storage/data-transfer time") tension. This remains open; Microsoft has not clarified. Above I quote both verbatim and note the gap rather than picking one.

6. **Oracle.** `SCHEMA.md` covered only Big-3 — Oracle was absent. `old/Accounting.md` mentions Oracle's power-based and spend-based modes but cites the OCI docs page only. The PDF in `references/` is the *2023 v1.0 revenue-based brief*; it does **not** document power-based. The merged doc above documents what the PDF supports and flags the power-based gap.

7. **"Three methodology families" framing** (used in `cross_provider_synthesis.md` and `paper/paper.tex` §3). This taxonomy puts AWS-foundational and OVHcloud-dedicated in different families even though both compute `Σ (customer_usage_units × per-unit factor)`. The shared template above is the more honest decomposition. `cross_provider_synthesis.md` needs the §"Three methodology families" section replaced with a pointer to this file.

8. **AWS idle / reserve-capacity allocation is documented, not undisclosed.** Both old docs treat AWS A4 as opaque. §4.2 of the AWS methodology PDF ("Utilization cases", following Eq 38–39) explicitly describes a two-regime rule: mature racks absorb idle into the user base proportionally; ramp-up racks (<12 mo) pull the *extra* low-utilisation emissions out and spread them as a global overhead across all services using that rack type. This is a real disclosed allocation rule, comparable in detail to GCP's idle-proportional rule. Only Azure and most of the rest remain undisclosed on this dimension.

9. **`old/Accounting.md` general staleness.** Outside the items above, the notebook predates Sustainability Console (Mar 2026), Model 3.0.1 (Apr 2026), CHEM 2026, OVH EIT v2 (Apr 2025), Scaleway 7-product coverage, and the Akamai Linode-coverage-gap verification. Treat as a historical scratchpad; the canonical references are now the per-provider folder READMEs.

---

## Open uncertainties / source gaps (after 2026-05-22 source addition by user)

### Closed by sources you added 2026-05-22

- **Azure A1 ambiguity** — *resolved.* Time-based ("compute, storage, data transfer"). PDF-grounded via `azure/azure-carbon-optimization-methodology-2026-05.md`.
- **Azure A2 (usage factor pattern)** — *resolved as meter-then-bucket black-box.* PDF-grounded.
- **Microsoft 2021 Scope-3 Whitepaper "footnote 2"** — *now PDF-grounded* via `azure/microsoft-scope3-transparency-2021.pdf`. Verbatim non-reconciliation passage (p. 12): *"The underlying methodologies and emissions findings generated from the calculator will differ from those reflected in Microsoft's corporate disclosure."* Citation in `paper.tex` §3 is now load-bearing.
- **Oracle power-based methodology** — *now PDF-grounded* via `oracle/oracle-power-based-calc-releasenote-2025-06.md`. Page release-date June 30, 2025 captured. Service list still not enumerated by Oracle.
- **Akamai equations / energy-metering claim** — *now PDF-grounded* via `akamai/akamai-emissions-reporting-policy-2025.pdf` + `akamai-carbon-calculator-blog-compilation-2026-05.md`. Per-server kWh metering verbatim-quoted; full per-customer equations still not published.
- **Scaleway per-product formulas + actual CPU consumption** — *now PDF-grounded* via `scaleway/scaleway-methodology-docs-2026-05.md`. Boavizta consumption profiles + actual CPU consumption for monthly reports + daily granularity all captured verbatim.

### Still open (provider would need to publish more)

1. **AWS foundational/non-foundational complete list** and **fleet-share allocated by revenue**. AWS will not publish either; the percentage in particular would be informative for sizing the residual in §4.

2. **AWS rack→service utilization-feed**. The methodology PDF does not show whether internal utilization telemetry feeds the per-unit factor at the rack→service stage. Marketing language hints at it; the formal document does not confirm.

3. **AWS Sustainability service successor docs** (`docs.aws.amazon.com/sustainability/latest/userguide`) — JS-rendered SPA, WebFetch returned empty. CCFT sunsets 2026-06-30. If you can fetch the successor methodology in a browser before that date, we can document any continuity gaps.

4. **Oracle power-based service coverage list** — release note states *"only supported by some OCI services"* without enumerating which.

5. **Akamai full per-customer equations**. The byte-share × DC-machine-utilization formula is stated qualitatively; the actual weighting equations remain unpublished.

6. **Cloudflare per-PoP energy factor** values. Formula is `bytes × per-request energy factor` with EFs from IEA/EPA/DEFRA; per-PoP factor tables not published. The 2025 Impact Report PDF may have more detail; current `references/` has the 2023 report.

7. **Azure DC-level utilization rates**. Needed to quantify the implicit overhead that the meter-then-bucket pattern hides in the per-unit factor. Microsoft does not publish.

8. **IBM v5 / Envizi cloud-specific methodology PDF** — IBM Envizi Emissions API GA'd Apr 2026 with claimed expanded Scope-3 + embodied + EoL via CCF + ML, but no v5 cloud-carbon methodology PDF is published. v3 PDF is in `references/`.

9. **Alibaba**: no PDF available; methodology is web-only and per-service intensities are unpublished. Bureau Veritas data assurance is the lone differentiator.

10. **Akamai customer-reporting cadence**: 400-day retention + YoY comparison is documented, but the dashboard refresh cadence (daily/weekly/monthly) is not.
