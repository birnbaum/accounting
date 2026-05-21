# CLAUDE.md

## Project

Research framework for reconciling bottom-up software carbon intensity (SCI) metrics with top-down provider-reported GHG numbers. Academic/research context — not production software. The output is a SoCC vision-track paper (6 pages) in `paper/`.

## Source-grounding rule (non-negotiable)

Before writing or repeating **any claim about prior work, a provider methodology, or a standard**:

1. Open the relevant file in `references/`. Start with the README inside the appropriate subfolder. For taxonomy / metric claims: `references/SCI_SUNK_CARBON.md` and `references/SCI.md`. For provider claims: `references/carbon_accounting_methodologies/<provider>/`.
2. **Grep the `.txt` companion** of the relevant PDF (every PDF in `references/` has a sibling `.txt` produced by `pdftotext -layout`). Use `grep -n` to find the line, then `Read offset=… limit=30` for a narrow window. Only open the PDF itself for figures or tables that the text extraction missed.
3. Find the supporting §/page. Page numbers are preserved in the `.txt` output.
4. Cite the §/page in the paper (e.g., "Bashir 2024 §3", "Schneider & Mattia 2024 §3.6", "AWS Model 3.0 methodology §X").
5. **If the source does not exist in `references/`, ask the user to add it. Do not paraphrase from memory or from any `CLOUD_CARBON_ACCOUNTING_*.md` working doc.**
6. **If a claim cannot be supported by an open primary source, do not write it.** Surface the conflict to the user.

Use `/verify-claim <claim>` to run this workflow as a structured slash command.

The `CLOUD_CARBON_ACCOUNTING_*.md` files are **working notebooks and inventories**, not authoritative for claims. Treat them as scratchpads.

This rule overrides convenience. Always open the source.

## Living files (update as you go)

The following are **living files** — update them whenever new information is verified, a new source is added, or terminology drift is uncovered. Don't let them get stale:

- `references/INDEX.md` — when a PDF or per-provider folder is added/removed/renamed, update the layout map and the "Missing" list.
- `references/terminology.md` — when a new term-collision or version-drift is uncovered (e.g., Azure's "usage" definition changing between 2021/2025/2026 docs), add a new row with the citation.
- `references/carbon_accounting_methodologies/<provider>/README.md` — when a provider ships a methodology revision (e.g., AWS Model 3.0 → 3.0.1, GCP AI-inference allocation update, Oracle Feb-2026 power-based standardization), update the relevant per-provider README before the change leaks into `paper/paper.tex`.

A useful habit: every time you verify a new fact for the paper, ask "should this also land in `terminology.md` or a provider README?" If yes, do it in the same turn.

## Where to find things

### Authoritative for prior work and standards
- `references/INDEX.md` — top-level index. Read this first when entering the project.
- `references/SCI.md`, `references/SCI_AI.md`, `references/SCI_SUNK_CARBON.md` — GSF SCI spec, AI extension, Bashir summary.
- `references/sources/` — academic priors (Bashir TeX sources, GreenSKU) and GHG Protocol standards.
- `references/terminology.md` — terminology drift across sources (esp. "usage", embodied scope, SCI variants, S1/2/3, FERA, LBM/MBM).
- `references/cross_provider_synthesis.md` — Big-3 GHG-Protocol compliance posture, gold-standard scorecard, cross-cutting findings, and the three methodology families used in `paper/paper.tex` §3.

### Authoritative for provider methodologies
- `references/carbon_accounting_methodologies/<provider>/README.md` — per-provider consolidated methodology summary, plus any PDFs in the same folder.
- `references/carbon_accounting_methodologies/README.md` — provider matrix.
- `references/carbon_accounting_methodologies/tier-b-c-providers.md` — providers without customer tools.

### Paper artifacts
- `paper/SECTIONS.md` — **read this first**: maps each §, its line range in `paper.tex`, and its key references. Read the narrow line range rather than the full file.
- `paper/paper.tex` — the SoCC vision-track paper draft (976 lines, 8 sections).
- `paper/references.bib` — bib entries.
- `paper/figures/` — figures.

### Working notebooks (NOT authoritative for claims)
- `README.md` — core framework definition (rSCI). Living research document.
- `paper/experiments_design.md` — §4 toy-cloud experiment design notes for the SoCC submission. Scratch; paraphrase into `paper.tex` once design is locked.

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

## Session continuity

After any paper-scoping decision (framing change, section drop, experiment cut), save it as a `project_*` memory before writing prose.
This keeps future sessions from re-deriving context from scratch.

For broad exploratory questions ("how do AWS and GCP differ on embodied?"), delegate to an `Agent subagent_type=Explore` — it reads the `.txt` companions and returns a concise synthesis, keeping the main context window clean.

## When in doubt

Ask the user. Surfacing uncertainty is always cheaper than writing something wrong into the paper. A passing self-check is not evidence the claim is right — it's only evidence your self-check didn't catch the bug.
