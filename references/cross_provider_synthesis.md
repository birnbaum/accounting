# Cross-provider synthesis (Big-3 focus)

Per-provider details live in `carbon_accounting_methodologies/<provider>/README.md`.
This file holds cross-provider observations that don't fit neatly into one provider's folder — GHG-Protocol compliance posture, gold-standard scoring, and the takeaway findings used in `paper/paper.tex` §3 and §6.

**This is a living file.** Update as you go.

## GHG Protocol compliance — areas of clear divergence

| Issue | Provider(s) | GHG Protocol requirement | Practice | Severity |
|---|---|---|---|---|
| Allocation parameters undisclosed | AWS, Azure | Physical allocation preferred; parameters verifiable | AWS: non-foundational economic; Azure: usage-factor parameters undisclosed | Medium |
| Historical recasting window | Azure | Recast base year on methodology change | 12-month window only | High |
| Scope-3 material categories excluded | All | Include all material categories | Significant gaps (see per-provider) | High |
| Materiality assessment for exclusions | All | Justify exclusions with materiality assessment | None published | Medium |

## Where GHG Protocol is under-specified for cloud

The most consequential differences arise from areas the standard does not address:

| Area | AWS | GCP | Azure |
|---|---|---|---|
| Allocation of shared cloud infrastructure | Usage (foundational) + economic fallback (non-foundational) | Physical internally; usage at customer boundary (vCPU-h × price factor); proportional ratio for non-electricity S3 | "Normalized cost metric" (2021) / "compute-storage-data-transfer time" (2025/26); undisclosed |
| Equipment lifetime | 6 yr IT, 50 yr buildings | 4 yr IT, buildings included | 6 yr IT, buildings excluded |
| EAC/PPA temporal matching | Not disclosed (assumed annual) | Hourly CFE reported | Not disclosed (assumed annual) |
| Building embodied carbon | Included (Model 3.0.1) | Included | Excluded |
| End-of-life hardware | Excluded | Excluded | Included |
| Business travel + commuting | Excluded | Included | Excluded |
| Idle-capacity allocation | Not disclosed | Proportionally allocated | Not disclosed |

These are interpretive divergences, not violations. A gold standard for cloud carbon accounting must resolve them.

## Gold-standard scorecard

Status: **Full** / **Partial** / **Not Met** / **Unclear**.

| Requirement | AWS | GCP | Azure |
|---|---|---|---|
| **Scope 1** | | | |
| Stationary combustion + fugitives | Full | Full | Full |
| Physical allocation to customers | Partial | Partial | Not Met |
| Independent S1 verification | Not Met | Not Met | Not Met |
| **Scope 2** | | | |
| Both LBM + MBM | Full | Full | Full |
| Granular (sub-annual) grid factors | Partial | Full | Partial |
| EAC/PPA temporal matching disclosed | Unclear | Partial | Unclear |
| Location-matched EACs/PPAs | Unclear | Partial | Unclear |
| **Scope 3 — Cat 2 capital goods** | | | |
| IT hardware embodied | Full | Full | Full |
| Building embodied | Full | Full | Not Met |
| Non-IT infrastructure | Full | Partial | Not Met |
| Cradle-to-grave (incl. EoL) | Not Met | Not Met | Full |
| Lifetime disclosed | Full | Partial | Partial |
| **Scope 3 — others** | | | |
| Cat 3 FERA | Full | Full | Not Met |
| Cat 4 upstream transport | Full | Partial | Full |
| Cat 5 waste | Not Met | Not Met | Full |
| Cat 6/7 business travel + commuting | Not Met | Full | Not Met |
| Cat 9 downstream transport | Not Met | Not Met | Full |
| Cat 12 end-of-life | Not Met | Not Met | Full |
| **Allocation** | | | |
| Physical allocation as primary | Partial | Partial | Partial |
| Methodology + parameters disclosed | Partial | Full | Partial |
| Economic-allocation services disclosed | Not Met | Partial | N/A |
| **Reporting** | | | |
| ≤1-month lag | Full | Full | Full |
| Full historical recasting | Full | Full | Partial |
| Retention ≥3 yr | Full | Full | Partial |
| Programmatic API | Full (since 31 Mar 2026 Sustainability Console) | Full (BigQuery) | Full (REST/Fabric/Power BI) |
| **Verification** | | | |
| Third-party assurance | Partial (limited) | Not Met | Partial |
| Standard + level disclosed | Full | Partial | Partial |
| Tool implementation verified | Not Met | Not Met | Not Met |
| **Transparency** | | | |
| Full methodology published | Partial | Full | Partial |
| Materiality assessment for exclusions | Not Met | Not Met | Not Met |
| Reconcile customer tool ↔ corporate disclosure | Not Met | Partial | Not Met |

## Cross-cutting findings (these feed the paper)

1. **No provider achieves comprehensive GHG-Protocol compliance.** Each has significant Scope-3 gaps and none verifies its tool implementation. Gap patterns differ: AWS allocation opacity (undisclosed non-foundational list); GCP scope gaps (no EoL, hourly-internal-only, 4-yr lifetime); Azure methodology opacity (undisclosed allocation parameters, 12-month recast, FERA and buildings excluded).
2. **GHG Protocol is under-specified for cloud.** Differences in allocation, lifetimes, building embodied, EAC matching are interpretive divergences arising from gaps in the standard.
3. **Verification claims are narrower than they look.** Apex (AWS) covers Model 3.0.x methodology Scope-3 Cat 2/3/4 at limited assurance; WSP (Azure) covers Scope-3 doc only; Fraunhofer (GCP) covers LCA methodology only. No Big-3 has its customer tool end-to-end audited.
4. **All three use usage allocation at the customer level.** GCP measures power physically internally but the customer-facing step distributes by price-proportional SKU factors × vCPU-hours. AWS foundational uses instance-hours; Azure uses a per-region usage factor. None reflects compute utilization at the customer surface.
5. **All three zero out embodied past the amortisation window** (AWS/Azure 6 yr, GCP 4 yr). Fleet-wide monthly Scope 3 mechanically decreases as equipment ages — independent of actual environmental impact.
6. **GCP is the most transparent and granular** Big-3 methodology: internal machine-level power telemetry, hourly Electricity Maps for Scope 2, peer-reviewed methodology (Schneider & Mattia 2024), buildings in customer tool. Customer-facing allocation is still usage-based (price-proportional × resource-time) — a shared limitation.
7. **Azure has the broadest Scope-3 count** (6 categories: Cat 1, 2 IT-only, 4, 5, 9, 12) but **excludes FERA and building embodied**. Uniquely includes Cat 12 end-of-life. As of Jan 2026 data (released Feb 2026), GCP additionally attributes AI-inference emissions at SKU level (Vertex AI, Cloud Natural Language, Speech APIs, Dialogflow).
8. **Compute utilization is invisible to all three customer methodologies.** Idle and fully-loaded VMs/GPUs report the same carbon for the same duration × SKU. Only reducing resource-time moves the reported number. This is the practical bound on what carbon-aware computing can change in the *reported* footprint.

## Tier-A non-Big-3 cross-cutting

For completeness — when contrasted against Big-3:

- **Akamai, OVHcloud** use real-DC-utilization allocation (the closest to physical among Tier-A).
- **OVHcloud** uniquely uses a **100%/24×7 baseline** until Smart-PDU rollout completes — customer numbers are *over-estimates*, the opposite bias of the Big-3.
- **Scaleway, OVHcloud** are the only Tier-A providers with component-level published LCA factors (Boavizta / IJO).
- **Cloudflare, Fastly** allocate by bytes/CPU-time — fundamentally different unit from the Big-3.
- **Alibaba** is the only Tier-A provider with third-party *data* assurance (Bureau Veritas under ISO 14064-3); all others have at most methodology-level assurance.
- **None** of the Tier-A providers reflects compute utilization in the customer-reported number.

## Three methodology families (used in `paper/paper.tex` §3)

The Tier-A landscape splits into three families that don't produce comparable numbers without an explicit residual bridge:

1. **Usage-time allocated** — AWS, GCP, Azure, Oracle, IBM, Alibaba. Carbon proportional to rental-line: vCPU-hours or instance-hours of an SKU, possibly re-weighted by list price (GCP), revenue (AWS non-foundational), or "normalized cost" (Azure). Embodied carbon folded into the per-SKU factor.
2. **Traffic-allocated** — Akamai, Cloudflare, Fastly. Carbon proportional to work-volume: bytes delivered or CPU-time consumed. Embodied carbon largely or entirely excluded.
3. **Component-LCA per resource** — OVHcloud, Scaleway. Carbon built from a physical inventory: per-component embodied factor + operational energy.

The three families allocate different slices of provider emissions in different units; adding or directly benchmarking across them is not meaningful without an explicit residual bridge — this is the rSCI gap.
