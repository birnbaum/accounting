# Terminology drift across sources

**This is a living file.** Add a new row whenever a term-collision or version-drift is uncovered — e.g., a provider revises a methodology and redefines a term, or a paper's definition diverges from a standard's. Don't trust the table to be complete; trust the source-grounding rule in `CLAUDE.md`.

Same word, different meaning across providers / standards / paper versions.
When the paper writes one of these terms, the exact reading should be specified.
Each row's Source links to the file that defines the term, under `references/sources/` (standards + academic priors) or `references/carbon_accounting_methodologies/<provider>/` (provider methodology PDFs).

## SCI taxonomy (Bashir et al. 2024)

| Term | Definition | Source |
|---|---|---|
| **SCI** (GSF original) | `(E·I + M) / R` where `M` = embodied carbon of the *active server*, amortised. | `SCI.md` (GSF v1.1) |
| **oSCI** (Bashir) | `(E·I) / R` — operational only; embodied excluded entirely. | `sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` §3 |
| **tSCI** (Bashir) | `(tO + tM) / R` — distributes the **entire infrastructure's** operational + embodied carbon proportionally across jobs (not just the active server's share). | `sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` (tSCI formula on line 374) |
| **Sunk carbon fallacy** | Per-job scheduling decision biased toward older, less efficient hardware because their amortised embodied carbon is lower. **Applies to GSF SCI only**; oSCI and tSCI avoid it. | `sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` §3, §6 |
| **rSCI** (this paper) | Reconcilable SCI: extends the taxonomy with a residual term `Δ` that closes the bottom-up / top-down gap. | `README.md` and `paper/paper.tex` §4 (this paper's definition) |

**Action items:**
- *Do not* repeat the claim "tSCI re-inherits the sunk-carbon fallacy" — it is wrong: oSCI and tSCI both avoid it (`sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` §3, §6).
- Cite Bashir by §/line from `sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex`.

## "Usage" — provider-specific definitions

| Provider / period | What "usage" means | Source |
|---|---|---|
| AWS Model 3.0 (Oct 2025) | Instance-hours for foundational services; *equivalent revenue* for non-foundational services (a "standardized measure of usage-based revenue that excludes pricing variation factors such as discounts"). | `carbon_accounting_methodologies/aws/aws-ccft-methodology-model3.pdf` |
| GCP Carbon Footprint (Schneider & Mattia 2024) | vCPU-hours per SKU × *list-price-proportional* SKU factor. Commitment / sustained-use / committed-use discounts excluded from the SKU price. | `carbon_accounting_methodologies/gcp/schneider-mattia-2024-gcp.pdf` §3.6 |
| Azure 2021 Whitepaper | "Normalized cost metric associated with IaaS, PaaS or SaaS, normalized to exclude discounts and other variables." → closer to *economic* allocation. | `carbon_accounting_methodologies/azure/microsoft-cloud-carbon-study-2018.pdf` (2021 update) |
| Azure 2025 docs (Microsoft Learn, Jan 2026 snapshot) | "Compute, storage, data transfer time" → resource-time allocation. | Web (Microsoft Learn) — not yet in `references/` |
| OVHcloud EIT v2.0 | Smart-PDU electricity measurement where deployed; 100%/24×7 baseline otherwise. | `carbon_accounting_methodologies/ovhcloud/ovh-eit-methodology-v2-2025.pdf` |

**Action item:** when the paper says "AWS uses usage allocation," disambiguate: foundational (physical-ish) or non-foundational (revenue-based). The cells in Table 1 already do this; prose must match.

## "Embodied carbon" — scope differences

| Source | Boundary | Lifetime | Buildings | End-of-life |
|---|---|---|---|---|
| AWS Model 3.0 | Cradle-to-gate; 4-pathway waterfall (PLCA→ML-extrap→RCA-LCA→EIO-LCA) | 6 yr IT, 50 yr buildings | Included (since Oct 2025) | Excluded |
| GCP Carbon Footprint | Cradle-to-gate; component LCA | **4 yr IT** (acknowledged shorter than actual) | Included | Excluded |
| Azure (CHEM) | Cradle-to-grave (incl. EoL); process-based LCA via Makersite + imec SSTS + ecoinvent | 6 yr IT | **Excluded** (building shell out) | Included |
| OVHcloud EIT v2.0 | Component-level LCA with published per-component factors | 5 yr | Included | Refurbishment netted per-range |
| Scaleway | Boavizta LCA models | n/a per docs; check `carbon_accounting_methodologies/scaleway/` if needed | Included | n/a |
| Fastly | n/a — **embodied carbon explicitly excluded** | n/a | n/a | n/a |
| IBM | n/a — **raw-material + manufacturing explicitly excluded** per v3 | n/a | n/a | n/a |
| Bashir SCI taxonomy | The `M` term in standard SCI = amortised embodied of the *active server* | flat-line amortisation | n/a | n/a |

**Action item:** never write "Big-3 include embodied carbon" without flagging the lifetime + buildings + EoL differences.

## "Foundational vs non-foundational" (AWS-specific)

- Defined in `carbon_accounting_methodologies/aws/aws-ccft-methodology-model3.pdf` (Model 3.0 methodology document, Oct 2025).
- **Foundational service**: "AWS service that has dedicated server racks in AWS data centers." Allocation = instance-hours.
- **Non-foundational service**: "AWS service with no dedicated server racks, which relies on foundational services to provide functionality to end customers." Allocation = equivalent revenue.
- **The published list of which services fall into each tier is not in the methodology document.** EC2, S3, EBS, Lambda, SageMaker are named in the doc but not explicitly classified. This is the largest opacity in CCFT.

## Scope 2 LBM vs MBM

| Term | Definition | Defined in |
|---|---|---|
| **Location-based method (LBM)** | Emissions based on the average emissions intensity of the grid where the consumption occurs. | `sources/ghg-protocol-scope2-guidance.pdf` |
| **Market-based method (MBM)** | Emissions based on contractual instruments (RECs/EACs/PPAs) the consumer purchased; can be 0 even on a non-renewable grid. | `sources/ghg-protocol-scope2-guidance.pdf` |
| **Effective**: Azure exports | Both documented; **only MBM in actual exports** (LBM ≈ 0 in CCFT data). Confirmed empirically. | Frankfurt case study notes |
| **Effective**: Oracle EU regions | MBM = 0 by Oracle PPA design. | `carbon_accounting_methodologies/oracle/oracle-technical-carbon-guidance.pdf` |

## Scope 3 categories — full names per GHG Protocol

Naming is sometimes loose. Canonical names (from `sources/ghg-protocol-scope3-standard.pdf`):

| # | Canonical name | Common short form |
|---|---|---|
| 1 | Purchased goods and services | "purchased goods" |
| 2 | Capital goods | "capital goods" / "IT hardware" (cloud usage) |
| 3 | Fuel- and energy-related activities not included in Scope 1 or 2 | **FERA** (the term cloud-methodology docs use), or "WTT + T&D" |
| 4 | Upstream transportation and distribution | "upstream transport" |
| 5 | Waste generated in operations | "waste" |
| 6 | Business travel | — |
| 7 | Employee commuting | — |
| 8 | Upstream leased assets | Akamai uses this for *customer's* allocation |
| 9 | Downstream transportation and distribution | "downstream transport" |
| 12 | End-of-life treatment of sold products | "end-of-life", "EoL" |

## Facility metrics

| Term | Definition | Source |
|---|---|---|
| **PUE** (Power Usage Effectiveness) | Total facility power ÷ IT equipment power. | Generic / Uptime Institute |
| **WUE** (Water Usage Effectiveness) | L of water per kWh of IT energy. | Generic |
| **CFE %** (Carbon-Free Energy percentage) | % of hourly energy consumption matched to carbon-free sources on the same grid. | Google sustainability docs |
| **CUE** (Carbon Usage Effectiveness) | kgCO₂e per kWh of IT energy. | Generic |
| **ERE / ERF** (Energy Reuse Effectiveness / Factor) | Recovered energy ÷ total energy. | Generic |

## "Reconciliation" — be careful

- **Provider-internal reconciliation**: matching internal Borg/utilisation telemetry to the customer-facing dashboard. GCP does this stage but distorts at the SKU step (price-proportional).
- **Customer-tool / corporate-disclosure reconciliation**: do the customer-allocated numbers sum to the provider's corporate Scope 1/2/3 disclosure? Microsoft explicitly says no (Scope-3 Whitepaper footnote 2).
- **rSCI reconciliation (this paper)**: bottom-up SCI per workload reconciles with the top-down provider report via residuals.

The three meanings collide constantly. Specify which when writing.
