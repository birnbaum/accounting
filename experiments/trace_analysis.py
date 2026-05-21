import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    return np, pd, plt


@app.cell
def _(np):
    TRACE_FILE = "data/AzureLLMInferenceTrace_conv_1week_minutely.csv"
    CI_FILE = "data/carbon_intensity_2026-05_10d.csv"
    CI_ZONE = "US-CAL-CISO"

    # Fleet definition
    NODES = {
        "DGX A100": {
            "tps": 3000.0,
            "peak_w": 6500.0, 
            "idle_w": 1600.0,
            "te_kg": 3000.0,
            "age_yr": 6.0,
            "lifespan_yr": 6.0
        },
        "DGX H100": {
            "tps": 6100.0,
            "peak_w": 10200.0,
            "idle_w": 2500.0,
            "te_kg": 5000.0,
            "age_yr": 0.0,
            "lifespan_yr": 6.0
        },
    }

    # SCI / Allocation Parameters
    RESIDUAL_KG = 200.0
    SHIFTABLE_FRAC = 0.10
    SCALE = 15.0
    J_PER_KWH = 3_600_000.0

    # Derived constants
    node_names = list(NODES.keys())
    for _v in NODES.values():
        _v["gamma_j_per_tok"] = (_v["peak_w"] - _v["idle_w"]) / _v["tps"]

    TOTAL_TPS = sum(v["tps"] for v in NODES.values())
    routing_arr = np.array([NODES[n]["tps"] / TOTAL_TPS for n in node_names])
    gammas = np.array([NODES[n]["gamma_j_per_tok"] for n in node_names])
    capacity_min = np.array([NODES[n]["tps"] * 60.0 for n in node_names])
    return (
        CI_FILE,
        CI_ZONE,
        J_PER_KWH,
        NODES,
        RESIDUAL_KG,
        SCALE,
        TOTAL_TPS,
        TRACE_FILE,
        capacity_min,
        gammas,
        node_names,
        routing_arr,
    )


@app.cell
def _(SCALE, TRACE_FILE, pd):
    df = pd.read_csv(TRACE_FILE)
    df["minute"] = pd.to_datetime(df["minute"])
    toks_min = df["context_tokens"].astype(float).values / SCALE
    # hour-of-trace index per minute row
    hour_id = ((df["minute"] - df["minute"].iloc[0]).dt.total_seconds() // 3600).astype(int).values
    n_min = len(df)
    return df, hour_id, n_min, toks_min


@app.cell
def _(df, plt):
    # Raw request trace (sanity).
    _fig, _axes = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    _axes[0].plot(df["n_requests"])
    _axes[0].set_ylabel("n_requests")
    _axes[1].plot(df["context_tokens"])
    _axes[1].set_ylabel("context_tokens")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(SCALE, TOTAL_TPS, plt, toks_min):
    # Fleet utilization at the chosen SCALE
    _fig, _ax = plt.subplots(figsize=(10, 2))
    # (tokens/min) / (60s * total_tps) / scale
    # Wait, SCALE was already applied to toks_min in the loading cell.
    _util_series = toks_min / (TOTAL_TPS * 60.0)
    _ax.plot(_util_series)
    _ax.set(ylim=(0, 1), ylabel="fleet utilization")
    _ax.set_title(f"Fleet Utilization (Scale={SCALE})")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(CI_FILE, CI_ZONE, n_min, pd, plt):
    # Cell 5: Carbon Intensity Loading
    df_ci = pd.read_csv(CI_FILE, parse_dates=["datetime"], index_col="datetime")
    # Resample to 1min and align with trace length
    df_ci = df_ci.resample("1min").ffill().reset_index(drop=True)
    ci_per_min = df_ci[CI_ZONE][:n_min].values  # gCO2/kWh

    _fig, _ax = plt.subplots(figsize=(10, 2))
    _ax.plot(ci_per_min)
    _ax.set_ylabel("gCO2/kWh")
    _ax.set_title(f"Carbon Intensity ({CI_ZONE})")
    _fig.tight_layout()
    _fig
    return (ci_per_min,)


@app.cell
def _(J_PER_KWH, ci_per_min, gammas, node_names, routing_arr, toks_min):
    # oSCI

    toks = toks_min[:, None] * routing_arr[None, :]
    E_kwh = toks * gammas[None, :] / J_PER_KWH
    osci = (gammas[None, :] * ci_per_min[:, None]) / J_PER_KWH  # gCO2/tok

    for _i, _n in enumerate(node_names):
        print(f"{_n}: kWh={E_kwh[:, _i].sum():,.1f}  "
              f"oSCI(mean)={osci[:, _i].mean():.6f} gCO2/tok")
    return E_kwh, osci, toks


@app.cell
def _(NODES, n_min, node_names, np, osci, toks):
    # SCI = oSCI + emboddied

    SECS_PER_YEAR = 365.25 * 24 * 3600
    week_secs = n_min * 60.0

    # Trace-derived per-node utilization
    tps_arr = np.array([NODES[n]["tps"] for n in node_names])
    _util = toks.sum(axis=0) / (tps_arr * week_secs)

    m_per_tok = np.zeros(len(node_names))
    for _i, _n in enumerate(node_names):
        _v = NODES[_n]
        # Always zero out embodied carbon if age >= lifespan
        if _v["age_yr"] < _v["lifespan_yr"]:
            _r_life = _v["tps"] * _util[_i] * _v["lifespan_yr"] * SECS_PER_YEAR
            m_per_tok[_i] = _v["te_kg"] * 1000.0 / _r_life
        print(f"{_n}: util={_util[_i]:.3f}  M={m_per_tok[_i]:.6f} gCO2/tok")

    sci = osci + m_per_tok[None, :]
    return (sci,)


@app.cell
def _(RESIDUAL_KG, capacity_min, hour_id, np, osci, toks):
    # rSCI = oSCI + residual

    def _cluster_load_proportional(toks, hour_id, capacity_min):
        # w ∝ hourly fleet load × cell tokens.
        hour_load_tok = np.bincount(hour_id, weights=toks.sum(axis=1))
        hour_load = hour_load_tok / capacity_min.sum()
        w = hour_load[hour_id][:, None] * toks
        return w / w.sum()

    def _peak_frac(toks, hour_id, capacity_min, frac):
        hour_load = np.bincount(hour_id, weights=toks.sum(axis=1))
        threshold = np.quantile(hour_load, 1.0 - frac)
        selected = (hour_load >= threshold)[hour_id]
        masked = toks * selected[:, None]
        return masked / masked.sum()

    STRATEGIES = {
        "load proportional":  lambda t, h, c: _cluster_load_proportional(t, h, c),
        "peak 10%": lambda t, h, c: _peak_frac(t, h, c, 0.10),
    #    "peak 50%": lambda t, h, c: _peak_frac(t, h, c, 0.50),
    }

    safe_toks = np.where(toks > 0, toks, 1.0)
    rsci = {}
    for _label, _fn in STRATEGIES.items():
        _w = _fn(toks, hour_id, capacity_min)
        _res = (_w * RESIDUAL_KG * 1000.0) / safe_toks
        rsci[_label] = osci + _res
        print(f"{_label:>22s}: reconciles to {(_res * toks).sum() / 1000.0:.2f} kg")
    return (rsci,)


@app.cell
def _(E_kwh, ci_per_min, node_names, osci, plt, rsci, sci):
    # Timeline comparison of metrics
    n_rows = 4 + len(rsci)
    _fig, _axes = plt.subplots(n_rows, 1, figsize=(7, 1.4 * n_rows), sharex=True)

    # Subplot 0: Carbon Intensity
    _axes[0].plot(ci_per_min, color='black', alpha=0.7)
    _axes[0].set_ylabel("CI\ngCO2/kWh")

    # Subplots 1-3: Active Power and standard SCI metrics
    # Fix: use _label instead of k
    Y_LIM_SCI = (0, max(sci.max(), max(v.max() for _label, v in rsci.items() if "peak 10%" not in _label)) * 1.1)

    for _i, _n in enumerate(node_names):
        _axes[1].plot(E_kwh[:, _i] * 60, label=_n)  # kWh/min -> kW
        _axes[2].plot(osci[:, _i],  label=_n)
        _axes[3].plot(sci[:, _i],   label=_n)

    _axes[1].set_ylabel("Active Power\nkW")
    _axes[2].set_ylabel("oSCI\ngCO2/tok")
    _axes[3].set_ylabel("SCI (M)\ngCO2/tok")

    # Subplots 4+: rSCI variants
    for _k, (_label, _arr) in enumerate(rsci.items()):
        _ax = _axes[4 + _k]
        for _i, _n in enumerate(node_names):
            _ax.plot(_arr[:, _i], label=_n)
        _ax.set_ylabel(f"rSCI\n[{_label}]")

    for i, _ax in enumerate(_axes):
        _ax.legend(loc="upper right", fontsize=8)
        _ax.grid(alpha=0.3)
        #if 1 < i < 5:
        #    _ax.set_ylim(Y_LIM_SCI)

    _fig.tight_layout()
    _fig
    return


@app.cell
def _(TOTAL_TPS, node_names, osci, plt, rsci, sci, toks_min):
    # Fleet utilization vs. Carbon Intensity (per strategy)
    _util_fleet = toks_min / (TOTAL_TPS * 60.0)
    panels = {"oSCI": osci, "SCI": sci, **{f"rSCI[{_k}]": _v for _k, _v in rsci.items() if "prop" in _k}}

    _fig, _axes = plt.subplots(1, len(panels), figsize=(3.5 * len(panels), 3.5), sharey=True)
    for _ax, (_name, _arr) in zip(_axes, panels.items()):
        for _i, _n in enumerate(node_names):
            _ax.scatter(_util_fleet, _arr[:, _i], s=2, alpha=0.15, label=_n)
        _ax.set_title(_name)
        _ax.set_xlabel("Fleet Utilization")
        _ax.set_xlim(0,1)
        _ax.grid(alpha=0.2)

    _axes[0].set_ylabel("gCO2 / token")
    _axes[0].legend(loc="upper left", fontsize=8, markerscale=4)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(RESIDUAL_KG, np, osci, plt, sci, toks):
    # ===== Reconciliation: what each metric captures vs the provider-reported total =====
    # All bars are computed on the same trace, fleet, and routing (throughput-weighted
    # upstream). The provider-reported total is the constructed top-down number
    # against which rSCI reconciles by construction; the residual RESIDUAL_KG carries
    # the non-operational share. We split the residual into:
    #   - IT embodied (the part SCI tries to model via M)
    #   - other overhead (PUE, FERA, S1, building embodied, S3 non-IT — everything
    #     else the bottom-up models miss).
    # Gaps relative to the provider bar are exactly what each metric structurally
    # misses.

    op_kg = float((osci * toks).sum() / 1000.0)
    sci_kg = float((sci * toks).sum() / 1000.0)
    it_embodied_kg = sci_kg - op_kg
    other_overhead_kg = RESIDUAL_KG - it_embodied_kg
    provider_kg = op_kg + RESIDUAL_KG  # = rSCI by construction (reconciliation identity)

    print(f"op (Scope-2 op)         = {op_kg:>7.2f} kg")
    print(f"IT embodied (SCI M)     = {it_embodied_kg:>7.2f} kg")
    print(f"other overhead (Δ − M)  = {other_overhead_kg:>7.2f} kg")
    print(f"provider total (= rSCI) = {provider_kg:>7.2f} kg")

    bars = [
        ("oSCI",     op_kg,  0.0,             0.0),
        ("SCI",      op_kg,  it_embodied_kg,  0.0),
        ("rSCI",     op_kg,  it_embodied_kg,  other_overhead_kg),
        ("provider", op_kg,  it_embodied_kg,  other_overhead_kg),
    ]
    _labels  = ["operational", "IT embodied", "other overhead"]
    _colors  = ["#4c72b0",     "#dd8452",     "#8c8c8c"]

    _fig, _ax = plt.subplots(figsize=(7, 4))
    _x = np.arange(len(bars))
    _bottoms = np.zeros(len(bars))
    for _ci, (_label, _color) in enumerate(zip(_labels, _colors)):
        _vals = np.array([_b[1 + _ci] for _b in bars])
        _ax.bar(_x, _vals, bottom=_bottoms, label=_label, color=_color, edgecolor="white")
        _bottoms = _bottoms + _vals
    _ax.set_xticks(_x)
    _ax.set_xticklabels([_b[0] for _b in bars])
    _ax.set_ylabel("attributed kgCO2e (week)")
    _ax.set_title("Reconciliation: what each metric captures vs the provider's top-down total")
    _ax.legend(loc="upper left", fontsize=9)
    _ax.grid(alpha=0.3, axis="y")

    # Annotate each bar with its total
    for _i, _b in enumerate(bars):
        _total = sum(_b[1:])
        _ax.text(_i, _total + provider_kg * 0.02, f"{_total:.0f} kg",
                 ha="center", fontsize=9)

    _fig.tight_layout()
    _fig
    return


if __name__ == "__main__":
    app.run()
