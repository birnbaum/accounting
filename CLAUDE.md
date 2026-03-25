# CLAUDE.md

## Project

Research framework for reconciling bottom-up software carbon intensity (SCI) metrics with top-down provider-reported GHG numbers. Academic/research context — not production software.

## README.md style

The README is a living research document for rapid iteration on ideas. Keep it concise:
- **Intro section**: can be more expository — collaborators need to understand the problem and motivation.
- **Everything after the intro**: definitions, math, and brief context only. No unnecessary prose or re-explanation. Say it once, reference it later.
- When concepts are defined once (e.g., the residual decomposition), do not re-explain them in later sections.

## General style

- Be concise. Prefer precision over prose.
- Don't add docstrings, comments, or type annotations to code that wasn't changed.
- This is a research repo — scripts are exploratory, not production code.

## Key files

- `README.md` — core framework definition (rSCI)
- `HYPERSCALER_CARBON_ACCOUNTING.md` — provider methodology comparison
- `SCHEMA.md` — provider profile schema and populated profiles
- `gcp/` — GCP benchmark experiments and data collection
- `azure/` — Azure carbon export data and analysis
