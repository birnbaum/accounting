"""
Timeseries view of how SCI / oSCI / rSCI signals differ in magnitude and
composition over the simulated week.

Three stacked panels:
  1. Per-minute kg by metric — the mass signal each metric attributes per minute.
     Shows how the three metrics differ over time, driven by I_r(t) hourly cycle
     × workload(t) diurnal cycle.
  2. rSCI mass composition (stacked area) — bottom-up op (γ·I_r(t)) vs
     time-constant residual (γ·ρ). Makes visible that rSCI's gap over oSCI is
     a constant intensity ρ applied to every token, not a time-varying signal.
  3. Context: grid CI (gCO2/kWh) and ContextTokens served per minute. The two
     drivers of variation in panel 1.

Writes paper/figures/timeseries.pdf.

Run: `uv run python -m experiments_old.timeseries`
"""

from __future__ import annotations

import pathlib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / "data/processed/simulation_trace.parquet"
OUT = ROOT / "paper/figures/timeseries.pdf"

# Resample window: per-minute is noisy at a 7-day scale. 30-min bins balance
# legibility with preserving the hourly CI structure.
BIN = "30min"

COLOR = {
    "SCI": "#a44a4a",
    "oSCI": "#3a6c95",
    "rSCI": "#2a7a4a",
    "op (γ·I_r(t))": "#3a6c95",
    "residual (γ·ρ)": "#9c6b3b",
    "ContextTokens": "#888",
    "Grid CI": "#a44a4a",
}


def main() -> None:
    if not TRACE.exists():
        raise SystemExit(
            f"{TRACE} not found. Run `uv run python -m experiments_old.run_simulation` first."
        )
    df = pd.read_parquet(TRACE)
    # Aggregate over GPU to per-minute totals
    per_min = (
        df.groupby("timestamp", observed=True)
        .agg(
            kg_sci=("kg_sci", "sum"),
            kg_osci=("kg_osci", "sum"),
            kg_rsci=("kg_rsci", "sum"),
            context_tokens=("context_tokens", "sum"),
            grid_ci=("grid_ci_gco2_per_kwh", "first"),  # same per minute across gpus
            # rSCI decomposition components — token-weighted sums
            op_kg=("kg_osci", "sum"),  # equal to per-row op*tokens summed over gpus
        )
        .reset_index()
        .set_index("timestamp")
    )
    # rSCI residual mass per minute = Σ_gpu (per_token_residual_g × tokens)
    residual_per_min = (
        df.assign(residual_kg=df["per_token_residual_g"] * df["context_tokens"] / 1000.0)
        .groupby("timestamp", observed=True)["residual_kg"]
        .sum()
    )
    bottom_up_op_per_min = (
        df.assign(
            bo_kg=(df["per_token_rsci_g"] - df["per_token_residual_g"])
            * df["context_tokens"]
            / 1000.0
        )
        .groupby("timestamp", observed=True)["bo_kg"]
        .sum()
    )
    per_min["rsci_residual_kg"] = residual_per_min
    per_min["rsci_op_kg"] = bottom_up_op_per_min

    # Resample to BIN bins (sum for mass, mean for intensity context)
    agg = per_min.resample(BIN).agg(
        kg_sci=("kg_sci", "sum"),
        kg_osci=("kg_osci", "sum"),
        kg_rsci=("kg_rsci", "sum"),
        rsci_op_kg=("rsci_op_kg", "sum"),
        rsci_residual_kg=("rsci_residual_kg", "sum"),
        context_tokens=("context_tokens", "sum"),
        grid_ci=("grid_ci", "mean"),
    )

    # ----------------------------------------------------------------- Figure
    fig, axes = plt.subplots(
        3, 1, figsize=(11, 7.5), sharex=True,
        gridspec_kw={"height_ratios": [1.4, 1.4, 1.0]},
    )

    # ---- Panel 1: per-minute (per-bin) kg by metric -----------------------
    ax = axes[0]
    ax.plot(agg.index, agg["kg_sci"], color=COLOR["SCI"], label="SCI", linewidth=1.0)
    ax.plot(agg.index, agg["kg_osci"], color=COLOR["oSCI"], label="oSCI", linewidth=1.0)
    ax.plot(agg.index, agg["kg_rsci"], color=COLOR["rSCI"], label="rSCI", linewidth=1.2)
    ax.set_ylabel(f"kgCO₂e / {BIN}")
    ax.set_title("Per-bin attributed mass — magnitude over time", fontsize=10)
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eee", linewidth=0.5)
    ax.set_axisbelow(True)
    # Weekly horizontal totals annotation
    week_totals = {
        "SCI": agg["kg_sci"].sum(),
        "oSCI": agg["kg_osci"].sum(),
        "rSCI": agg["kg_rsci"].sum(),
    }
    txt = "  ·  ".join(f"Σ {k} = {v:.0f} kg" for k, v in week_totals.items())
    ax.text(0.01, 0.97, txt, transform=ax.transAxes, fontsize=8,
            va="top", color="#444", family="monospace")

    # ---- Panel 2: rSCI composition (stacked area) -------------------------
    ax = axes[1]
    ax.fill_between(agg.index, 0, agg["rsci_op_kg"],
                    color=COLOR["op (γ·I_r(t))"], alpha=0.85,
                    label="Bottom-up op   (γ·I_r(t)·R)")
    ax.fill_between(agg.index, agg["rsci_op_kg"],
                    agg["rsci_op_kg"] + agg["rsci_residual_kg"],
                    color=COLOR["residual (γ·ρ)"], alpha=0.85,
                    label="Slice residual (γ·ρ·R)")
    # Overlay oSCI line so the viewer sees where oSCI lands inside the rSCI stack
    ax.plot(agg.index, agg["kg_osci"], color=COLOR["oSCI"], linewidth=1.0,
            linestyle="--", label="oSCI (for reference)")
    ax.set_ylabel(f"kgCO₂e / {BIN}")
    ax.set_title(
        "rSCI mass composition — bottom-up op varies with grid CI, "
        "residual is the time-constant intensity ρ applied to every token",
        fontsize=10,
    )
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eee", linewidth=0.5)
    ax.set_axisbelow(True)

    # ---- Panel 3: drivers (grid CI + tokens) ------------------------------
    ax = axes[2]
    ax2 = ax.twinx()
    ax.fill_between(agg.index, 0, agg["context_tokens"] / 1e6, color=COLOR["ContextTokens"],
                    alpha=0.35, label="ContextTokens (M / bin)")
    ax2.plot(agg.index, agg["grid_ci"], color=COLOR["Grid CI"], linewidth=1.0,
             label="Grid CI (us-central1)")
    ax.set_ylabel("ContextTokens (M)", color="#666")
    ax2.set_ylabel("gCO₂ / kWh", color=COLOR["Grid CI"])
    ax.set_title("Drivers — workload (left) and grid CI (right)", fontsize=10)
    ax.spines[["top"]].set_visible(False)
    ax2.spines[["top"]].set_visible(False)
    ax.grid(axis="y", color="#eee", linewidth=0.5)
    ax.set_axisbelow(True)
    # Combined legend
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8, frameon=False)

    # X-axis formatting on the bottom-most
    for a in axes:
        a.xaxis.set_major_locator(mdates.DayLocator())
        a.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m"))
    axes[-1].set_xlabel(None)
    fig.autofmt_xdate(rotation=0, ha="center")

    fig.suptitle(
        "Signal magnitude & composition over the simulated week — single-slice 2-DGX toy",
        fontsize=11, y=1.005,
    )
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"wrote {OUT}")
    print()
    print(f"Bins: {BIN}, {len(agg)} samples over {(agg.index[-1] - agg.index[0])!s}")
    print(f"Weekly totals (kgCO2e): " + "  ".join(f"{k}={v:.1f}" for k, v in week_totals.items()))


if __name__ == "__main__":
    main()
