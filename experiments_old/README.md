# `experiments/` — §4 toy-cloud simulation

Scripts that build the §4 reference toy cloud, replay the real Azure 2024 LLM
inference trace through a fully-controlled energy + attribution model, and
emit the figures in `paper/figures/`.

Authoritative design notes: `paper/experiments_design.md`.
Source-grounding rule: see `/CLAUDE.md`.

## Pipeline at a glance

```
        raw CSVs ──► prepare_data.py ──► per_minute.parquet ──► run_simulation.py ──► simulation_trace.parquet
                                                                                              │
                                                                                              ├──► a0_sanity.py        (stdout)
                                                                                              ├──► a2_reconciliation.py (figure)
                                                                                              ├──► timeseries.py       (figure)
                                                                                              └──► a1_sunk_carbon.py   (figure)
```

The **`simulation_trace.parquet`** is the single source of truth for the §4
attribution numbers. All downstream drivers read from it; they do not
re-derive the math from `constants.py`. To re-run the simulation after
changing a constant, re-run `run_simulation.py` first.

## Where things live

| Stage | Path | What it is |
|---|---|---|
| Raw trace input | `data/AzureLLMInferenceTrace_{conv,code}_1week.csv` | Azure LLM Inference Dataset 2024 (gitignored). Download from <https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md>. |
| Grid CI input | `data/carbonintensity_2026-03-23.csv` | 24-hour multi-region grid CI. Tiled hourly over the 7-day trace window. |
| Per-minute aggregates | `data/processed/per_minute.parquet` | One row per `(minute, workload)`; request count + token sums. Produced by `prepare_data.py`. |
| Sample of requests | `data/processed/sample_per_request.parquet` | 50k requests / workload, fixed seed. Used for the request-size histogram in `a1_sunk_carbon.py`. |
| **Master simulation trace** | `data/processed/simulation_trace.parquet` | **One row per `(minute, gpu)` ≈ 26k rows.** All per-token / per-row attribution lives here. |
| Figures | `paper/figures/a{1,2,3}_*.pdf`, `timeseries.pdf` | Per-driver outputs. |

### `simulation_trace.parquet` schema

| Column | Type | Notes |
|---|---|---|
| `timestamp` | datetime[min] | Aligned to the Azure trace's 7-day window. |
| `gpu` | category | `DGX A100` / `DGX H100`. Tokens allocated by throughput-weighted routing share (~28.6 / 71.4%). |
| `n_requests`, `context_tokens`, `generated_tokens` | int | Combined across workloads, allocated to this GPU. |
| `grid_ci_gco2_per_kwh` | float | Hourly CI at this minute's hour (24h pattern tiled). |
| `per_token_op_g` | float | Faithful SCI/oSCI E per token: $(\gamma_g + \text{idle\_share}) \cdot \text{PUE} \cdot I_r(t)$. |
| `per_token_m_g` | float | SCI M-term (constant per GPU; 0 for fully-past-EL A100). |
| `per_token_residual_g` | float | rSCI residual share: $\gamma_g \cdot \rho$ where $\rho$ is the slice-level residual intensity. |
| `per_token_sci_g`, `per_token_osci_g`, `per_token_rsci_g` | float | Sum of components. |
| `kg_sci`, `kg_osci`, `kg_rsci` | float | Per-row mass: per_token × context_tokens / 1000. |

**Invariants** (verified at the end of `run_simulation.py`):
- $\sum \text{kg\_rsci} = $ top-down report total (exact reconciliation by construction)
- $\sum \text{kg\_osci} = $ top-down $S_2$ (faithful SCI-spec idle + PUE → all of $S_2$)

## How to run

All commands from the repo root.

```sh
# One-time: process raw CSVs (only when input CSVs change).
uv run python -m experiments_old.prepare_data

# Run the simulation — produces simulation_trace.parquet.
uv run python -m experiments_old.run_simulation

# Sanity check — stdout, no plotting.
uv run python -m experiments_old.a0_sanity

# Figures — each writes a PDF to paper/figures/.
uv run python -m experiments_old.a1_sunk_carbon     # per-token attribution by metric × GPU
uv run python -m experiments_old.a2_reconciliation  # top-down ↔ Σ metric_i·R_i
uv run python -m experiments_old.timeseries         # how signals vary over the week
# uv run python -m experiments_old.a3_peak_shaving  # TODO
```

The simulation is **fully in-process Python**, single machine. No GPU is
actually run; the "execution" is replaying the Azure trace through the energy
+ attribution model defined in `picocloud.py` + `metrics.py`. The resulting
per-row attribution lives in the master parquet — durable on disk, queryable
from any analysis.

## Module layout

| File | Role |
|---|---|
| `constants.py` | All physical / methodology constants with primary-source citations. Single edit point for retuning the toy. |
| `picocloud.py` | Fleet primitives, throughput-weighted routing, energy model, top-down report construction. |
| `metrics.py` | SCI / oSCI / rSCI definitions, per-token intensities, M-term amortization. |
| `prepare_data.py` | Resamples raw Azure CSVs into the parquet artefacts. |
| `run_simulation.py` | **Main entrypoint.** Reads inputs, applies routing + energy + attribution model, writes the master trace. |
| `a0_sanity.py` | Aggregate sanity check — stdout. Reads the trace. |
| `a1_sunk_carbon.py` | §4.1 Analysis 1 — per-token attribution by metric × GPU. |
| `a2_reconciliation.py` | §4.2 Analysis 2 — top-down vs $\sum_i$ metric$_i \cdot R_i$. |
| `timeseries.py` | Per-minute magnitude and composition of all three metrics over the week. |
| `a3_peak_shaving.py` | §4.3 Analysis 3 — not yet written. |

## When in doubt

- A number is wrong / surprising → check `constants.py` first; every value has
  a comment naming its source. Then re-run `run_simulation.py` so the trace
  picks up the change.
- A new claim wants a citation → see `paper/references.bib`. Entries with
  `localfile = MISSING` should not be cited from `paper.tex` until the source
  lands in `references/sources/`.
- Reconciliation broke (Σ kg_rsci ≠ top-down) → most likely cause is an
  inconsistency between how S2 is integrated in `run_simulation.py` and how
  idle is allocated in the per-row attribution. The current model uses
  per-token-uniform idle allocation throughout.
