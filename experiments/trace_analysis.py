import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from pathlib import Path
    import matplotlib.pyplot as plt

    return pd, plt


@app.cell
def _(pd):
    df = pd.read_csv("data/AzureLLMInferenceTrace_conv_1week_minutely.csv")
    df.head(2)
    return (df,)


@app.cell
def _(df, plt):
    print(df.describe())

    fig, axes = plt.subplots(2, 1, figsize=(10, 4), sharex=True)

    axes[0].plot(df["n_requests"])
    axes[0].set_ylabel("n_requests")

    axes[1].plot(df["context_tokens"])
    axes[1].set_ylabel("context_tokens")

    fig.tight_layout()
    fig
    return


@app.cell
def _(pd, plt):
    df_ci = pd.read_csv("data/carbon_intensity_2026-04.csv", parse_dates=["datetime"], index_col="datetime")
    df_ci = df_ci.resample("1min").ffill().reset_index(drop=True)
    _fig, _ax = plt.subplots(figsize=(10, 2))
    df_ci.plot(ax=_ax)
    _fig
    return (df_ci,)


@app.cell
def _(df, plt):
    _fig, _ax = plt.subplots(figsize=(10,2))
    (df["context_tokens"] / 60 / 9100 / 15).plot(ax=_ax)
    _ax.set(ylim=(0,1))
    _fig
    return


@app.cell
def _():
    # Toy fleet: 2 nodes, both 8x TP.
    # DGX A100: 8xA100, ~3000 tok/s prefill (70B bf16, TP=8), 6.5 kW peak, 1.6 kW idle.
    # DGX H100: 8xH100, ~6100 tok/s prefill (70B bf16, TP=8), 10.2 kW peak, 2.5 kW idle.
    # Sources: NVIDIA DGX-A100/H100 datasheets. Marginal energy per prefill token
    # gamma = (peak - idle) / throughput (J/tok). oSCI uses marginal active only.
    nodes = {
        "DGX A100": {"tps": 3000.0, "peak_w": 6500.0, "idle_w": 1600.0},
        "DGX H100": {"tps": 6100.0, "peak_w": 10200.0, "idle_w": 2500.0},
    }
    for _n, _v in nodes.items():
        _v["gamma_j_per_tok"] = (_v["peak_w"] - _v["idle_w"]) / _v["tps"]

    total_tps = sum(v["tps"] for v in nodes.values())
    routing = {n: v["tps"] / total_tps for n, v in nodes.items()}
    SCALE = 15.0
    J_PER_KWH = 3_600_000.0
    return J_PER_KWH, SCALE, nodes, routing


@app.cell
def _(J_PER_KWH, SCALE, df, df_ci, nodes, pd, plt, routing):
    # oSCI: per-minute operational footprint from marginal electricity only.
    # Tokens scaled by 1/SCALE to fit fleet capacity; throughput-weighted routing
    # splits tokens across A100 / H100; per-minute mass = sum_g (gamma_g * tok_g) * CI / J_PER_KWH.
    toks_min = df["context_tokens"].astype(float).values / SCALE
    gamma_avg = sum(routing[n] * nodes[n]["gamma_j_per_tok"] for n in nodes)
    active_kwh_min = gamma_avg * toks_min / J_PER_KWH  # kWh per minute (fleet)
    ci_per_min = df_ci["europe-west1"][:len(active_kwh_min)]      # gCO2 per kWh
    g_per_min = active_kwh_min * ci_per_min      # gCO2 per minute

    R_total = float(toks_min.sum())
    osci_g_per_tok = float(g_per_min.sum()) / R_total
    kg_total = float(g_per_min.sum()) / 1000.0
    print(f"week total context tokens (scaled): {R_total:,.0f}")
    print(f"fleet active energy (week):         {active_kwh_min.sum():,.1f} kWh")
    print(f"oSCI (avg over week):               {osci_g_per_tok:.4f} gCO2 / context-token")
    print(f"total operational CO2e (week):      {kg_total:,.2f} kg")

    out = pd.DataFrame({"minute": range(len(active_kwh_min)), "kg_per_min": g_per_min / 1000.0,
                        "ci": ci_per_min, "active_kwh": active_kwh_min})
    _fig, _axes = plt.subplots(3, 1, figsize=(10, 5), sharex=True)
    _axes[0].plot(out["minute"], out["active_kwh"]); _axes[0].set_ylabel("kWh / min (active)")
    _axes[1].plot(out["minute"], out["ci"]);          _axes[1].set_ylabel("CI gCO2/kWh")
    _axes[2].plot(out["minute"], out["kg_per_min"]);  _axes[2].set_ylabel("oSCI kg / min")
    _fig.tight_layout()
    _fig
    return


if __name__ == "__main__":
    app.run()
