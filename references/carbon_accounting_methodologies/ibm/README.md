# IBM Cloud Carbon Calculator

**Customer tool:** IBM Cloud Carbon Calculator (console + REST API; integrates into IBM Envizi).

## Authoritative source in this folder

- `ibm-carbon-calc-methodology-v3.pdf` — methodology v3 (foundational).
- **Methodology v5 (2025/2026 Update)**: Transition to automated, data-driven accounting integrated with IBM Envizi ESG Suite.

## Provider URLs

- Envizi Emissions API (Apr 2026): https://www.ibm.com/apidocs/envizi-emissions
- Excel Integration launch (May 2026): https://www.ibm.com/blog/ibm-envizi-excel-integration/

## Methodology summary

### Version 5 (2025-2026 Update)
- **Scope coverage**: Expanded to include **Embodied Emissions (Scope 3)** and more granular AI workload tracking.
- **Embodied Carbon**: Uses **Cloud Carbon Footprint (CCF)** methodology as a base, enhanced by IBM's ML models to account for hardware manufacturing and end-of-life.
- **AI Workload Granularity**: Enhanced tracking for high-density AI/HPC workloads, identifying energy "hot spots."
- **Integration**: Fully integrated with IBM Envizi ESG Suite via REST API (launched Apr 2026).

### Calculation
`total electricity consumption per service × PUE_location × CEF_location`, summed across service / location / client account.

- Per-location Carbon Emission Factor (CEF) and per-location PUE.
- ML / "advanced algorithms" cited for pattern + anomaly detection on top of the base electricity model.

### Granularity
Month / quarter / year; service-level.

### Standards / assurance
- GHG Protocol formatting.
- **None disclosed** for the calculator itself; press release footnote states "client is responsible for confirming accuracy."

### Replicability
Medium. Formula explicit, API documented; per-service / per-location PUE and CEF values would need to be cross-referenced from external sources.

### Known gaps for rSCI
- Service coverage incomplete + opaque (no public inventory).
- S3 + embodied excluded entirely.
- No assurance.

## Recent verification (2026-05-16)
- Tool GA per IBM newsroom + Computer Weekly.
- Docs URL bot-blocked on WebFetch; could not verify current service coverage live.
- Methodology v3 PDF accessible (download succeeded).
