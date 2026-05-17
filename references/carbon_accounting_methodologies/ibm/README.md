# IBM Cloud Carbon Calculator

**Customer tool:** IBM Cloud Carbon Calculator (console + REST API; integrates into IBM Envizi).

## Authoritative source in this folder

- `ibm-carbon-calc-methodology-v3.pdf` — methodology v3 (the existence of a v3 implies an iteration history; IBM is treating this as a maintained product).

## Provider URLs

- Product newsroom: https://newsroom.ibm.com/IBM-Cloud-Carbon-Calculator-Aims-to-Help-Organizations-Address-Greenhouse-Gas-Emissions-to-Advance-their-Sustainability-Objectives
- Docs: https://cloud.ibm.com/docs/billing-usage?topic=billing-usage-what-is-cloud-calc
- FAQs: https://cloud.ibm.com/docs/billing-usage?topic=billing-usage-carboncalcfaqs
- API: https://cloud.ibm.com/apidocs/carbon-calculator
- Methodology v3 PDF (in folder): https://cloud.ibm.com/media/docs/downloads/account/carbon-calc-method-v3.pdf
- Envizi (separately-licensed ESG suite): https://www.ibm.com/products/envizi
- Computer Weekly coverage: https://www.computerweekly.com/news/366545992/IBM-debuts-Cloud-Carbon-Calculator-to-help-enterprises-manage-their-GHG-emissions

## Methodology summary (verify against `ibm-carbon-calc-methodology-v3.pdf` before quoting)

### Status
- **Generally available** per IBM newsroom.
- Service coverage: launched with **Cloud Object Storage, IBM Kubernetes Service, Virtual Server for VPC and Classic**; "more service coverage planned quarterly." No public per-service inventory of current coverage.
- API documented; output can be piped into the separately-licensed IBM Envizi ESG suite.

### Scope coverage
- **Scope 1**: included.
- **Scope 2**: LBM. MBM not surfaced.
- **Scope 3**: **excluded**.
- Embodied: **excluded** — "raw material and manufacturing of equipment, including servers, racks, and networking equipment, is out of scope."

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
