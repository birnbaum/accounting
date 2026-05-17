# Oracle Cloud Infrastructure (OCI) — Carbon Emissions Analysis

**Customer tool:** OCI Carbon Emissions Analysis (in OCI Console + Usage API).

## Authoritative sources in this folder

- `oracle-technical-carbon-guidance.pdf` — Oracle's published methodology guidance. Power-based is the primary mode for CSRD / SB-253 compliance reporting; spend-based remains the fallback for services without power-based coverage.

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

## Recent verification (2026-05-16)
- Tool confirmed live; paying customers only.
- Docs page does not enumerate power-based vs spend-based service lists.
- "Not intended to reduce emissions" disclaimer confirmed in docs page.
