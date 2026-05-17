# GCP Carbon Accounting

**Customer tool:** Google Cloud Carbon Footprint (console + BigQuery export).

## Authoritative sources in this folder

- `schneider-mattia-2024-gcp.pdf` — Schneider & Mattia 2024 (arXiv:2406.09645). The peer-reviewed write-up of GCP's customer-facing methodology by Google authors. **This is the canonical reference for any GCP claim.**

## Provider URLs (for fresh verification)

- Product page: https://cloud.google.com/carbon-footprint
- Methodology docs: https://docs.cloud.google.com/carbon-footprint/docs/methodology
- Covered services: https://docs.cloud.google.com/carbon-footprint/docs/covered-services
- View data: https://docs.cloud.google.com/carbon-footprint/docs/view-carbon-data
- Release notes: https://docs.cloud.google.com/carbon-footprint/docs/release-notes
- Per-region carbon-free energy %: https://cloud.google.com/sustainability/region-carbon
- Architecture-framework sustainability section: https://docs.cloud.google.com/architecture/framework/sustainability/continuously-measure-improve

## Methodology summary (verify against `schneider-mattia-2024-gcp.pdf` before quoting)

### Surface
- Console + **BigQuery export API**.
- Unlimited retention; ~15-day lag; monthly granularity at the customer surface.
- Methodology docs last updated **2026-05-15** (verified WebFetch).
- Per-region hourly **Carbon-Free Energy (CFE) percentage** is the only sub-monthly carbon signal any Big-3 publishes — but it is *separate* from the customer-allocated number.

### Scope coverage
- **Scope 1**: included.
- **Scope 2**: LBM + MBM. Internal granularity hourly; customer granularity monthly.
- **Scope 3**: Cat 2 (capital goods, **including buildings**), Cat 3 (FERA), Cat 6 (business travel), Cat 7 (employee commuting).
- **Excluded**: Cat 5 (waste), Cat 9, Cat 12 end-of-life. End-of-life explicitly excluded.

### Service coverage
- **100+ services** covered. Compute Engine, App Engine, Cloud Run, GKE, Cloud TPU, BigQuery, Dataflow, Dataproc, Composer, AlloyDB, Cloud SQL, Spanner, Bigtable, Vertex AI, Gemini API, Cloud ML Engine, Cloud Storage, Filestore, Cloud DNS, Firebase, Pub/Sub, Logging, Secret Manager, and others.
- **Explicit exclusions**: Apigee, AppSheet, Google Security Operations, Looker. "Any services not listed are not covered by Carbon Footprint."
- AI-inference emissions attributed directly to associated services (Vertex AI, Cloud Natural Language, Speech APIs, Dialogflow, $\ldots$) at the SKU level.

### Embodied carbon (Cat 2)
- Component-level LCA; Fraunhofer IZM critical review (ISO 14040/44).
- Lifetime: **4 yr IT** (financial-accounting depreciation). Google acknowledges real lifetimes are longer; the customer number therefore over-allocates annual amortised embodied carbon vs AWS/Azure's 6 yr.
- Buildings included in customer tool.
- Zero past-amortisation.

### Allocation (two-stage)
- **Stage 1 — internal, physical**: machine-level power monitoring via Borg telemetry. Dynamic power (workload-driven) is allocated proportional to **GCU** (Google Compute Unit) usage; idle power (~60% of average server energy) is allocated by resource-weighted shares of GCU/RAM/etc.
- **Stage 1.5 — cost-based fallback for shared services**: where shared internal services (e.g., Cloud Storage built on Blobstore/Colossus) lack sufficient usage data, GCP reallocates energy by back-charged internal costs. Affected service set + emission fraction **not disclosed**.
- **Stage 2 — customer-facing, price-proportional**: each internal team's energy is distributed across customer-facing SKUs by a formula in which energy per usage unit is **proportional to list price** (commitment-, committed-use-, and sustained-use-discounts excluded). Customers are then allocated by usage units (vCPU-hours for Compute Engine, GiB-months for storage, etc.).
- **Schneider & Mattia §3.6** explicitly notes: *"One limitation of this approach is that customers do not receive a signal about how switching from SKU A to SKU B can reduce their actual emissions, but rather their allocated emissions based on list prices."*
- **Non-electricity Scope 3** (embodied, FERA, transport): allocated by proportional ratio `(customer electricity) / (total GCP electricity)`. Assumes non-electricity emissions track electricity, which doesn't hold across CPU vs GPU workload mixes.

### Assurance
- **Fraunhofer IZM critical review (ISO 14040/14044)** of LCA methodology only.
- **No formal ISO 14064-3 GHG assurance** of the tool.
- Tool implementation not audited.

### Strengths and weaknesses for rSCI
- **Strength**: only Big-3 with published machine-level internal telemetry; only Big-3 with peer-reviewed methodology; only Big-3 to expose hourly CFE %.
- **Weakness**: customer-surface allocation does *not* reflect actual compute utilization. Price-proportional SKU step decouples customer signal from physical measurement. Non-electricity-S3 proportional-ratio assumption is fragile across heterogeneous workloads.

## Recent verification (2026-05-16)

- 100+ services confirmed via covered-services docs page.
- 4 explicit exclusions: Apigee, AppSheet, SecOps, Looker.
- Last update on methodology page: 2026-05-15.
