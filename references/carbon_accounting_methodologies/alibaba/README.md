# Alibaba Cloud — Energy Expert

**Customer tool:** Energy Expert (paid product; platform-level, also serves non-cloud customers).

## No PDF available in this folder

Alibaba does not publish a single methodology PDF. Information below is consolidated from the live docs page and TÜV/Bureau Veritas press releases.

## Provider URLs

- Product page: https://www.alibabacloud.com/en/product/energy-expert
- Sustainability solutions: https://www.alibabacloud.com/en/solutions/sustainability
- Cloud product carbon footprint docs (verified 2026-05-16; last updated Jun 2025): https://www.alibabacloud.com/help/en/energy-expert/support/cloud-product-carbon-footprint
- Launch blog: https://www.alibabacloud.com/blog/alibaba-cloud-launches-carbon-management-solution-energy-expert_599071
- Press release: https://www.alibabacloud.com/press-room/alibaba-cloud-launches-carbon-management-solution
- TÜV Rheinland certification press: https://www.tuv.com/press/en/press-releases/alibabacloud-energyexpert.html
- Customer-focused emission targets blog: https://www.alibabacloud.com/blog/alibaba-cloud%E2%80%99s-energy-expert-helps-companies-meet-emission-targets_600035

## Methodology summary (verified 2026-05-16)

### Surface
- Platform-level paid product (not a built-in console feature of every Alibaba Cloud account).
- Also serves customers measuring their own (non-cloud) operations.
- Per Alibaba docs: measures "GHGs emissions indirectly caused by enterprises or individuals when using cloud services," derived from data center energy consumption powering customer resources — **not** the customer's own operations.

### Service coverage
- Computing, storage, network, database, CDN. "Further products planned."
- No public per-service inventory beyond the categories above.

### Scope coverage (per Alibaba docs)
- **Scope 1**: included (direct operations).
- **Scope 2**: included (purchased electricity for production).
- **Scope 3**: included **only for "leased computer rooms"** — i.e., emissions where Alibaba Cloud itself is a leaseholder. Broader S3 categories not addressed in public docs.

### Embodied carbon
- **Not addressed in public docs.**

### Energy model
`per-IDC PUE × resource sales × green-power-usage ratio × technical carbon-reduction measures`

### Allocation chain (explicit, three-stage)
1. IDC level
2. Cloud product level
3. Cloud account level — final attribution to tenants is by the actual amount of cloud resources used

### Standards
- GHG Protocol Corporate Standard.
- **ISO 14064-3:2019** (verification / GHG statement inventory guidelines).
- CEC (China Environment United Certification Center) procedures.

### Assurance — *the differentiator*
- **Bureau Veritas (Beijing)** — third-party data assurance for the cloud-customer methodology.
- **TÜV Rheinland certification** for customer outputs.
- Alibaba's July 2023 claim: "first enterprise in China to pass the evaluation of carbon accounting services for cloud services."

This is the **only third-party data assurance** of a customer-facing cloud carbon tool in the entire SOTA set. AWS/GCP/Azure assurers cover methodology documents only.

### Replicability
Low–medium. Allocation chain stated but emission factors and per-service intensities not published.

### Pricing
Paid product. Specific pricing not documented publicly.

### Known gaps for rSCI
- Methodology document not in PDF form; cannot independently verify equations.
- Embodied carbon not addressed in public docs.
- Pricing/access barrier for academic verification.
