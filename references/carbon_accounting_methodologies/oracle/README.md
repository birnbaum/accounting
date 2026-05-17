# Oracle Cloud Infrastructure (OCI) — Carbon Emissions Analysis

**Customer tool:** OCI Carbon Emissions Analysis (in OCI Console + Usage API).

## Authoritative sources in this folder

- `oracle-technical-carbon-guidance.pdf` — Oracle's published methodology guidance.

## Provider URLs

- Docs entry: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/emissions-management.htm
- Viewing carbon emissions reports: https://docs.oracle.com/en-us/iaas/Content/General/Tasks/carbon-analysis-viewreports.htm
- Power-based calculation release note: https://docs.public.content.oci.oraclecloud.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm
- How-to-enable KB: https://support.oracle.com/knowledge/Oracle%20Cloud/3000157_1.html
- Technical carbon calculation guidance PDF (in folder): https://www.oracle.com/a/ocom/docs/corporate/technical-carbon-calculation-guidance.pdf
- Renewable energy guidance PDF: https://www.oracle.com/a/ocom/docs/renewable-energy-guidance.pdf
- Clean Cloud OCI data sheet (FY25): https://www.oracle.com/a/ocom/docs/corporate/citizenship/clean-cloud-oci.pdf
- Green Cloud landing: https://www.oracle.com/sustainability/green-cloud/
- Sustainability hub: https://www.oracle.com/sustainability/

## Methodology summary (verify against `oracle-technical-carbon-guidance.pdf` before quoting)

### Surface
- OCI Console under "Emissions Management" + Usage API.
- Available to all **paying commercial OCI tenancies**. Free tier excluded.
- Requires IAM policy: `carbon-emission-reports` read/manage.
- CSV export.
- **Temporal**: monthly (default) or daily; standard or cumulative.
- **Resource granularity**: date range, compartment, region, service, tag, tenant; spend-based mode adds availability domain, platform (Gen_1/Gen_2), product description, subscription ID.
- 7 default reports: LBM/MBM by service; by service-and-description; by service-and-SKU; LBM/MBM by region; cumulative by region.

### Calculation modes
- **Power-based** — `kWh consumed by service workloads in OCI data centers × regional emission factor`. Allocates DC energy "considering both dedicated and shared hardware across customers." Supported only for a subset of OCI native (**Gen_2**) services. Explicit list of supported services not published.
- **Spend-based** — `customer pre-discount spend × regional emission factor`. Broader service coverage (effectively any service that produces a usage record). Documented as the "less exact" mode.

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
