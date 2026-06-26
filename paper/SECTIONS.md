# paper.tex Section Map

Living file — update the **anchor** column only when a section is added/removed/renamed (rare); never maintain line numbers (they rot on every edit).
Use this to orient before reading paper.tex; read the section's range, not the whole file.

To jump to a section, grep its anchor to get the current line, then read from there:

```
grep -n '\label{sec:rsci}' paper/paper.tex   # then Read offset=<line>
```

| § | Title | Anchor | Key references |
|---|-------|--------|----------------|
| §1 | Introduction | `sec:intro` | Bashir 2024, SCI.md, greensku-isca-2024.txt, accountable-carbon-footprints-serverless.txt |
| §2 | The Issue with Bottom-Up Carbon Metrics | `sec:background` | SCI.md, sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex |
| §3 | State of the Art in Cloud GHG Reporting | `sec:sota` | cross_provider_synthesis.md, all carbon_accounting_methodologies/<provider>/README.md, terminology.md |
| §4 | Reconciling Bottom-Up and Top-Down | `sec:rsci` | SHARMA_2024_SHAPLEY.md, BOAVIZTAPI_2024.md, CINERGY_2025.md |
| §5 | rSCI in Practice: A Controlled Demonstration | `sec:demo` | `experiments/trace_analysis.py` (live notebook); [[project-experiment2-spine-vision-first]]. Outline/skeleton only — 3 figs (one per gap), prose TBW |
| §6 | Why rSCI Cannot Be Computed Today | `sec:practice` | provider READMEs (gaps), terminology.md, Scaleway (re-run pending) |
| §7 | Call to Action | `sec:asks` | cross_provider_synthesis.md §5 |
| §8 | Future Work | `sec:future-work` | TODO: Acun 2023, Radovanović, Wiesner et al. (self-citations — not yet in references/) |
| §9 | Conclusion | `sec:conclusion` | — |
| App A | Cloud provider survey universe (48 providers) | `app:inventory` | carbon_accounting_methodologies/README.md + non-customer-tool-providers.md |

## Subsection landmarks (§4)

| Subsection | Anchor |
|------------|--------|
| Weight families: the residual as a design surface | `sec:rsci-design` |
