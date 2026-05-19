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
def _():
    """
    Toy fleet: 2 DGX-class nodes, both 8x TP, serving the Azure LLM inference trace.

    Throughput numbers are 70B-bf16 prefill with TP=8.
    Peak/idle power from NVIDIA DGX A100 / DGX H100 datasheets.
    TE (kgCO2e) is a bounded estimate:
      - A100: Falk 2025 8x A100 SXM ~1021 kgCO2e + ~3x chassis/board/CPU/RAM multiplier.
      - H100: NVIDIA HGX H100 PCF (1312 kgCO2e baseboard) + ~3x chassis multiplier.
    age_yr / lifespan_yr feed the SCI M-term; A100 past EL is the Bashir sunk-carbon case.
    """
    NODES = {
        "DGX A100": {"tps": 3000.0, "peak_w": 6500.0,  "idle_w": 1600.0,
                     "te_kg": 3000.0, "age_yr": 6.0, "lifespan_yr": 6.0},
        "DGX H100": {"tps": 6100.0, "peak_w": 10200.0, "idle_w": 2500.0,
                     "te_kg": 5000.0, "age_yr": 0.0, "lifespan_yr": 6.0},
    }
    for _n, _v in NODES.items():
        _v["gamma_j_per_tok"] = (_v["peak_w"] - _v["idle_w"]) / _v["tps"]

    TOTAL_TPS = sum(v["tps"] for v in NODES.values())
    ROUTING = {n: v["tps"] / TOTAL_TPS for n, v in NODES.items()}

    SCALE = 15.0          # divide raw trace tokens by this to fit fleet capacity
    J_PER_KWH = 3_600_000.0
    return J_PER_KWH, NODES, ROUTING, SCALE


@app.cell
def _(SCALE, pd):
    df = pd.read_csv("data/AzureLLMInferenceTrace_conv_1week_minutely.csv")
    df["minute"] = pd.to_datetime(df["minute"])
    toks_min = df["context_tokens"].astype(float).values / SCALE
    # hour-of-trace index per minute row — drives hour-aggregated allocation rules.
    hour_id = ((df["minute"] - df["minute"].iloc[0]).dt.total_seconds() // 3600).astype(int).values
    n_min = len(df)
    return df, hour_id, n_min, toks_min


@app.cell
def _(df, plt):
    # Raw request trace (sanity).
    _fig, _axes = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    _axes[0].plot(df["n_requests"]);     _axes[0].set_ylabel("n_requests")
    _axes[1].plot(df["context_tokens"]); _axes[1].set_ylabel("context_tokens")
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(df, plt):
    # Fleet utilization at the chosen SCALE.
    _fig, _ax = plt.subplots(figsize=(10, 2))
    (df["context_tokens"] / 60 / 9100 / 15).plot(ax=_ax)
    _ax.set(ylim=(0, 1), ylabel="fleet utilization")
    _fig
    return


@app.cell
def _(n_min, pd, plt):
    df_ci = pd.read_csv("data/carbon_intensity_2026-05_10d.csv",
                        parse_dates=["datetime"], index_col="datetime")
    df_ci = df_ci.resample("1min").ffill().reset_index(drop=True)
    ci_per_min = df_ci["US-CAL-CISO"][:n_min].values  # gCO2/kWh

    _fig, _ax = plt.subplots(figsize=(10, 2))
    df_ci.plot(ax=_ax)
    _fig
    return (ci_per_min,)


@app.cell
def _(J_PER_KWH, NODES, ROUTING, ci_per_min, np, toks_min):
    node_names = list(NODES.keys())
    gammas = np.array([NODES[n]["gamma_j_per_tok"] for n in node_names])
    capacity = np.array([NODES[n]["tps"] * 60.0 for n in node_names])  # tok/min/node

    routing_arr = np.array([ROUTING[n] for n in node_names])
    toks = toks_min[:, None] * routing_arr[None, :]
    E_kwh = toks * gammas[None, :] / J_PER_KWH
    osci = (gammas[None, :] * ci_per_min[:, None]) / J_PER_KWH  # gCO2/tok

    for _i, _n in enumerate(node_names):
        print(f"{_n}: kWh={E_kwh[:, _i].sum():,.1f}  "
              f"oSCI(mean)={osci[:, _i].mean():.4f} gCO2/tok")
    return E_kwh, capacity, node_names, osci, toks


@app.cell
def _(NODES, n_min, node_names, np, osci, toks):
    ZERO_PAST_EL = True
    SECS_PER_YEAR = 365.25 * 24 * 3600
    week_secs = n_min * 60.0

    # Trace-derived per-node utilization keeps R_lifetime consistent if SCALE changes.
    # Replace with a fixed constant (e.g. 0.638) for a fixed-utilization assumption.
    tps = np.array([NODES[n]["tps"] for n in node_names])
    util = toks.sum(axis=0) / (tps * week_secs)

    m_per_tok = np.zeros(len(node_names))
    for _i, _n in enumerate(node_names):
        _v = NODES[_n]
        if not (ZERO_PAST_EL and _v["age_yr"] >= _v["lifespan_yr"]):
            _r_life = _v["tps"] * util[_i] * _v["lifespan_yr"] * SECS_PER_YEAR
            m_per_tok[_i] = _v["te_kg"] * 1000.0 / _r_life
        print(f"{_n}: util={util[_i]:.3f}  M={m_per_tok[_i]:.4f} gCO2/tok")

    sci = osci + m_per_tok[None, :]
    return (sci,)


@app.cell
def _(capacity, hour_id, np, osci, toks):
    RESIDUAL_KG = 200.0

    def _load_peak(toks):
        # w ∝ hourly fleet load × cell tokens. Per-token residual ∝ hourly load.
        hour_load_tok = np.bincount(hour_id, weights=toks.sum(axis=1))
        hour_load = hour_load_tok / (capacity.sum() * 60.0)
        w = hour_load[hour_id][:, None] * toks
        return w / w.sum()

    def _peak_hour(toks, top_frac):
        # Hard threshold: top `top_frac` busiest hours carry all the residual.
        hour_load = np.bincount(hour_id, weights=toks.sum(axis=1))
        threshold = np.quantile(hour_load, 1.0 - top_frac)
        selected = (hour_load >= threshold)[hour_id]
        masked = toks * selected[:, None]
        return masked / masked.sum()

    STRATEGIES = {
        "load_peak":      lambda t: _load_peak(t),
        "peak (top 10%)": lambda t: _peak_hour(t, 0.10),
        "peak (top 50%)": lambda t: _peak_hour(t, 0.50),
    }

    safe_toks = np.where(toks > 0, toks, 1.0)
    rsci = {}
    for _label, _fn in STRATEGIES.items():
        _res = (_fn(toks) * RESIDUAL_KG * 1000.0) / safe_toks
        rsci[_label] = osci + _res
        print(f"{_label:>22s}: reconciles to {(_res * toks).sum() / 1000.0:.2f} kg "
              f"(target {RESIDUAL_KG:.2f})")
    return (rsci,)


@app.cell
def _(E_kwh, ci_per_min, node_names, osci, plt, rsci, sci):
    n_rows = 4 + len(rsci)
    fig, axes = plt.subplots(n_rows, 1, figsize=(10, 1.8 * n_rows), sharex=True)

    axes[0].plot(ci_per_min)
    axes[0].set_ylabel("CI\ngCO2/kWh")

    for _i, _n in enumerate(node_names):
        axes[1].plot(E_kwh[:, _i], label=_n)
        axes[2].plot(osci[:, _i],  label=_n)
        axes[3].plot(sci[:, _i],   label=_n)
    axes[1].set_ylabel("active\nkWh / min")
    axes[2].set_ylabel("oSCI\ngCO2/tok")
    axes[3].set_ylabel("SCI\ngCO2/tok")

    for _k, (_label, _arr) in enumerate(rsci.items()):
        _ax = axes[4 + _k]
        for _i, _n in enumerate(node_names):
            _ax.plot(_arr[:, _i], label=_n)
        _ax.set_ylabel(f"rSCI\n[{_label}]")

    for _ax in axes[1:]:
        _ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig
    return


if __name__ == "__main__":
    app.run()
