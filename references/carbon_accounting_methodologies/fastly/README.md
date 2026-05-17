# Fastly — Sustainability Dashboard

**Customer tool:** Sustainability Dashboard in the Fastly control panel; API + CSV export.

## No PDF available in this folder

The Fastly 2024 Sustainability Report PDF download is bot-blocked (verified 2026-05-16 — `Access Denied` response). User should manually download from the link below if/when a citable artifact is needed.

## Provider URLs

- Product landing: https://www.fastly.com/products/sustainability-dashboard
- Dashboard docs: https://www.fastly.com/documentation/guides/account-info/account-management/about-the-sustainability-dashboard/
- **Methodology page** (canonical reference): https://www.fastly.com/documentation/guides/account-info/sustainability/our-sustainability-dashboard-methodology/
- 2024 Sustainability Report PDF (gated): https://investors.fastly.com/files/doc_governance/2025/Nov/26/2024-Fastly-Sustainability-Report-290db1.pdf

## Methodology summary (verified 2026-05-16 via methodology page WebFetch)

### Surface
- Control panel + API + CSV download.
- **Granularity**: daily, at facility / country / state-or-region / global levels.

### Service coverage
- **Fastly Delivery + Fastly Compute**.
- **Excludes** third-party cloud hosting (Compute@Edge backends).
- Excludes Fastly's own corporate emissions.

### Scope coverage
- **No Scope 1.** Explicitly excluded — Fastly operates only in leased colocations.
- **Scope 2**: LBM + MBM. Includes IT-equipment electricity in colocated facilities. Renewable accounting: location-based (no renewables) vs. market-based (includes EAC procurement; **Fastly committed to 100% EAC from Jan 2025**, then updated in Sep 2025 to cover 100% of non-renewable grid electricity via high-quality EACs).
- **Scope 3 Cat 3 (FERA)** — upstream fuel-and-energy, T&D losses, well-to-tank.
- **Scope 3 Cat 8** — non-IT equipment in leased assets (cooling, building).

### Embodied carbon
- **Explicitly excluded.** Material extraction, transport, manufacturing, construction, end-of-life all out of scope.

### Energy model
- Power apportioned by **CPU-time** across processes.
- Does *not* account for variation in fleet CPU utilization, time-based variation, or hardware-based power-consumption modeling.
- A **25% adjustment** is applied to cache-server electricity when PDU-data discrepancies occur (infrastructure overhead correction).

### Allocation key
- **Delivery**: network-transfer volume.
- **Compute**: request-time (CPU-time).
- Shared processes: distributed as overhead to customers.

### Renewable accounting
- Operators substantiate renewable-energy procurement via contracts/attestations/EACs.
- No independent audit of the dashboard cited.

### Standards
- GHG Protocol Scope 2 Guidance.
- BSR Future of Internet Power Report methodology.

### Update lag
- PUE, renewable percentages, and emission factors **only ever available for the previous year**.

### Replicability
- Methodology page is the **most explicit allocation rule** in the Tier-A set — both the apportionment rule and the 25% overhead correction are stated.
- Reference factors not fully tabulated, though.

### Known gaps for rSCI
- No Scope 1 (structural).
- No embodied carbon (structural).
- No real-time fleet utilization — power apportioned by CPU-time only.
- Previous-year emission factors mean ~12-month lag baked in.
- No tool-implementation assurance.

## Recent verification (2026-05-16)
- Methodology page WebFetch successful (URL above).
- Most recent commitment date: September 2025 (100% non-renewable grid coverage via EACs).
- Methodology page does not have a "last updated" timestamp.
