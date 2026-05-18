"""
Analysis 2 — Reconciliation against the constructed top-down report.

Reads the master simulation trace (`data/processed/simulation_trace.parquet`)
and renders a stacked-bar comparison of:

  (a) Top-down report, decomposed by scope/category.
  (b) Sum_i SCI_i  * R_i  — past-lifetime A100 carries M = 0 per SCI v1.1.
  (c) Sum_i oSCI_i * R_i  — operational-only refinement.
  (d) Sum_i rSCI_i * R_i  — matches (a) exactly by construction.

Writes paper/figures/a2_reconciliation.pdf.

Run: `uv run python -m experiments.a2_reconciliation`
"""

from __future__ import annotations

import pathlib

import matplotlib.pyplot as plt
import pandas as pd

from experiments.constants import DGX_A100, DGX_H100, PUE
from experiments.picocloud import (
    HOURS_PER_WEEK,
    SYSTEMS,
    TopDown,
    build_topdown,
    slice_active_energy_kwh,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / "data/processed/simulation_trace.parquet"
OUT = ROOT / "paper/figures/a2_reconciliation.pdf"


def topdown_components(td: TopDown) -> dict[str, float]:
    return {
        "S1": td.s1,
        "S2 (op+PUE+idle)": td.s2_lbm,
        "S3 IT embodied": td.s3_it_embodied,
        "S3 DC infra": td.s3_dc_infra,
        "S3 FERA": td.s3_fera,
        "S3 transport": td.s3_transport,
    }


def sci_components(df: pd.DataFrame) -> dict[str, float]:
    """Σ SCI_i * R_i decomposed into op (active+idle×PUE×I) by GPU plus M."""
    comp: dict[str, float] = {}
    # per-row op kg = per_token_op_g * context_tokens / 1000
    for name in SYSTEMS:
        sub = df[df["gpu"] == name]
        op_kg = (sub["per_token_op_g"] * sub["context_tokens"]).sum() / 1000.0
        comp[f"op×PUE {name}"] = float(op_kg)
        m_kg = (sub["per_token_m_g"] * sub["context_tokens"]).sum() / 1000.0
        if m_kg > 0:
            comp[f"M {name}"] = float(m_kg)
    return comp


def osci_components(df: pd.DataFrame) -> dict[str, float]:
    comp: dict[str, float] = {}
    for name in SYSTEMS:
        sub = df[df["gpu"] == name]
        op_kg = (sub["per_token_op_g"] * sub["context_tokens"]).sum() / 1000.0
        comp[f"op×PUE {name}"] = float(op_kg)
    return comp


def rsci_components(df: pd.DataFrame, td: TopDown) -> dict[str, float]:
    """Σ rSCI_i * R_i decomposed into bottom-up O + scope residuals."""
    # Bottom-up O = Σ γ × tokens × CI(t) — kg_rsci_op_t_term, isolated
    # from per_token_rsci_g = γ*(CI+ρ): the γ*CI piece is the bottom-up O.
    # Σ (γ*CI/J_PER_KWH * tokens) = O_active. We can recover it from columns
    # we already have: kg_rsci - residual_kg, where residual_kg uses γ*ρ.
    residual_kg = (df["per_token_residual_g"] * df["context_tokens"]).sum() / 1000.0
    rsci_total = (df["per_token_rsci_g"] * df["context_tokens"]).sum() / 1000.0
    o_active_kg = float(rsci_total - residual_kg)

    delta_s2 = td.s2_lbm - o_active_kg
    return {
        "Bottom-up op (E·I)": o_active_kg,
        "Δ S1": td.s1,
        "Δ S2": delta_s2,
        "Δ S3": td.s3,
    }


PALETTE = {
    "S1": "#cccccc",
    "S2 (op+PUE+idle)": "#4f8fc3",
    "S3 IT embodied": "#7a3b3b",
    "S3 DC infra": "#b86b6b",
    "S3 FERA": "#d6a59c",
    "S3 transport": "#e8d3cc",
    f"op×PUE {DGX_A100.name}": "#6fa8d1",
    f"op×PUE {DGX_H100.name}": "#3a6c95",
    f"M {DGX_A100.name}": "#a44a4a",
    f"M {DGX_H100.name}": "#7a3b3b",
    "Bottom-up op (E·I)": "#3a6c95",
    "Δ S1": "#cccccc",
    "Δ S2": "#9fb8cf",
    "Δ S3": "#b86b6b",
}


def stacked_bar(ax, x, components: dict[str, float]) -> float:
    bottom = 0.0
    for label, val in components.items():
        if val <= 0:
            continue
        ax.bar(x, val, bottom=bottom, color=PALETTE.get(label, "#888"),
               edgecolor="white", linewidth=0.5, width=0.7, label=label)
        if val > 15:
            ax.text(x, bottom + val / 2, label, ha="center", va="center",
                    fontsize=7, color="white")
        bottom += val
    return bottom


def main() -> None:
    if not TRACE.exists():
        raise SystemExit(
            f"{TRACE} not found. Run `uv run python -m experiments.run_simulation` first."
        )

    df = pd.read_parquet(TRACE)

    # Re-derive top-down using the trace-integrated S2 (= Σ kg_osci).
    R = float(df["context_tokens"].sum())
    s2_integrated = float((df["per_token_op_g"] * df["context_tokens"]).sum() / 1000.0)
    td = build_topdown(R, s2_lbm_override_kg=s2_integrated)

    bars = [
        ("Top-down\n(ground truth)", topdown_components(td)),
        ("SCI", sci_components(df)),
        ("oSCI", osci_components(df)),
        ("rSCI", rsci_components(df, td)),
    ]

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    totals: list[float] = []
    for i, (_, comps) in enumerate(bars):
        totals.append(stacked_bar(ax, i, comps))
    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([b[0] for b in bars], fontsize=9)
    ax.set_ylabel("Weekly attributed footprint (kgCO₂e)")
    ax.set_title(
        "Analysis 2 — Reconciliation against constructed top-down report",
        fontsize=10,
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eee", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    tot_topdown = totals[0]
    for i, t in enumerate(totals):
        label = f"{t:.0f} kg" if i == 0 else f"{t:.0f} kg\n({t / tot_topdown:.0%})"
        ax.text(i, t + tot_topdown * 0.015, label, ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, tot_topdown * 1.25)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    print(f"wrote {OUT}")

    print()
    print("Bar totals (kgCO2e / week):")
    for (name, _), t in zip(bars, totals):
        print(f"  {name.replace(chr(10), ' '):<35} {t:>8.2f}    "
              f"({t / tot_topdown * 100:5.1f}% of top-down)")


if __name__ == "__main__":
    main()
