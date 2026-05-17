# Carbon Accounting Methodologies — per-provider folders

Each subdirectory is the authoritative reference for one cloud provider's customer-facing carbon-accounting tool. Each folder contains the provider's methodology PDF(s) (where available) and a `README.md` consolidating URLs, methodology details, scope/embodied/allocation choices, assurance posture, and recent verification notes.

## Tier-A providers (per-customer dashboard exists) — 11 first-party tools

| Provider | Folder | Primary methodology source |
|---|---|---|
| AWS | `aws/` | `aws-ccft-methodology-model3.pdf` (Oct 2025) |
| GCP | `gcp/` | `schneider-mattia-2024-gcp.pdf` (arXiv:2406.09645, peer-reviewed) |
| Azure | `azure/` | `azure-chem-2026.pdf` + Microsoft Learn (web, snapshot pending) |
| Oracle (OCI) | `oracle/` | `oracle-technical-carbon-guidance.pdf` |
| IBM Cloud | `ibm/` | `ibm-carbon-calc-methodology-v3.pdf` |
| Alibaba Cloud | `alibaba/` | web-only — see folder README |
| OVHcloud | `ovhcloud/` | `ovh-eit-methodology-v2-2025.pdf` + v1 |
| Scaleway | `scaleway/` | web-only (per-product pages) — see folder README |
| Akamai | `akamai/` | web-only — see folder README |
| Cloudflare | `cloudflare/` | `cloudflare-impact-report-2023.pdf` + methodology blog |
| Fastly | `fastly/` | web-only (methodology docs page) — see folder README |

## Borderline: Exoscale

| Provider | Folder | Notes |
|---|---|---|
| Exoscale | `exoscale/` | Calculator is third-party (CloudAssess by Resilio/Kleis); engine methodology partner-owned and not fully public. Excluded from the paper's main Tier-A table for this reason. |

## Excluded: Huawei Cloud (Huella Cloud)

Verified 2026-05-16: vendor is **SGS Solutions** (Chile), multi-cloud. Not a first-party Huawei product. Not added as a folder; mentioned only as a footnote in `paper/paper.tex` §3.

## Tier-B / Tier-C providers — no per-customer tools

See `tier-b-c-providers.md` (in this folder) for the consolidated list (corporate-disclosure-only and marketing-claim providers).

## Verification protocol (also in `../INDEX.md`)

Before quoting any provider methodology claim in the paper:
1. Open the relevant folder's PDF (or its `README.md` if no PDF exists).
2. Cite the §/page that supports the claim.
3. If the source doesn't support the claim, the claim is wrong — stop, ask the user, do not write it.
4. If the source isn't in the folder, ask the user to add it. Do not paraphrase from notes.

This overrides any contradicting summary in `vision_paper_notes.md`.
