# AWS Carbon Accounting

**Customer tool:** AWS Sustainability Console. Built on methodology Model 3.0.1 (Apr 2026).

## Authoritative sources in this folder

- `aws-ccft-methodology-model3.pdf` — methodology document (the canonical reference for any AWS claim). **Note:** this PDF is the Oct~2025 Model~3.0 version; the upstream URL now serves the Apr~2026 Model~3.0.1 revision. Re-download if a 3.0.1-specific claim is needed.
- `aws-ccft-assurance.pdf` — Apex Companies LLC assurance statement (ISO 14064-3:2019, *limited* assurance, ±5% materiality). **Scope of assurance: Scope-3 Cat 2/3/4 methodology only.** Scope 1, Scope 2, and tool implementation are *not* within the assurance boundary.
- `amazon-carbon-methodology.pdf` — Amazon corporate-wide carbon methodology. Use this for the *corporate-disclosure* side when comparing to the customer-tool side (the gap is the rSCI residual at AWS).

## Provider URLs (for fresh verification)

- Sustainability Console landing: https://aws.amazon.com/sustainability/tools/console/
- Sustainability Console launch blog (31 Mar 2026): https://aws.amazon.com/blogs/aws/announcing-the-aws-sustainability-console-programmatic-access-configurable-csv-reports-and-scope-1-3-reporting-in-one-place/
- CCFT (legacy) landing: https://aws.amazon.com/sustainability/tools/aws-customer-carbon-footprint-tool/
- CCFT docs: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/what-is-ccft.html
- Overview & coverage: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-overview.html
- Estimation method: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ccft-estimation.html
- Methodology PDF: https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-methodology.pdf
- Assurance PDF: https://sustainability.aboutamazon.com/aws-customer-carbon-footprint-tool-methodology-assurance.pdf
- Amazon corporate carbon methodology: https://sustainability.aboutamazon.com/carbon-methodology.pdf
- Release notes: https://docs.aws.amazon.com/ccft/latest/releasenotes/what-is-ccftrn.html
- Scope-3 expansion blog: https://aws.amazon.com/blogs/aws/aws-customer-carbon-footprint-tool-now-includes-scope-3-emissions/
- Methodology-update blog: https://aws.amazon.com/blogs/aws-cloud-financial-management/updated-carbon-methodology-for-the-aws-customer-carbon-footprint-tool/

## Methodology summary (verify against `aws-ccft-methodology-model3.pdf` before quoting in paper)

### Surface
- **AWS Sustainability Console** (since 31 Mar 2026): unified replacement for the Billing-console-only CCFT view. Includes:
  - Public REST API: `get-estimated-carbon-emissions`
  - AWS SDK + CLI access
  - Filterable CSV export (Region / service / account / Scope)
  - Preset monthly and annual reports
  - Fiscal-year configuration
  - IAM permissions independent of Billing
- Data history back to January 2022. ≤21-day lag, monthly granularity. 38-month retention.
- Default view: market-based; LBM toggleable.

### Scope coverage
- **Scope 1**: included.
- **Scope 2**: LBM + MBM in parallel.
- **Scope 3**: Cat 2 (capital goods, **including buildings and non-IT** since Oct 2025), Cat 3 (FERA), Cat 4 (upstream transport).
- **Excluded**: Scope 3 Cat 5, 6, 7, 9, 12 — without a published materiality assessment.

### Embodied carbon (Cat 2)
- **Hybrid LCA** via a 4-pathway waterfall:
  1. PLCA-Eng (process-LCA from engineering data)
  2. ML-extrapolation
  3. Representative Category Average LCA (K-NN)
  4. Component-EIO-LCA (cost-based fallback using NAICS sector factors)
- **Pathway distribution across the fleet not disclosed.**
- Lifetime: IT 6 yr; buildings 50 yr (added Oct 2025); zero past-amortisation.
- A 30-yr building assumption would raise annual building embodied carbon by ~67% (arithmetic identity).

### Allocation
- **Tier 1 — Foundational services** ("AWS services that have dedicated server racks"): allocation = instance-hours. Described as physical allocation based on resource utilization (CPU, memory, storage I/O, network). Whether internal utilization telemetry feeds the per-instance-hour factor is **not publicly disclosed**.
- **Tier 2 — Non-foundational services** ("AWS services with no dedicated server racks, which rely on foundational services"): allocation = **equivalent revenue** — "a standardized measure of usage-based revenue that excludes pricing variation factors such as discounts."
- **Critical transparency gap**: the foundational vs non-foundational distinction is defined but the methodology document **does not publish the list of services in each category**, nor the share of total CCFT emissions allocated by equivalent revenue. EC2, S3, EBS, Lambda, and SageMaker are named as covered services without being classified.

### Assurance
- Apex Companies LLC, ISO 14064-3:2019, **limited** assurance, ±5% materiality.
- Scope of engagement: **Scope 3 Cat 2/3/4 methodology only**.
- Scope 1, Scope 2, and tool implementation **not** in the assurance boundary.

### EAC matching
- Not disclosed; assumed annual.

### Known gaps for rSCI
- Foundational/non-foundational service split (unpublished list, unpublished share).
- EAC temporal matching not stated.
- Share of fleet on each LCA pathway not disclosed.
- Cat 5/6/7/9/12 excluded without materiality assessment.

## Recent verification (2026-05-16)

- Launch of Sustainability Console (Mar 2026) confirmed via launch blog.
- Methodology document still v3.0 (Oct 2025).
- Services covered (named): CloudFront, EC2, S3 — full list of foundational vs non-foundational still unpublished.
