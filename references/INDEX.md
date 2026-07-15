# References Index

**This is a living file.** Update it whenever a source is added, removed, or renamed. Keep the layout map and the "Missing" list current; otherwise the source-grounding rule in `CLAUDE.md` cannot point to the right place.

This folder is the **source of truth** for any claim in `paper/paper.tex` that cites prior work, a provider methodology, or a standard.

**Hard rule (also in `CLAUDE.md`):** Before writing or repeating any claim about a cited document, open the file in this folder, find the supporting §/page, and cite it. Do not paraphrase from working notebooks or memory.
If the document is not in this folder, ask the user to add it — do not invent or guess.

**PDF access convention:** Every PDF in this folder has a sibling `.txt` produced by `pdftotext -layout`.
Always grep the `.txt` first (`grep -n <keyword> <file>.txt`), read a narrow window with `Read offset= limit=30`, and cite the §/page from the PDF.
Only open the PDF itself for figures or tables that survived poorly in the text extraction.
When adding a new PDF, immediately run: `pdftotext -layout <file>.pdf <file>.txt`

## Layout

```
references/
├── INDEX.md                            this file
├── terminology.md                      cross-source terminology drift (esp. "usage", embodied scope, SCI variants)
├── cross_provider_synthesis.md         Big-3 GHG-Protocol compliance + gold-standard scorecard + cross-cutting findings
├── SCI.md                              GSF SCI Specification v1.1 (markdown)
├── SCI_AI.md                           GSF SCI for AI extension (markdown)
├── SHARMA_2024_SHAPLEY.md              authoritative short summary of Sharma & Fuerst 2024 (Shapley attribution for FaaS)
├── BOAVIZTAPI_2024.md                  authoritative short summary of Simon et al. 2024 (BoaviztAPI bottom-up LCA)
├── CINERGY_2025.md                     authoritative short summary of Jacquet et al. 2025 (Cinergy deterministic VM power)
│
├── sources/                            academic priors + standards
│   ├── bashir-2024-sunk-carbon/        TeX source folder
│   │   ├── bashir-2024-sunk-carbon.tex   the paper source (grep-able; verify quotes here)
│   │   └── figures/
│   ├── greensku-isca-2024.pdf
│   ├── accountable-carbon-footprints-serverless.pdf
│   ├── boaviztapi-hotcarbon-2024.pdf
│   ├── cinergy-tcc-2025.pdf
│   ├── ghg-protocol-corporate-standard.pdf
│   ├── ghg-protocol-scope3-standard.pdf
│   └── ghg-protocol-scope2-guidance.pdf
│
└── carbon_accounting_methodologies/    one folder per provider
    ├── README.md                       provider matrix; links to each folder
    ├── non-customer-tool-providers.md  consolidated list of providers with no customer tool
    ├── aws/        (PDFs + README)
    ├── gcp/        (PDF + README)
    ├── azure/      (PDFs + README)
    ├── oracle/     (PDF + README)
    ├── ibm/        (PDF + README)
    ├── alibaba/    (web-only; README)
    ├── ovhcloud/   (PDFs + README)
    ├── scaleway/   (web-only; README)
    ├── t-cloud-public/  (web-only; README — formerly Open Telekom Cloud; per-customer dashboard launched 2026-02-23)
    ├── exoscale/   (web-only; README — folder retained, provider listed in `non-customer-tool-providers.md` since CloudAssess engine is third-party)
    ├── akamai/     (web-only; README)
    ├── cloudflare/ (PDF + README)
    └── fastly/     (web-only; README)
```

## Academic priors and standards — `sources/`

### Prior work
- `sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` — **Bashir et al. 2024** *"The Sunk Carbon Fallacy"* (arXiv:2410.15087). The central prior we extend. Defines oSCI / SCI / tSCI. **Both oSCI and tSCI avoid the sunk-carbon fallacy; only GSF-standard SCI exhibits it** (confirmed 2026-05-17 by reading §3 and §6 of the TeX source; tSCI formula is on line 374: `tSCI = (tO + tM) per R`). Cite §/line numbers from the TeX source for paper claims.
- `sources/greensku-isca-2024.pdf` — **GreenSKU (ISCA 2024)**. Microsoft research on hardware sustainability / SKU design for carbon reduction.
- `sources/accountable-carbon-footprints-serverless.pdf` — **Sharma & Fuerst 2024** *"Accountable Carbon Footprints and Energy Profiling For Serverless Functions"* (SoCC '24). Approximated-Shapley fair attribution for FaaS: three allocation rules (usage-proportional, frequency-proportional, even-share-among-active) for three classes of shared cost, with explicit "embodied as static sunk cost" framing that contrasts with SCI. The directly citable prior for rSCI's per-component residual-allocation schema (§4 surgery). See `SHARMA_2024_SHAPLEY.md` for the summary; cite §/eq from the PDF for paper claims. Bib key: `sharma2024accountable_footprint_serverless`.
- `sources/boaviztapi-hotcarbon-2024.pdf` — **Simon et al. 2024** *"BoaviztAPI: A Bottom-Up Model to Assess the Environmental Impacts of Cloud Services"* (HotCarbon '24). Open-source provider-agnostic bottom-up LCA toolkit; component-level embodied + usage modelling; multi-criteria (GWP, ADP, PE); their Table 1 independently corroborates our §3 provider-methodology critique. Falls under our §2 critique of bottom-up-only metrics — not reconcilable to top-down — but is the natural choice of bottom-up engine that feeds rSCI's $\varepsilon_p$. See `BOAVIZTAPI_2024.md` for the summary. Bib key: **TODO** (only a generic `boavizta-dc-lca` misc entry currently exists).
- `sources/cinergy-tcc-2025.pdf` — **Jacquet et al. 2025** *"Cinergy: Deterministic Power Monitoring for Carbon Accounting in the Cloud"* (IEEE TCC, extended from CCGrid 2025). Per-VM deterministic power model combining WCPC top-down with bottom-up RAPL profiling, validated with OVHcloud across 6 architectures (MAPE 6.6\%). **Headline finding: current carbon-accounting tools can underestimate operational CO2 by up to 3× for high-utilisation VMs (§V.C)** — a strong empirical hook for our §2 critique. The "Cinergy ratio" (per-cluster consolidation-gain correction) is conceptually adjacent to our $\mu_{s,r}$ Scope-2 multiplier. See `CINERGY_2025.md` for the summary. Bib key: **TODO** (not yet in bib).

### Fair-attribution priors (grouped cite in §4, `\parag{Relation to prior attribution work}`)

These fairly attribute a *bottom-up* energy/carbon quantity among co-tenants (cost-sharing / Shapley); rSCI's contrast is that it allocates the *residual* against the audited top-down total.

- `sources/fair-co2-isca-2025.pdf` — **Han, Kakadia, Lee, Gupta 2025** *"Fair-CO2: Fair Attribution for Cloud Carbon Emissions"* (ISCA '25). Shapley-value attribution of operational + embodied carbon to workloads; addresses Shapley scalability. Journal/ISCA successor to `han2024gametheoretic` (HotCarbon '24). Bib key: `han2025fairco2`.
- `sources/han-gametheoretic-carbon-2024.pdf` — **Han, Kakadia, Lee, Gupta 2024** *"Towards Game-Theoretic Approaches to Attributing Carbon in Cloud Data Centers"* (HotCarbon '24). Single-node Shapley model for fair attribution of operational + embodied carbon; the workshop precursor to `han2025fairco2` (Fair-CO2). Bib key: `han2024gametheoretic`.
- `sources/fair-carbon-disaggregation-carbonmetrics-2025.pdf` — **Sharma 2025** *"Fair Carbon Disaggregation and Scoped Attribution for Cloud Applications"* (CarbonMetrics '25, PER 53(2)). Two-axis framing (operational disaggregation × embodied locus-of-control) yielding a spectrum of metrics; Shapley as one point. Bib key: `sharma2025disaggregation`.
- `sources/fair-carbon-llm-serving-carbonmetrics-2025.pdf` — **Li, Han, Suh, Delimitrou, Kazhamiaka, Choukse, Fonseca 2025** *"Fair, Practical, and Efficient Carbon Accounting for LLM Serving"* (CarbonMetrics '25, PER 53(2)). Shapley as fairness ground truth for LLM-inference carbon attribution; notes attribution mismatch → over/under-reporting. Bib key: `li2025llmserving`.
- `sources/fairwatt-ict4s-2025.pdf` — **Montoya Franco, Muccini, van der Waaij 2025** *"FairWatt: An Energy Accounting System for Fair and Sustainable Data Centers"* (ICT4S '25, IEEE). Design-time fairness policies + runtime Shapley-based "Shared B" fairness score for multi-tenant *energy* allocation. Bib key: `montoyafranco2025fairwatt`.
- `sources/westerhof-allocation-model-2023.pdf` — **Westerhof, Atherton, Andrikopoulos 2023** *"An Allocation Model for Attributing Emissions in Multi-tenant Cloud Data Centers"* (arXiv:2305.10439). Allocation model for multi-tenant emissions attribution. Bib key: `westerhof2023allocation` (was in bib, previously uncited).

### Standards
- `sources/ghg-protocol-corporate-standard.pdf` — **GHG Protocol Corporate Standard** (revised).
- `sources/ghg-protocol-scope3-standard.pdf` — **GHG Protocol Corporate Value Chain (Scope 3) Standard**.
- `sources/ghg-protocol-scope2-guidance.pdf` — **GHG Protocol Scope 2 Guidance**. Defines LBM vs MBM.

### Markdown extracts (no PDF available)
- `SCI.md` — full GSF SCI Specification v1.1. Authoritative for what GSF SCI *is*.
- `SCI_AI.md` — GSF SCI-for-AI extension.

## Provider methodologies — `carbon_accounting_methodologies/`

See that folder's `README.md` for the provider matrix.
Each provider folder contains the methodology PDF(s) (where available) and a `README.md` consolidating URLs, methodology details, scope/embodied/allocation, assurance, and verification notes.

## Cross-provider synthesis — `cross_provider_synthesis.md`

Big-3 GHG-Protocol compliance posture, gold-standard scorecard, the three methodology families used in `paper/paper.tex` §3, and the eight cross-cutting findings that feed §3 and §6. This file holds what doesn't belong in any single per-provider README.

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
| ~~Microsoft 2021 Scope-3 Whitepaper~~ | ~~Microsoft~~ | **Resolved 2026-05-21**: added as `azure/microsoft-scope3-transparency-2021.{pdf,txt}`. Footnote 2, p. 2 (repeated as fn. 11, p. 10) verbatim: *"Microsoft Cloud is exploring new methods for emissions reporting that Microsoft has not yet adopted in its corporate disclosure. The underlying methodologies and emissions findings generated from the calculator will differ from those reflected in Microsoft's corporate disclosure."* `paper.tex:496–509` updated to quote this directly. |
| ~~Azure Emissions Calculation Methodology (Microsoft Learn page snapshot)~~ | ~~learn.microsoft.com~~ | **Resolved 2026-05-22**: compiled as `azure/azure-carbon-optimization-methodology-2026-05.md` — 4 pages crawled (Overview, View Emissions, Emissions Terminology, Power BI Methodology). No daily granularity; monthly ~19-day lag. Billing/emissions divergence verbatim confirmed. |
| ~~Oracle power-based calculation release note~~ | ~~docs.oracle.com~~ | **Resolved 2026-05-22**: compiled as `oracle/oracle-power-based-calc-releasenote-2025-06.md`. Page release date June 30, 2025 (not Feb 2026). LBM/MBM confirmed; zero-MBM in EU. Blog (blogs.oracle.com) returns 403. |
| **Scaleway per-product formulas** | scaleway.com | **Partially resolved 2026-05-22**: compiled as `scaleway/scaleway-methodology-docs-2026-05.md` from GitHub MDX source. Bare Metal, Instances, Block Storage formulas captured. **Daily granularity confirmed** — unusual among providers. |
| ~~Akamai May 2025 Cat-8 blog~~ | ~~akamai.com~~ | **Resolved 2026-05-22**: full content pasted by researcher into `akamai/akamai-carbon-calculator-blog-compilation-2026-05.md`. Allocation = byte + machine utilization; 5 emission factor types confirmed. Other blog URLs still 403. |
| ~~Akamai Emissions Reporting Policy PDF~~ | ~~~/Downloads/~~ | **Resolved 2026-05-22**: `akamai/akamai-emissions-reporting-policy-2025.pdf+txt`. Formal policy doc (Jan 2025, 7 pp.): non-disclosure of models confirmed §3.1; on-site audits forbidden §7.3; customer assurance customer-funded §2.1. Citable for replicability/assurance gaps. |
| **deloitte2024SEC_analysis** | Deloitte / SEC | **Cited in paper.tex lines 218, 269** but **missing from references.bib** — will cause LaTeX error. Likely a Deloitte analysis of the SEC Climate Disclosure Rule (finalized March 2024, subsequently stayed). User must supply the bib entry or replace the citation. |

## Verification protocol (mandatory before paper-level prose)

1. Identify the claim. ("Bashir says tSCI re-inherits the sunk-carbon bug.")
2. Open the relevant file in `references/` (`sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex` for the SCI-variant taxonomy and nuance). For provider methodology claims: `carbon_accounting_methodologies/<provider>/`.
3. Find the supporting passage. Cite §/page or §/line (e.g., "Bashir 2024 §3 line 374", "Schneider & Mattia 2024 §3.6").
4. If the supporting passage doesn't exist → the claim is wrong. Stop, ask the user, do not write it.
5. If the source isn't in `references/` → ask the user to add it. Do not paraphrase from memory or from notes.

This protocol overrides any contradicting summary in a working notebook — those are scratchpads, not authorities.
