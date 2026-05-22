# Scaleway — Environmental Footprint Calculator

**Customer tool:** Console + API; monthly/yearly reports.

## No PDF available in this folder

Scaleway publishes methodology as per-product web pages (one page per service), not a single PDF. The 2024 Impact Report PDF (URL below) is annual sustainability messaging, not the calculator methodology.

- `scaleway-methodology-docs-2026-05.md` — compiled methodology from all per-product and reference documentation pages (fetched 2026-05-22 from public GitHub `scaleway/docs-content` repo). Contains verbatim formulas, reference values, temporal granularity details, per-product allocation rules, and research flags.

## Provider URLs

- Calculator landing: https://www.scaleway.com/en/environmental-footprint-calculator/
- **Concepts**: https://www.scaleway.com/en/docs/environmental-footprint/concepts/
- **Calculation breakdown**: https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator/
- Estimation doc: https://www.scaleway.com/en/docs/environmental-footprint/additional-content/environmental-footprint-calculator-estimation/
- **Calculation reference values**: https://www.scaleway.com/en/docs/environmental-footprint/additional-content/calculation-values-reference/
- Dashboard how-to: https://www.scaleway.com/en/docs/environmental-footprint/how-to/environmental-footprint-dashboard/
- Monthly footprint how-to: https://www.scaleway.com/en/docs/environmental-footprint/how-to/track-monthly-footprint/
- Methodology blog: https://www.scaleway.com/en/blog/overcoming-the-challenges-of-cloud-environmental-impact-measurement/
- CSRD positioning blog: https://www.scaleway.com/en/blog/scaleways-environmental-footprint-calculator-your-best-partner-for-csrd-reporting/
- Environmental leadership page: https://www.scaleway.com/en/environmental-leadership/
- 2024 Impact Report PDF: https://www-uploads.scaleway.com/Impact_Report2024_A4_EN_9a7bd88445.pdf (currently 404 — replace URL if found)

## Methodology summary (verified 2026-05-16)

### Surface
- Console + API; monthly and yearly reports.
- **Temporal granularity:** Daily data generated internally; dashboard shows daily data when a single month is selected, monthly data when multiple months are selected. Monthly PDF reports use actual (not estimated) CPU consumption. This is sub-monthly resolution — uncommon among providers (confirmed from `environmental-footprint-dashboard.mdx` validation 2026-01-23).

### Service coverage (per docs page)
- 7 products with per-product calculation pages:
  - Bare Metal
  - Instances
  - Block Storage
  - Object Storage
  - Load Balancer
  - Kubernetes (Kapsule)
  - Managed Databases

### Scope coverage
- Scope 1, Scope 2, Scope 3. Scaleway reports **Scope 3 ≈ 80%** of total service emissions.

### Embodied carbon
- Yes — LCA via partnership with **Boavizta** (French association maintaining open LCA impact models for hardware, including older servers).
- Construction (non-IT) impacts use ADEME generic factors (per m² datacenter) where site-specific data is missing.

### Energy model
- Per-resource calculations exposed (each product has its own per-product methodology page).
- LCA-based for embodied; ADEME generic factors for construction.

### Standards
- **ADEME PCR for Datacenter and Cloud** — the French national ecological agency's standardized framework.
- Co-developed with **IJO** consultancy.

### Multi-criteria
- **Water consumption** included alongside carbon — uncommon among providers.

### Assurance
- None disclosed.

### Acknowledged uncertainty
- Data-center-construction factors carry high uncertainty.
- Non-IT impacts updated annually from personnel statistics to avoid seasonal distortion.
- Methodology described as "actively evolving."

### Replicability
- Per-product calculation pages + reference-values page intended to support customer recompute.
- Quality of disclosure is among the best in the SOTA set.

### Known gaps for rSCI
- No assurance.
- 7 named products; longer-tail Scaleway services (Apple Silicon, FunctionsAsAService, IoT Hub, etc.) coverage not enumerated.
- Methodology spread across many web pages; no single PDF citable artifact.

## Recent verification (2026-05-22)
- 7 products covered confirmed via Concepts page.
- Impact Report 2024 PDF URL returned 404 ("NoSuchKey" via S3); URL may have rotated.
- Full methodology compiled into `scaleway-methodology-docs-2026-05.md` from GitHub `scaleway/docs-content` source MDX files.
- **Daily granularity confirmed** in dashboard (single-month filter shows daily data; `environmental-footprint-dashboard.mdx` validation 2026-01-23).
- Per-product formulas verified for Bare Metal, Instances, and Block Storage (MDX source dates: bare-metal 2025-05-27, instances 2025-10-01, block-storage 2025-07-10).
- Reference values page (validation 2025-06-09): France energy mix = 0.044 kgCO₂e/kWh; examples in product pages use older values (0.056–0.065) — methodology is actively updated.
