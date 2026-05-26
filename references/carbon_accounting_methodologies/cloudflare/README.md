# Cloudflare — Carbon Impact Report

**Customer tool:** Carbon Impact Report in the Cloudflare dashboard. Available to all plans (free + paid).

## Authoritative source in this folder

- `cloudflare-impact-report-2023.pdf` — Cloudflare 2023 Impact Report (~10 MB). Methodology snippet is a small section of this larger sustainability report.

## Provider URLs

- Impact landing: https://www.cloudflare.com/impact/
- Sustainability blog tag: https://blog.cloudflare.com/tag/sustainability/
- Carbon-impact tool methodology blog: https://blog.cloudflare.com/understand-and-reduce-your-carbon-impact-with-cloudflare/
- SBTi commitment & savings: https://blog.cloudflare.com/switching-cloudflare-cut-your-network-carbon-emissions-sbti/
- 2021 Impact Report PDF: https://www.cloudflare.com/resources/assets/slt3lc6tev37/1vmmNMaaktXDk5iHxxDdCj/ebe40635588eaafa15ab89944ff9a36b/Cloudflare_Impact_Report_2021.pdf
- 2023 Impact Report PDF (in folder): https://cf-assets.www.cloudflare.com/slt3lc6tev37/3Z7xOV53lGEIAwCqw5SncT/69eaca7bd5d2395ee0274b15e7854dd6/2023_Impact_Report.pdf

## Methodology summary (verify against `cloudflare-impact-report-2023.pdf` + blog before quoting)

### Surface
- Dashboard report; **available to all plans, including free**.

### Service coverage
- Account-level edge bytes across the global PoP network.
- **No per-service breakdown** described.

### Customer framing
- Presented as a **Scope 3** report from the customer's perspective.
- **Primary narrative**: "carbon saved by using Cloudflare vs. average network" — i.e., the headline is *savings vs. industry baseline*, not absolute emissions. This is a meaningful difference from the other per-customer tools.

### Calculation method
- Per-customer **data-transfer (bytes) × per-request energy factor**.
- Energy factor derived from public DC-energy benchmarks plus internal Cloudflare PoP-level emission scores.
- Emission-factor sources: IEA, EPA, DEFRA.

### Scope coverage
- Scope 3 customer-side only (savings framing).
- Cloudflare's own Scope 1 / 2 reported separately in corporate sustainability reports under SBTi commitment.

### Embodied carbon
- **Not included.**

### Granularity
- Account-level; no per-service breakdown.

### Standards
- No formal GHG-Protocol scope-3-category alignment cited.

### Assurance
- **None** for the customer tool.
- Corporate emissions reported under SBTi commitment.

### Replicability
- **Low** — the per-request factor and PoP-specific scores are not tabulated publicly.

### Known gaps for rSCI
- No absolute-emissions framing.
- No embodied carbon.
- No formal Scope-3-category alignment.
- Per-PoP factors undisclosed.
- WAF / Workers / Pages / Image Resizing all rolled into the bytes-based number.

## Recent verification (2026-05-16)
- Tool confirmed available to all plans (free + paid).
- "Savings vs. average network" framing confirmed via methodology blog.
- WAF / Network Firewall / DDoS / Image Resizing / Pages / Workers KV mentioned as additional carbon-reduction benefits but not separately measured.
