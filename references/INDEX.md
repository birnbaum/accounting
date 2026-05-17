# References Index

This folder is the **source of truth** for any claim in `paper/paper.tex` that cites prior work, a provider methodology, or a standard.

**Hard rule (also in `CLAUDE.md`):** Before writing or repeating any claim about a cited document, open the file in this folder, find the supporting §/page, and cite it. Do not paraphrase from `vision_paper_notes.md`, the `CLOUD_CARBON_ACCOUNTING_DEEPDIVE.md` working doc, or memory.
If the document is not in this folder, ask the user to add it — do not invent or guess.

## Layout

```
references/
├── INDEX.md                            this file
├── terminology.md                      cross-source terminology drift (esp. "usage", embodied scope, SCI variants)
├── SCI.md                              GSF SCI Specification v1.1 (markdown)
├── SCI_AI.md                           GSF SCI for AI extension (markdown)
├── SCI_SUNK_CARBON.md                  authoritative short summary of Bashir et al. 2024
│
├── pdfs/                               academic priors + standards
│   ├── bashir-2024-sunk-carbon.pdf
│   ├── greensku-isca-2024.pdf
│   ├── ghg-protocol-corporate-standard.pdf
│   ├── ghg-protocol-scope3-standard.pdf
│   └── ghg-protocol-scope2-guidance.pdf
│
└── carbon_accounting_methodologies/    one folder per provider
    ├── README.md                       provider matrix; links to each folder
    ├── tier-b-c-providers.md           consolidated list of providers with no customer tool
    ├── aws/        (PDFs + README)
    ├── gcp/        (PDF + README)
    ├── azure/      (PDFs + README)
    ├── oracle/     (PDF + README)
    ├── ibm/        (PDF + README)
    ├── alibaba/    (web-only; README)
    ├── ovhcloud/   (PDFs + README)
    ├── scaleway/   (web-only; README)
    ├── exoscale/   (web-only; README — borderline)
    ├── akamai/     (web-only; README)
    ├── cloudflare/ (PDF + README)
    └── fastly/     (web-only; README)
```

## Academic priors and standards — `pdfs/`

### Prior work
- `bashir-2024-sunk-carbon.pdf` — **Bashir et al. 2024** *"The Sunk Carbon Fallacy"* (arXiv:2410.15087). The central prior we extend. Defines oSCI / SCI / tSCI. **Both oSCI and tSCI avoid the sunk-carbon fallacy; only GSF-standard SCI exhibits it.** See `SCI_SUNK_CARBON.md` for the corrected taxonomy summary.
- `greensku-isca-2024.pdf` — **GreenSKU (ISCA 2024)**. Microsoft research on hardware sustainability / SKU design for carbon reduction.

### Standards
- `ghg-protocol-corporate-standard.pdf` — **GHG Protocol Corporate Standard** (revised).
- `ghg-protocol-scope3-standard.pdf` — **GHG Protocol Corporate Value Chain (Scope 3) Standard**.
- `ghg-protocol-scope2-guidance.pdf` — **GHG Protocol Scope 2 Guidance**. Defines LBM vs MBM.

### Markdown extracts (no PDF available)
- `SCI.md` — full GSF SCI Specification v1.1. Authoritative for what GSF SCI *is*.
- `SCI_AI.md` — GSF SCI-for-AI extension.
- `SCI_SUNK_CARBON.md` — short summary of Bashir et al. 2024 with the **correct** taxonomy.

## Provider methodologies — `carbon_accounting_methodologies/`

See that folder's `README.md` for the provider matrix.
Each provider folder contains the methodology PDF(s) (where available) and a `README.md` consolidating URLs, methodology details, scope/embodied/allocation, assurance, and verification notes.

## Missing — please add manually

Web-only or paywalled — must be acquired by the user and dropped in:

| File | Source | Notes |
|---|---|---|
| **ISO/IEC 21031:2024** | iso.org (~CHF 150) | Codified GSF SCI standard. `SCI.md` is the GSF v1.1 public version. |
| **Basu Roy et al. 2024** *"Hidden Carbon Footprint of Serverless"* | SoCC 2024 / ACM DL | Cited for §7 multi-tenant / serverless discussion. |
| **Acun et al. 2023** *"Carbon Explorer"* | HPCA 2023 / IEEE | Meta carbon-footprint paper. |
| **Radovanović et al.** | IEEE | Google carbon-aware compute scheduling. |
| **Wiesner et al.** (Cucumber, *Let's Wait Awhile*, …) | Author's own | Self-citation for §6 / §7 prior-art coverage. |
| **Lin et al.** | TBD by author | Specific carbon-aware paper to cite. |
| **Microsoft 2021 Scope 3 Whitepaper** (with footnote 2) | Microsoft | Verify whether this is a separate doc from `microsoft-cloud-carbon-study-2018.pdf` 2021 update, or the same. The famous footnote-2 non-reconciliation passage lives in this update. |
| **Azure Emissions Calculation Methodology (Microsoft Learn page snapshot)** | learn.microsoft.com | Currently web-only. Print-to-PDF as `azure/azure-methodology-2026-01-snapshot.pdf` for a citable artifact. |

## Verification protocol (mandatory before paper-level prose)

1. Identify the claim. ("Bashir says tSCI re-inherits the sunk-carbon bug.")
2. Open the relevant file in `references/` (`SCI_SUNK_CARBON.md` first for the taxonomy, then `pdfs/bashir-2024-sunk-carbon.pdf` for nuance). For provider methodology claims: `carbon_accounting_methodologies/<provider>/`.
3. Find the supporting passage. Cite §/page (e.g., "Bashir 2024 §3 p.5", "Schneider & Mattia 2024 §3.6").
4. If the supporting passage doesn't exist → the claim is wrong. Stop, ask the user, do not write it.
5. If the source isn't in `references/` → ask the user to add it. Do not paraphrase from memory or from notes.

This protocol overrides any contradicting summary in `vision_paper_notes.md` or in `CLOUD_CARBON_ACCOUNTING_DEEPDIVE.md`/`HYPERSCALER_CARBON_ACCOUNTING.md` — those are inventories, not authorities.
