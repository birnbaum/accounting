# Akamai — Carbon Calculator (Akamai Control Center)

**Customer tool:** Per-customer Carbon Calculator inside the Akamai Control Center.

## No PDF available in this folder

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

### Energy model
- Real DC energy use × utilization weighting; not bytes-only.

### Embodied carbon
- Not separately disclosed in the customer report.

### Akamai's own corporate Scopes 1+2
- Published in the corporate sustainability report; not surfaced through this customer tool.
- As of 2022, 64% of Akamai's Connected Cloud is powered by clean energy.

### Standards
- GHG Protocol.
- Customer report is explicitly **Cat-8-compatible**.

### Assurance
- Akamai's corporate emissions are externally reported.
- The **customer-allocated report itself is not separately assured**.

### Replicability
- **Low** — equations not published; customer relies on Akamai's allocation.

### Known gaps for rSCI
- Linode Compute uncovered despite being a major product line.
- Equations not published.
- No tool-implementation assurance.
- Customer-allocated number is Cat-8-shaped — useful for customer inventory but not directly comparable with provider total.

## Recent verification (2026-05-16)
- Carbon Calculator confirmed live in Akamai Control Center.
- Delivery-only coverage confirmed via 2025 customer-reporting blog and supply-chain blog.
- Linode/Compute exclusion confirmed — no mention in any Carbon Calculator coverage description.
