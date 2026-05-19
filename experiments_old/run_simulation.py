"""
Run the toy-cloud simulation and persist the master per-minute trace.

This script is the single source of truth for the §4 attribution numbers. All
downstream drivers (a0_sanity, a1, a2, timeseries) read the resulting parquet
rather than re-computing from constants.

Inputs (all in `data/`):
  - processed/per_minute.parquet  — Azure trace, per-minute aggregates per workload
  - carbonintensity_2026-03-23.csv — hourly grid CI, multi-region

Output (`data/processed/simulation_trace.parquet`):
  Long format, one row per (timestamp_minute, gpu).
  ~20k rows for a 7-day week.

  Columns:
    timestamp              datetime[min]
    gpu                    category — DGX A100 / DGX H100
    n_requests             int      — workload-merged requests this minute, allocated
                                       to this GPU by throughput-weighted routing share
    context_tokens         int      — same, ContextTokens summed
    generated_tokens       int      — carried for completeness
    grid_ci_gco2_per_kwh   float    — hourly CI at this minute's hour
    per_token_op_g         float    — (gamma + idle_share) * PUE * I_r(t), gCO2/tok
    per_token_m_g          float    — SCI M-term (constant per gpu; 0 for past-EL A100)
    per_token_residual_g   float    — gamma * rho (rSCI residual; rho is slice-constant)
    per_token_sci_g        float    — op + m
    per_token_osci_g       float    — op
    per_token_rsci_g       float    — gamma * (I_r(t) + rho) = gamma*xi(t)
    kg_sci, kg_osci, kg_rsci  float — per-row mass (per_token * context_tokens / 1000)

Run: `uv run python -m experiments.run_simulation`
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

from experiments.constants import DGX_A100, DGX_H100, PUE, ROUTING_SHARE
from experiments.metrics import m_per_token_g, xi_gco2_per_kwh
from experiments.picocloud import (
    GAMMA,
    HOURS_PER_WEEK,
    J_PER_KWH,
    SYSTEMS,
    build_topdown,
    load_grid_intensity,
    slice_active_energy_kwh,
    slice_idle_energy_kwh,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
PER_MIN_IN = ROOT / "data/processed/per_minute.parquet"
TRACE_OUT = ROOT / "data/processed/simulation_trace.parquet"


def _tile_grid_ci(per_minute_index: pd.DatetimeIndex) -> pd.Series:
    """
    The CI CSV covers one calendar day; the trace is 7 days. Tile the 24-hour
    pattern over the trace window by mapping each trace hour to its hour-of-day
    in the CSV. Returns a series indexed by per_minute_index.
    """
    grid = load_grid_intensity().set_index("datetime")
    grid["hour"] = grid.index.hour
    by_hour = grid.groupby("hour")["gco2_per_kwh"].mean()  # one value per hour-of-day
    ci_per_min = per_minute_index.to_series().dt.hour.map(by_hour).astype(float).values
    return pd.Series(ci_per_min, index=per_minute_index, name="grid_ci_gco2_per_kwh")


def main() -> None:
    print(f"Reading {PER_MIN_IN} ...")
    pm = pd.read_parquet(PER_MIN_IN)

    # ----- 1) Merge workloads: collapse the `service` axis ------------------
    combined = (
        pm.groupby("timestamp", observed=True)
        .agg(
            n_requests=("n_requests", "sum"),
            context_tokens=("context_tokens_sum", "sum"),
            generated_tokens=("generated_tokens_sum", "sum"),
        )
        .reset_index()
        .sort_values("timestamp")
    )
    print(f"  combined: {len(combined):,} minutes, "
          f"{combined.timestamp.min()} → {combined.timestamp.max()}")

    # ----- 2) Slice-level totals (no CI yet) -------------------------------
    R_total = float(combined["context_tokens"].sum())
    e_active = slice_active_energy_kwh(R_total)["total"]
    e_idle_total = slice_idle_energy_kwh(HOURS_PER_WEEK)["total"]

    # gamma averaged over routing shares — used for per-minute bottom-up E
    gamma_avg = sum(GAMMA[name] * share for name, share in ROUTING_SHARE.items())

    # Idle-share per token (uniform allocation: spec-faithful for SCI/oSCI).
    idle_j_per_token = e_idle_total * J_PER_KWH / R_total

    # ----- 3) Tile CI hourly over the trace minute index -------------------
    combined["grid_ci_gco2_per_kwh"] = _tile_grid_ci(
        pd.DatetimeIndex(combined["timestamp"])
    ).values

    # ----- 4) Time-integrated S2 and O_active ------------------------------
    # IT energy per minute, with idle allocated *per-token* (consistent with the
    # per-row attribution in step 5). The total idle over the week is the same,
    # but its time distribution tracks tokens served (so high-activity minutes
    # bear more idle). This is what keeps Σ kg_osci = top-down S2 exactly.
    tokens_arr = combined["context_tokens"].astype(float).values
    minute_active_kwh = gamma_avg * tokens_arr / J_PER_KWH
    minute_idle_kwh = (e_idle_total / R_total) * tokens_arr  # per-token allocation
    minute_it_kwh = minute_active_kwh + minute_idle_kwh
    ci_arr = combined["grid_ci_gco2_per_kwh"].values

    # S2 (LBM, with PUE) — constructed to be internally consistent with per-row
    # attribution. A real metered S2 would integrate per-minute uniform idle;
    # we adopt per-token-uniform here so the toy reconciles cleanly.
    s2_integrated_kg = float((minute_it_kwh * PUE * ci_arr).sum() / 1000.0)

    # Bottom-up O_active — sum of E_active * I_r(t), per paper §rSCI
    o_active_integrated_kg = float((minute_active_kwh * ci_arr).sum() / 1000.0)

    # Build top-down with the time-integrated S2 (other S3 lines stay constant)
    td = build_topdown(R_total, s2_lbm_override_kg=s2_integrated_kg)

    # Slice-level rho per the paper: rho = (Delta^S1 + Delta^S2 + Delta^S3) / E_active
    delta_s2 = td.s2_lbm - o_active_integrated_kg
    rho = (td.s1 + delta_s2 + td.s3) * 1000.0 / e_active  # kg/kWh -> g/kWh

    print(f"  weekly slice totals: E_active={e_active:,.1f} kWh, "
          f"E_idle={e_idle_total:,.1f} kWh, R={R_total:,.0f} tokens")
    print(f"  S2 (time-integrated)   = {s2_integrated_kg:.2f} kg")
    print(f"  O_active (∫γ·R·I_r dt) = {o_active_integrated_kg:.2f} kg")
    print(f"  Δ^S2 (residual bridge) = {delta_s2:.2f} kg")
    print(f"  rho                    = {rho:.2f} gCO2/kWh  (slice-level constant)")

    # ----- 4) Expand by GPU, apply routing share ----------------------------
    parts = []
    for gpu_name, share in ROUTING_SHARE.items():
        sub = combined.copy()
        sub["gpu"] = gpu_name
        sub["n_requests"] = (sub["n_requests"] * share).round().astype("int64")
        sub["context_tokens"] = (sub["context_tokens"] * share).round().astype("int64")
        sub["generated_tokens"] = (sub["generated_tokens"] * share).round().astype("int64")
        parts.append(sub)
    long = pd.concat(parts, ignore_index=True)

    # ----- 5) Per-token attribution (minute-resolved I_r(t)) ----------------
    gamma = long["gpu"].map(GAMMA).astype(float).values
    m_per_tok = long["gpu"].map(
        {name: m_per_token_g(name) for name in SYSTEMS}
    ).astype(float).values

    ci = long["grid_ci_gco2_per_kwh"].values

    # Faithful SCI/oSCI E per token: (gamma + idle_share) * PUE, in J/tok
    e_op_j_per_tok = (gamma + idle_j_per_token) * PUE
    long["per_token_op_g"] = e_op_j_per_tok * ci / J_PER_KWH
    long["per_token_m_g"] = m_per_tok
    long["per_token_sci_g"] = long["per_token_op_g"] + long["per_token_m_g"]
    long["per_token_osci_g"] = long["per_token_op_g"]

    # rSCI: gamma * xi(t) / J_PER_KWH, where xi(t) = I_r(t) + rho
    long["per_token_residual_g"] = gamma * rho / J_PER_KWH
    long["per_token_rsci_g"] = gamma * (ci + rho) / J_PER_KWH

    # ----- 6) Per-row mass (kgCO2e) ----------------------------------------
    toks = long["context_tokens"].astype(float).values
    long["kg_sci"] = long["per_token_sci_g"].values * toks / 1000.0
    long["kg_osci"] = long["per_token_osci_g"].values * toks / 1000.0
    long["kg_rsci"] = long["per_token_rsci_g"].values * toks / 1000.0

    long["gpu"] = pd.Categorical(long["gpu"], categories=list(ROUTING_SHARE.keys()))
    long = long.sort_values(["timestamp", "gpu"]).reset_index(drop=True)

    # ----- 7) Persist -------------------------------------------------------
    TRACE_OUT.parent.mkdir(parents=True, exist_ok=True)
    long.to_parquet(TRACE_OUT, compression="zstd")
    print()
    print(f"wrote {TRACE_OUT}")
    print(f"  rows = {len(long):,}")
    print(f"  size = {TRACE_OUT.stat().st_size / 1024:.0f} KB")

    # ----- 8) Aggregate sanity check ---------------------------------------
    print()
    print("Aggregate sanity (sum over trace):")
    print(f"  sum context_tokens     = {long['context_tokens'].sum():,.0f}  "
          f"(vs R_total = {R_total:,.0f})")
    print(f"  sum kg_sci             = {long['kg_sci'].sum():>8.2f}")
    print(f"  sum kg_osci            = {long['kg_osci'].sum():>8.2f}")
    print(f"  sum kg_rsci            = {long['kg_rsci'].sum():>8.2f}")
    print(f"  top-down total         = {td.total:>8.2f}    (rSCI must match)")


if __name__ == "__main__":
    main()
