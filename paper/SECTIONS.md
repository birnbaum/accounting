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
| §2 | State of the Art in Cloud Carbon Reporting | `sec:sota` | cross_provider_synthesis.md, all carbon_accounting_methodologies/<provider>/README.md, terminology.md |
| §3 | The Issue with Bottom-Up Carbon Metrics | `sec:background` | SCI.md, sources/bashir-2024-sunk-carbon/bashir-2024-sunk-carbon.tex |
| §4 | Reconciling Bottom-Up and Top-Down | `sec:rsci` | SHARMA_2024_SHAPLEY.md, BOAVIZTAPI_2024.md, CINERGY_2025.md |
| §5 | Example | `sec:demo` | `experiments/trace_analysis.py` (live notebook) → `figures/sec5_example.pdf`. Single 8xH100 node, single workload; one figure (timeline + reconciliation gauges); Setup/Result/Properties prose written. See `project_sec5_example_design` memory. |
| §6 | Barriers to Practical Adoption | `sec:practice` | provider READMEs (gaps), terminology.md, aws/ (CUR + CCFT), Scaleway; two barriers (coarse reports / opaque+inconsistent methodologies), each with a callforaction box. Barrier 1: AWS 81% in "Other" (Fig `fig:aws`, spend-vs-carbon inversion) + Scaleway buggy-daily paragraph. Barrier 2: EC2 negative-residual smell + Microsoft self-divergence (`microsoft-s3-2021`) |
| §7 | Call to Action | `sec:asks` | cross_provider_synthesis.md §5; Future Work merged in as the `Outlook` paragraph (2026-07-01) |
| App A | Cloud provider survey universe (48 providers) | `app:inventory` | carbon_accounting_methodologies/README.md + non-customer-tool-providers.md |
| App B | Scope-3 category coverage in the Big-3 (`tab:bigthree-s3`) | `app:bigthree-s3` | per-provider READMEs (moved out of §3 `\iffalse` salvage, 2026-07-01) |

## Subsection landmarks (§4)

| Subsection | Anchor |
|------------|--------|
| Weight families: the residual as a design surface | `sec:rsci-design` |
