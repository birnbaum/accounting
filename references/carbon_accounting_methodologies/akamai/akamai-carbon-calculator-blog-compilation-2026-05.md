# Akamai Carbon Calculator — Blog Compilation

**Fetch date:** 2026-05-22
**Note:** All blog URLs returned HTTP 403 for automated crawl. Content below was pasted manually by researcher.

---

## Source 1: Scope 3, Category 8: What Akamai Is Doing for Customer Reporting

**URL:** https://www.akamai.com/blog/sustainability/2025/may/what-akamai-is-doing-for-customer-reporting
**Author:** Mike Mattera
**Date:** May 19, 2025

### Overview

Akamai's Custom Emissions Reports are designed to give customers detailed, credible emissions data for operations conducted on their behalf, specifically to capture Scope 3, Category 8 (Upstream Leased Assets) in customer GHG inventories.

### Scope 3, Category 8 framing

Under GHG Protocol Category 8, any services contracted by an organization with an associated power value that do not appear in Scope 1 or Scope 2 should be included in the customer's Scope 3, Category 8 inventory.
Akamai frames its servers as contracted computing resources: owned and maintained by Akamai, but running on behalf of the customer.

### How Custom Emissions Reports work — four steps

1. **Collecting facility data** — Akamai measures the electricity used by every server and network device in global colocation sites, recording kWh consumed exactly when and where.

2. **Allocating based on use** — customer workloads are mapped to servers, regions, and countries.
   Allocation key (verbatim):
   > *"For instance, your use in a particular data center is measured by byte utilization and machine utilization. We take that data and allocate the appropriate proportion of that data center's energy use and emissions to your account."*

3. **Breaking down by GHG Protocol category** — allocated emissions are categorized so customers can plug them into Scope 3, Category 8 reporting directly.

4. **Providing detailed reports** — includes:
   - Actual energy use (MWh drawn by Akamai equipment)
   - Facility efficiency (PUE metrics)
   - Renewable share (percentage from renewables)
   - Total emissions impact (market-based)
   - Grid losses (carbon impacts from T&D losses)

### Emission factor types used

Five emission factor types applied for continuity:

- **Location-based** — average grid mix for each balancing authority
- **Market-based** — emissions profile of contracted energy sources (PPAs, RECs)
- **Balancing authority** — average grid rates published by regional operators
- **Location marginal** — carbon intensity of the next unit of electricity needed to meet incremental demand
- **Marginal Operating Emissions Rate (MOER)** — real-time, sub-hourly signal showing which generators actually ramp up or down

### Service coverage

Report is for "content delivery and edge computing tasks" — delivery products.
No explicit mention of Linode / Akamai Connected Cloud Compute.
Blog refers to "compute, security software and services, and delivery capacities" broadly but allocation methodology examples focus on delivery.

### Competitive claims (verbatim differentiators vs "other major infrastructure and cloud service providers")

- More complete data (not just a single rolled-up number)
- Tailored for GHG Protocol Scope 3, Category 8
- Granular transparency (by country, not continent-level)
- Easy integration into ESG reporting
- Human-centric service (methodology walkthroughs on request)

### Regulatory context

No explicit mention of CSRD or SB-253 by name in this blog post.
GHG Protocol alignment is the stated standard.

---

## Source 2: Emissions-Reporting-Policy-2025.pdf

**File:** `akamai-emissions-reporting-policy-2025.pdf`
**Status:** PDF provided in ~/Downloads/. Due to macOS sandbox restrictions, automated tools could not copy it.
To add, run:
```
cp ~/Downloads/Emissions-Reporting-Policy-2025.pdf \
  references/carbon_accounting_methodologies/akamai/akamai-emissions-reporting-policy-2025.pdf
pdftotext -layout \
  references/carbon_accounting_methodologies/akamai/akamai-emissions-reporting-policy-2025.pdf \
  references/carbon_accounting_methodologies/akamai/akamai-emissions-reporting-policy-2025.txt
```

---

## Other blog URLs — HTTP 403 (automated crawl)

- https://www.akamai.com/blog/culture/akamai-carbon-calculator-supply-chain-emissions — 403
- https://www.akamai.com/blog/sustainability/new-carbon-calculator-report-supports-400-days-data — 403
- https://www.akamai.com/blog/sustainability/what-akamai-is-doing-for-customer-reporting — 403

**Previously known (from 2026-05-16 manual verification):**
- Supply-chain blog: allocation method is byte utilization + machine utilization per DC (distinguishes Akamai from bytes-only approaches like Cloudflare).
- 400-days-data blog: announces 400-day history and year-over-year comparison for all delivery-product customers.
