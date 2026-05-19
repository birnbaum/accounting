"""
Analysis 1 — Sunk-carbon pathology (Bashir 2024) on the toy cloud.

Headline: identical inference requests receive systematically wrong SCI
attributions on aged hardware; rSCI gives the right embodied gradient and oSCI
is silent on the embodied axis.

Under the linear prefill energy model, per-ContextToken attribution collapses to
a constant per GPU type for each metric, so the natural visual is a grouped
bar by metric × GPU with op vs M decomposed. The per-request size distribution
(ContextTokens varies over ~3 orders of magnitude across the trace) is shown as
a side panel — total per-request kgCO2e is simply the per-token value × request
size, so the figure carries the per-request information without a degenerate
scatter.

Writes paper/figures/a1_sunk_carbon.pdf.

Run: `uv run python -m experiments_old.a1_sunk_carbon`
"""

from __future__ import annotations

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from experiments_old.constants import DGX_A100, DGX_H100
from experiments_old.picocloud import SYSTEMS

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / "data/processed/simulation_trace.parquet"
SAMPLE = ROOT / "data/processed/sample_per_request.parquet"
OUT = ROOT / "paper/figures/a1_sunk_carbon.pdf"


GPU_COLOR = {
    DGX_A100.name: "#c97e5d",  # warmer tone for the "old" system
    DGX_H100.name: "#3a6c95",  # cooler for the "new" system
}


def main() -> None:
    if not TRACE.exists():
        raise SystemExit(
            f"{TRACE} not found. Run `uv run python -m experiments_old.run_simulation` first."
        )

    trace = pd.read_parquet(TRACE)
    # Token-weighted per-token values per GPU type, from the trace.
    decomps: dict[str, dict[str, float]] = {}
    intens: dict[str, dict[str, float]] = {}
    for name in SYSTEMS:
        sub = trace[trace["gpu"] == name]
        w = sub["context_tokens"].astype(float)

        def wavg(col: str) -> float:
            return float((sub[col] * w).sum() / w.sum())
        decomps[name] = {"op": wavg("per_token_op_g"), "m": wavg("per_token_m_g")}
        intens[name] = {
            "sci": wavg("per_token_sci_g"),
            "osci": wavg("per_token_osci_g"),
            "rsci": wavg("per_token_rsci_g"),
        }

    # ----------------------------------------------------------------- Figure
    fig, (ax_bar, ax_hist) = plt.subplots(
        1, 2, figsize=(10.5, 4.4), gridspec_kw={"width_ratios": [1.4, 1.0]}
    )

    # ===== Left panel: per-token attribution by metric × GPU =================
    metrics = ["SCI", "oSCI", "rSCI"]
    gpus = list(SYSTEMS.keys())
    x = np.arange(len(metrics))
    width = 0.36

    # Convert all to μg/token for readable y-axis
    UG = 1e6

    for j, name in enumerate(gpus):
        op = decomps[name]["op"] * UG
        m = decomps[name]["m"] * UG
        rsci_val = intens[name]["rsci"] * UG
        # Per-metric stacked values:
        #   SCI = op (active+idle×PUE×I) + M
        #   oSCI = op
        #   rSCI = γ × xi / J_PER_KWH (single value; can't be op/M-split — it's
        #          decomposed differently, by residual bridges)
        sci_op, sci_m = op, m
        osci_op = op
        # rSCI: show as a single solid bar; decomposing into "active op contribution +
        # residual contribution" needs xi math that doesn't fit op/M split cleanly here.
        rsci_total = rsci_val

        offset = (j - 0.5) * width
        # SCI: op + M stacked
        ax_bar.bar(x[0] + offset, sci_op, width=width, color=GPU_COLOR[name],
                   edgecolor="white", linewidth=0.6, label=name if x[0] == 0 else None)
        ax_bar.bar(x[0] + offset, sci_m, width=width, bottom=sci_op,
                   color=GPU_COLOR[name], edgecolor="white", linewidth=0.6,
                   hatch="///", alpha=0.55)
        # oSCI
        ax_bar.bar(x[1] + offset, osci_op, width=width, color=GPU_COLOR[name],
                   edgecolor="white", linewidth=0.6)
        # rSCI
        ax_bar.bar(x[2] + offset, rsci_total, width=width, color=GPU_COLOR[name],
                   edgecolor="white", linewidth=0.6, alpha=0.85)

        # Annotate M-term presence/absence for SCI
        if m < 0.001:
            ax_bar.text(x[0] + offset, sci_op + 0.15, "M=0",
                        ha="center", va="bottom", fontsize=8, color="#7a3b3b",
                        fontweight="bold")

    # Legend: solid = op (active+idle×PUE), hatched = M-term
    from matplotlib.patches import Patch
    legend_items = [
        Patch(facecolor=GPU_COLOR[DGX_A100.name], label=f"{DGX_A100.name} (aged)"),
        Patch(facecolor=GPU_COLOR[DGX_H100.name], label=f"{DGX_H100.name} (fresh)"),
        Patch(facecolor="#888", hatch="///", alpha=0.55, label="SCI $M$-term (embodied)"),
    ]
    ax_bar.legend(handles=legend_items, loc="upper left", fontsize=8, frameon=False)

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(metrics)
    ax_bar.set_ylabel("Per-token attribution (μgCO₂e / ContextToken)")
    ax_bar.set_title(
        "Per-token attribution under each metric, by GPU type\n"
        "rSCI: A100 > H100 (correct).  SCI: M=0 on aged A100 (Bashir pathology).",
        fontsize=9,
    )
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.grid(axis="y", color="#eee", linewidth=0.5, zorder=0)
    ax_bar.set_axisbelow(True)

    # ===== Right panel: ContextTokens distribution from the real trace =======
    sample = pd.read_parquet(SAMPLE)
    bins = np.logspace(0, 4.5, 60)
    for svc, color in [("conv", "#6fa8d1"), ("code", "#c97e5d")]:
        sub = sample[sample.service == svc]
        ax_hist.hist(sub.context_tokens, bins=bins, color=color, alpha=0.55,
                     label=f"{svc}-svc (n={len(sub):,})", edgecolor="white", linewidth=0.3)
    ax_hist.set_xscale("log")
    ax_hist.set_xlabel("ContextTokens per request (log)")
    ax_hist.set_ylabel("Request count (sample)")
    ax_hist.set_title(
        "Trace request-size distribution\n"
        "Per-request total = (per-token attribution) × ContextTokens.",
        fontsize=9,
    )
    ax_hist.legend(fontsize=8, frameon=False)
    ax_hist.spines[["top", "right"]].set_visible(False)
    ax_hist.grid(axis="y", color="#eee", linewidth=0.5, zorder=0)
    ax_hist.set_axisbelow(True)

    fig.suptitle(
        "Analysis 1 — Sunk-carbon pathology: per-token attribution, single slice 2-DGX toy",
        fontsize=10, y=1.01,
    )
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    print(f"wrote {OUT}")

    # Numerics for the prose
    print()
    print("Per-token attribution (μgCO2e / ContextToken):")
    print(f"  {'GPU':<12} {'SCI op':>10} {'SCI M':>10} {'SCI total':>11} "
          f"{'oSCI':>10} {'rSCI':>10}")
    for name in gpus:
        op = decomps[name]["op"] * UG
        m = decomps[name]["m"] * UG
        sci_total = op + m
        osci = intens[name]["osci"] * UG
        rsci = intens[name]["rsci"] * UG
        print(f"  {name:<12} {op:>10.3f} {m:>10.3f} {sci_total:>11.3f} "
              f"{osci:>10.3f} {rsci:>10.3f}")

    print()
    print("Embodied gradient (A100 vs H100, μgCO2e/token):")
    sci_a100_m = decomps[DGX_A100.name]["m"] * UG
    sci_h100_m = decomps[DGX_H100.name]["m"] * UG
    rsci_a100 = intens[DGX_A100.name]["rsci"] * UG
    rsci_h100 = intens[DGX_H100.name]["rsci"] * UG
    print(f"  SCI:   A100 M = {sci_a100_m:.3f}, H100 M = {sci_h100_m:.3f}  "
          f"→ ratio A100/H100 = {sci_a100_m / max(sci_h100_m, 1e-9):.2f} "
          f"(pathology: aged system M=0, fresh system carries the embodied)")
    print(f"  rSCI:  A100   = {rsci_a100:.3f}, H100   = {rsci_h100:.3f}  "
          f"→ ratio A100/H100 = {rsci_a100 / rsci_h100:.2f} "
          f"(correct: aged & less-efficient → higher rSCI)")


if __name__ == "__main__":
    main()
