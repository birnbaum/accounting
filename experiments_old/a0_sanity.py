"""
Phase-1 sanity driver. No plotting.

Reads the master simulation trace and prints aggregate numbers + per-GPU
per-token intensities. Run `experiments_old.run_simulation` first to (re)generate
the trace.

Run: `uv run python -m experiments_old.a0_sanity`
"""

from __future__ import annotations

import pathlib

import pandas as pd

from experiments_old.constants import DGX_A100, DGX_H100, ROUTING_SHARE
from experiments_old.metrics import m_per_token_g
from experiments_old.picocloud import (
    HOURS_PER_WEEK,
    SYSTEMS,
    avg_grid_intensity_gco2_per_kwh,
    build_topdown,
    slice_active_energy_kwh,
    slice_idle_energy_kwh,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / "data/processed/simulation_trace.parquet"


def total_context_tokens() -> float:
    """Kept for backward compat with a1_sunk_carbon."""
    df = pd.read_parquet(TRACE, columns=["context_tokens"])
    return float(df["context_tokens"].sum())


def main() -> None:
    if not TRACE.exists():
        raise SystemExit(
            f"{TRACE} not found. Run `uv run python -m experiments_old.run_simulation` first."
        )

    df = pd.read_parquet(TRACE)
    R = float(df["context_tokens"].sum())

    print("=" * 72)
    print("Phase-1 sanity check — single-slice 2-DGX toy cloud")
    print("=" * 72)

    print()
    print(f"Trace: total ContextTokens = {R:,.0f}")
    print(f"  minutes                  = {df['timestamp'].nunique():,}")
    print(f"  rows (minute × gpu)      = {len(df):,}")
    print(f"  weekly average rate      = {R / (HOURS_PER_WEEK * 3600):,.0f} tok/s")
    print()
    print(f"Region grid CI (uniform avg) = {avg_grid_intensity_gco2_per_kwh():.1f} gCO2/kWh")
    print(f"  trace-weighted CI          = "
          f"{(df['grid_ci_gco2_per_kwh'] * df['context_tokens']).sum() / df['context_tokens'].sum():.2f} gCO2/kWh")
    print()
    print(f"Routing shares (throughput-weighted):")
    for k, v in ROUTING_SHARE.items():
        print(f"  {k:<12} = {v:.4f}")

    print()
    print("Slice energy (one week):")
    active = slice_active_energy_kwh(R)
    idle = slice_idle_energy_kwh(HOURS_PER_WEEK)
    print(f"  active IT (DGX A100)  = {active[DGX_A100.name]:>8,.1f} kWh")
    print(f"  active IT (DGX H100)  = {active[DGX_H100.name]:>8,.1f} kWh")
    print(f"  idle  IT (DGX A100)   = {idle[DGX_A100.name]:>8,.1f} kWh")
    print(f"  idle  IT (DGX H100)   = {idle[DGX_H100.name]:>8,.1f} kWh")
    print(f"  total IT              = {active['total'] + idle['total']:>8,.1f} kWh")

    # Reconciliation: aggregate sums from the trace
    sums = {
        "sci": df["kg_sci"].sum(),
        "osci": df["kg_osci"].sum(),
        "rsci": df["kg_rsci"].sum(),
    }
    print()
    print("Aggregate footprint over the week (from trace):")
    print(f"  Sum SCI  * R_i = {sums['sci']:>8.2f} kg")
    print(f"  Sum oSCI * R_i = {sums['osci']:>8.2f} kg")
    print(f"  Sum rSCI * R_i = {sums['rsci']:>8.2f} kg")

    print()
    print("Per-GPU per-token intensity (μgCO2e/ContextToken, weekly avg):")
    print(f"  {'GPU':<12} {'op':>10} {'M':>10} {'SCI':>10} {'oSCI':>10} {'rSCI':>10}")
    for name in SYSTEMS:
        sub = df[df["gpu"] == name]
        # Token-weighted means
        w = sub["context_tokens"].astype(float)
        if w.sum() == 0:
            continue
        def wavg(col: str) -> float:
            return (sub[col] * w).sum() / w.sum() * 1e6
        print(f"  {name:<12} "
              f"{wavg('per_token_op_g'):>10.3f} "
              f"{wavg('per_token_m_g'):>10.3f} "
              f"{wavg('per_token_sci_g'):>10.3f} "
              f"{wavg('per_token_osci_g'):>10.3f} "
              f"{wavg('per_token_rsci_g'):>10.3f}")


if __name__ == "__main__":
    main()
