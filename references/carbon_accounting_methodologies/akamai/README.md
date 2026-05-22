# Akamai — Carbon Calculator (Akamai Control Center)

**Customer tool:** Per-customer Carbon Calculator inside the Akamai Control Center.

## Sources in this folder

- `akamai-carbon-calculator-blog-compilation-2026-05.md` — compiled blog content. Source 1 (May 2025 Cat-8 customer-reporting blog by Mike Mattera) pasted in full by researcher 2026-05-22. Three other blog URLs still return HTTP 403.
- `akamai-emissions-reporting-policy-2025.pdf` / `.txt` — **Akamai Environmental Policy: Customer Emissions Data** (published 2025-01, 7 pp.). Formal policy governing what Akamai provides to customers and what it refuses to disclose. Cite this for replicability / assurance gaps.

Akamai does not publish a single methodology PDF. The information below consolidates the blog posts and the corporate sustainability PDF.

## Provider URLs

- Sustainability hub: https://www.akamai.com/company/corporate-responsibility/sustainability
- Supply-chain Carbon Calculator blog: https://www.akamai.com/blog/culture/akamai-carbon-calculator-supply-chain-emissions
- 400-day-data Carbon Calculator blog: https://www.akamai.com/blog/sustainability/new-carbon-calculator-report-supports-400-days-data
- Customer Scope 3 Cat-8 reporting blog (2025): https://www.akamai.com/blog/sustainability/2025/may/what-akamai-is-doing-for-customer-reporting
- TechDocs Carbon Calculator changelog: https://techdocs.akamai.com/reporting/changelog/mar-31-2022-new-report-carbon-calculator
- Environmental sustainability PDF: https://www.akamai.com/content/dam/sdl-content/us/en/multimedia/documents/sustainability/environmental-sustainability-at-akamai.pdf
- Sustainability Highlights dashboard (Metrio): https://www.akamaisustainability.com/indicators/our_year_and_looking_ahead

## Methodology summary (verified 2026-05-16)

### Surface
- Per-customer report inside the **Akamai Control Center**.
- Available to **all delivery-product customers**.
- Up to **400 days** of history with year-over-year comparison.

### Service coverage — *the key gap*
- **Delivery products only**.
- **Linode / Akamai Connected Cloud Compute is NOT covered** by the Carbon Calculator, despite the Linode acquisition in February 2022 — verified live 2026-05-16. This is a 4-year gap between acquisition and coverage that remains unclosed.

### Customer scope mapping
- Reported as **Scope 3 Category 8** (upstream leased assets) for the customer — i.e., the number is structured to plug directly into a customer's own Scope 3 inventory.

### Allocation key
- Byte utilization + machine utilization per DC are used to allocate the appropriate proportion of a data center's energy use and emissions to a customer.
- This is real DC-utilization allocation, not bytes-only — distinguishes Akamai from Cloudflare's bytes-only approach.
- Source: May 2025 blog verbatim — see `akamai-carbon-calculator-blog-compilation-2026-05.md`.

### Energy model
- Real DC energy use × utilization weighting; not bytes-only.
- Five emission factor types reported: location-based, market-based, balancing authority, location marginal, and MOER (real-time sub-hourly).
- Report includes: MWh consumed, PUE, renewable share, total emissions impact (MBM), grid losses.

### Embodied carbon
- Not separately disclosed in the customer report.

### Akamai's own corporate Scopes 1+2
- Published in the corporate sustainability report; not surfaced through this customer tool.
- As of 2022, 64% of Akamai's Connected Cloud is powered by clean energy.

### Standards
- GHG Protocol.
- Customer report is explicitly **Cat-8-compatible**.

### Assurance
- Akamai obtains a corporate-level assurance report annually covering "all relevant scopes and categories" (§4.2, policy doc). Published publicly through CDP.
- The **customer-allocated report itself is not separately assured** — customers must arrange and fund their own third-party verification (§2.1, policy doc).
- Scope 3 full-year coverage in customer reports starts from 2022 onward; Akamai will not amend published values prior to 2022 (policy doc §4.1, fn. 1).

### Replicability
- **Low** — equations not published; customer relies on Akamai's allocation.
- Formally confirmed by policy: *"Akamai will not provide access to its proprietary models, algorithms, or underlying data during the audit process or in response to customer requests"* (§3.1, `akamai-emissions-reporting-policy-2025.pdf`).
- On-site audits not permitted (§7.3). Customers cannot meet Akamai's external auditors (§7.4).

### Known gaps for rSCI
- Linode Compute uncovered despite being a major product line.
- Equations not published.
- No tool-implementation assurance.
- Customer-allocated number is Cat-8-shaped — useful for customer inventory but not directly comparable with provider total.

## Recent verification (2026-05-22)
- May 2025 Cat-8 blog (Mattera) read in full (pasted by researcher). Allocation key verbatim confirmed: byte + machine utilization. Five emission factor types confirmed. No CSRD/SB-253 named; GHG Protocol only. Linode/Compute still absent from coverage language.
- `akamai-emissions-reporting-policy-2025.pdf` read in full. Key additions: (1) non-disclosure of models confirmed in formal policy §3.1; (2) on-site audits not permitted §7.3; (3) customer assurance is customer's own expense §2.1; (4) Scope 3 coverage from 2022 onward; (5) corporate disclosure via CDP only.
- Three other blog URLs still return HTTP 403 from automated agents.
