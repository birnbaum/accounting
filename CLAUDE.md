# CLAUDE.md

## Project

Research framework for reconciling bottom-up software carbon intensity (SCI) metrics with top-down provider-reported GHG numbers. Academic/research context — not production software. The output is a SoCC vision-track paper (6 pages) in `paper/`.

## Source-grounding rule (non-negotiable)

Before writing or repeating **any claim about prior work, a provider methodology, or a standard**:

1. Open the relevant file in `references/`. Start with the README inside the appropriate subfolder. For taxonomy / metric claims: `references/SCI_SUNK_CARBON.md` and `references/SCI.md`. For provider claims: `references/carbon_accounting_methodologies/<provider>/`.
2. Find the supporting §/page in the primary source (PDF or `references/` markdown).
3. Cite the §/page in the paper (e.g., "Bashir 2024 §3", "Schneider & Mattia 2024 §3.6", "AWS Model 3.0 methodology §X").
4. **If the source does not exist in `references/`, ask the user to add it. Do not paraphrase from memory, from `vision_paper_notes.md`, or from any `CLOUD_CARBON_ACCOUNTING_*.md` working doc.**
5. **If a claim cannot be supported by an open primary source, do not write it.** Surface the conflict to the user.

`vision_paper_notes.md` and the `CLOUD_CARBON_ACCOUNTING_*.md` files are **working notebooks and inventories**, not authoritative for claims. Treat them as scratchpads.

This rule overrides convenience. Always open the source.

## Where to find things

### Authoritative for prior work and standards
- `references/INDEX.md` — top-level index. Read this first when entering the project.
- `references/SCI.md`, `references/SCI_AI.md`, `references/SCI_SUNK_CARBON.md` — GSF SCI spec, AI extension, Bashir summary.
- `references/pdfs/` — academic priors (Bashir, GreenSKU) and GHG Protocol standards.
- `references/terminology.md` — terminology drift across sources (esp. "usage", embodied scope, SCI variants, S1/2/3, FERA, LBM/MBM).

### Authoritative for provider methodologies
- `references/carbon_accounting_methodologies/<provider>/README.md` — per-provider consolidated methodology summary, plus any PDFs in the same folder.
- `references/carbon_accounting_methodologies/README.md` — provider matrix.
- `references/carbon_accounting_methodologies/tier-b-c-providers.md` — providers without customer tools.

### Paper artifacts
- `paper/paper.tex` — the SoCC vision-track paper draft.
- `paper/references.bib` — bib entries.
- `paper/figures/` — figures.

### Working notebooks (NOT authoritative for claims)
- `README.md` — core framework definition (rSCI). Living research document.
- `vision_paper_notes.md` — paper outline + working notes. May contain inaccuracies; verify against `references/` before using.
- `HYPERSCALER_CARBON_ACCOUNTING.md`, `CLOUD_CARBON_ACCOUNTING_DEEPDIVE.md` — working inventories used for the original §3 build. Useful for cross-checking but not citable.
- `SCHEMA.md` — provider profile schema.

### Data
- `gcp/` — GCP benchmark experiments.
- `azure/` — Azure carbon export data and analysis (incl. the Frankfurt case study).
- `aws/` — AWS data.

## README.md style

The README is a living research document. Keep it concise:
- **Intro section** can be expository — collaborators need to understand the problem and motivation.
- **Everything after** is definitions, math, and brief context. Say it once, reference it later.

## General style

- Be concise. Prefer precision over prose.
- **One sentence per line** in all markdown files. Always newline after each sentence.
- Don't add docstrings, comments, or type annotations to code that wasn't changed.
- Research repo — scripts are exploratory, not production code.

## When in doubt

Ask the user. Surfacing uncertainty is always cheaper than writing something wrong into the paper. A passing self-check is not evidence the claim is right — it's only evidence your self-check didn't catch the bug.
