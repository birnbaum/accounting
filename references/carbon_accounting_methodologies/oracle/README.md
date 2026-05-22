# Oracle Cloud Infrastructure (OCI) — Carbon Emissions Analysis

**Customer tool:** OCI Carbon Emissions Analysis (in OCI Console + Usage API).

## Authoritative sources in this folder

- `oracle-technical-carbon-guidance.pdf` — Oracle's published methodology guidance (Feb 2023, v1.0). **Spend/revenue-based only** — predates the power-based rollout. Formula: customer revenue × regional emission intensity factor = estimated Scope 3 emissions.
- `oracle-power-based-calc-releasenote-2025-06.md` — Compiled text of the OCI release note for power-based calculation support (page release date: June 30, 2025; fetched 2026-05-22). Documents LBM/MBM distinction, EU/UK regulatory alignment, and zero-MBM in European regions. **Note:** specific service coverage list (which services are power-based vs spend-based) is not enumerated in public docs.

## Provider URLs

- Docs entry: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/emissions-management.htm
- Power-based calculation release note (Feb 2026): https://docs.public.content.oci.oraclecloud.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm

## Methodology summary

### Calculation modes
- **Power-based** (primary) — tracks actual kWh consumed by hardware. Recommended for "financial-grade" / regulatory reporting. Covers Compute, Storage, and Database services.
- **Spend-based** (fallback) — customer pre-discount spend × regional factor. Available for all services but flagged as "less exact" and not recommended for regulatory reporting.

### Scope coverage
- **Scope 1**: not surfaced at customer.
- **Scope 2**: LBM + MBM documented.
- **Scope 3**: not surfaced at customer.
- **EU regions report MBM = 0 by design** (Oracle's PPA contracts produce zero market-based emissions in European regions).

### Embodied carbon
- **Not included.** Power-based mode is explicitly operational only.

### Emission factors
- Regional grid mix; specific factor values not documented publicly.
- Tied to the Oracle Clean Cloud OCI Data Sheet (FY25).

### Assurance
- **None disclosed** for the customer-facing tool. Oracle's corporate sustainability disclosure is separate.

### Provider's own caveat (in Oracle's docs)
> *"Carbon Emissions Analysis isn't intended to be used as a developer tool to reduce emissions. All customer carbon emissions provided ... are estimates."*

This is useful as a direct provider acknowledgement that the tool is for reporting, not workload-shaping.

### Replicability
Medium. Allocation logic described qualitatively but emission factors and per-service energy intensities not tabulated.

### Known gaps for rSCI
- S1 and S3 not surfaced.
- Embodied not included.
- Power-based service list undisclosed.
- Spend-based is the broadest coverage — same allocation pathology as AWS revenue-fallback.

## Recent verification (2026-05-22)
- Release note fetched; power-based calculation confirmed live as of June 30, 2025.
- "Feb 2026" in prior notes was researcher annotation, not the page's own date.
- Service list for power-based coverage still not enumerated in public docs.
- Oracle blog (blogs.oracle.com/...) returned HTTP 403 — not accessible via automated crawl.
- "Not intended to reduce emissions" disclaimer confirmed in release note.
- Zero-MBM in European regions confirmed (Oracle PPA contracts).
- Power-based supports both LBM and MBM; spend-based supports MBM only.
