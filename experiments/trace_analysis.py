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
    _axes[0].plot(df["n_requests"])
    _axes[0].set_ylabel("n_requests")
    _axes[1].plot(df["context_tokens"])
    _axes[1].set_ylabel("context_tokens")
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

    _routing_arr = np.array([ROUTING[n] for n in node_names])
    toks = toks_min[:, None] * _routing_arr[None, :]
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
    _util = toks.sum(axis=0) / (tps * week_secs)

    m_per_tok = np.zeros(len(node_names))
    for _i, _n in enumerate(node_names):
        _v = NODES[_n]
        if not (ZERO_PAST_EL and _v["age_yr"] >= _v["lifespan_yr"]):
            _r_life = _v["tps"] * _util[_i] * _v["lifespan_yr"] * SECS_PER_YEAR
            m_per_tok[_i] = _v["te_kg"] * 1000.0 / _r_life
        print(f"{_n}: util={_util[_i]:.3f}  M={m_per_tok[_i]:.4f} gCO2/tok")

    sci = osci + m_per_tok[None, :]
    return (sci,)


@app.cell
def _(np):
    # Residual-allocation strategies. Each takes (toks, hour_id, capacity) →
    # weight array shape (n_min, n_nodes) summing to 1.
    RESIDUAL_KG = 200.0

    def _inv_load(toks, hour_id, capacity):
        # w ∝ hourly fleet load × cell tokens. Per-token residual ∝ hourly load.
        hour_load_tok = np.bincount(hour_id, weights=toks.sum(axis=1))
        hour_load = hour_load_tok / (capacity.sum() * 60.0)
        w = hour_load[hour_id][:, None] * toks
        return w / w.sum()

    def _peak_frac(toks, hour_id, capacity, frac):
        # Hard threshold: top `frac` busiest hours carry all the residual.
        hour_load = np.bincount(hour_id, weights=toks.sum(axis=1))
        threshold = np.quantile(hour_load, 1.0 - frac)
        selected = (hour_load >= threshold)[hour_id]
        masked = toks * selected[:, None]
        return masked / masked.sum()

    STRATEGIES = {
        "inv load":      lambda t, h, c: _inv_load(t, h, c),
        "peak 10%": lambda t, h, c: _peak_frac(t, h, c, 0.10),
        "peak 50%": lambda t, h, c: _peak_frac(t, h, c, 0.50),
    }
    return RESIDUAL_KG, STRATEGIES


@app.cell
def _(RESIDUAL_KG, STRATEGIES, capacity, hour_id, np, osci, toks):
    # rSCI = oSCI + residual. Reconciliation by construction (weights sum to 1).
    safe_toks = np.where(toks > 0, toks, 1.0)
    rsci = {}
    for _label, _fn in STRATEGIES.items():
        _res = (_fn(toks, hour_id, capacity) * RESIDUAL_KG * 1000.0) / safe_toks
        rsci[_label] = osci + _res
        print(f"{_label:>22s}: reconciles to {(_res * toks).sum() / 1000.0:.2f} kg "
              f"(target {RESIDUAL_KG:.2f})")
    return (rsci,)


@app.cell
def _(E_kwh, ci_per_min, node_names, osci, plt, rsci, sci):
    n_rows = 4 + len(rsci)
    _fig, _axes = plt.subplots(n_rows, 1, figsize=(10, 1.8 * n_rows), sharex=True)

    _axes[0].plot(ci_per_min)
    _axes[0].set_ylabel("CI\ngCO2/kWh")

    Y_LIM = (0,0.00019)

    for _i, _n in enumerate(node_names):
        _axes[1].plot(E_kwh[:, _i], label=_n)
        _axes[2].plot(osci[:, _i],  label=_n)
        _axes[3].plot(sci[:, _i],   label=_n)
    _axes[1].set_ylabel("active\nkWh / min")
    _axes[2].set_ylabel("oSCI\ngCO2/tok")
    _axes[2].set_ylim(Y_LIM)
    _axes[3].set_ylabel("SCI\ngCO2/tok")
    _axes[3].set_ylim(Y_LIM)

    for _k, (_label, _arr) in enumerate(rsci.items()):
        _ax = _axes[4 + _k]
        for _i, _n in enumerate(node_names):
            _ax.plot(_arr[:, _i], label=_n)
        _ax.set_ylabel(f"rSCI\n[{_label}]")
        if "peak" not in _label:
            _ax.set_ylim(Y_LIM)

    for _ax in _axes[1:]:
        _ax.legend(loc="upper right", fontsize=8)


    _fig.tight_layout()
    _fig
    return


@app.cell
def _(capacity, node_names, osci, plt, rsci, sci, toks_min):
    _util = toks_min / (capacity.sum() * 60.0)  # fleet utilization ∈ [0, 1]
    panels = {"oSCI": osci, "SCI": sci, **{f"rSCI[{k}]": v for k, v in rsci.items() if "peak 10%" not in k}}

    _fig, _axes = plt.subplots(1, len(panels), figsize=(3.0 * len(panels), 3.4), sharex=True, sharey=True)
    for _ax, (_name, _arr) in zip(_axes, panels.items()):
        for _i, _n in enumerate(node_names):
            _ax.scatter(_util, _arr[:, _i], s=3, alpha=0.25, label=_n)
        _ax.set_title(_name)
        _ax.set_xlabel("fleet utilization")
    _axes[0].set_ylabel("gCO2 / token")
    _axes[0].legend(loc="upper left", fontsize=8, markerscale=2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(capacity, hour_id, np, toks_min):
    SHIFTABLE_FRAC = 0.10

    shiftable_min = SHIFTABLE_FRAC * toks_min
    fixed_min = toks_min - shiftable_min

    # Water-filling: distribute the shiftable budget across off-peak hours so
    # the fleet load curve is flattened up to a level T. Avoids the failure
    # mode of greedy fill-quietest-first, which would create *new* peaks in
    # the previously-quiet hours and put the shiftable workload right back on
    # top of them. Closed-form: sort fixed_per_hour ascending; find the
    # smallest k such that T = (budget + Σ_{i≤k} fph_sorted[i]) / (k+1)
    # ≤ fph_sorted[k+1]. Then shifted_per_hour = max(T - fixed_per_hour, 0).
    fixed_per_hour = np.bincount(hour_id, weights=fixed_min)
    budget = float(shiftable_min.sum())
    fph_sorted = np.sort(fixed_per_hour)
    csum = np.cumsum(fph_sorted)
    T = (budget + csum[-1]) / len(fph_sorted)  # default: all hours lifted
    for _k in range(len(fph_sorted) - 1):
        _cand = (budget + csum[_k]) / (_k + 1)
        if _cand <= fph_sorted[_k + 1]:
            T = _cand
            break

    hour_cap = capacity.sum() * 60.0
    if T > hour_cap:
        print(f"WARN: water-fill T={T:,.0f} > hour_cap={hour_cap:,.0f} "
              "— fleet has no headroom to absorb shiftable budget")
        T = hour_cap
    shifted_per_hour = np.clip(T - fixed_per_hour, 0.0, None)
    shiftable_min_shifted = shifted_per_hour[hour_id] / 60.0

    print(f"water-fill T={T:,.0f} tok/hr  "
          f"budget={budget:,.0f}  filled={shifted_per_hour.sum():,.0f}  "
          f"hours used={(shifted_per_hour > 0).sum()}")
    return fixed_min, shiftable_min, shiftable_min_shifted


@app.cell
def _(
    RESIDUAL_KG,
    ROUTING,
    STRATEGIES,
    capacity,
    fixed_min,
    hour_id,
    node_names,
    np,
    osci,
    plt,
    sci,
    shiftable_min,
    shiftable_min_shifted,
):
    _routing_arr = np.array([ROUTING[n] for n in node_names])

    fixed_toks   = fixed_min[:, None]              * _routing_arr[None, :]
    shift_toks_b = shiftable_min[:, None]          * _routing_arr[None, :]
    shift_toks_s = shiftable_min_shifted[:, None]  * _routing_arr[None, :]
    toks_b = fixed_toks + shift_toks_b   # baseline scenario fleet tokens
    toks_s = fixed_toks + shift_toks_s   # shifted  scenario fleet tokens

    # oSCI / SCI per-token values depend only on γ and CI, not on token placement,
    # so the same `osci` / `sci` arrays apply to both scenarios.
    def _per_tok_under(toks_scenario):
        out = {"oSCI": osci, "SCI": sci}
        _safe = np.where(toks_scenario > 0, toks_scenario, 1.0)
        for _label, _fn in STRATEGIES.items():
            _w = _fn(toks_scenario, hour_id, capacity)
            out[f"rSCI[{_label}]"] = osci + (_w * RESIDUAL_KG * 1000.0) / _safe
        return out

    per_tok_b = _per_tok_under(toks_b)
    per_tok_s = _per_tok_under(toks_s)

    print(f"{'metric':>18s}   {'baseline':>10s}   {'shifted':>10s}   {'Δ':>7s}")
    labels, kg_b_list, kg_s_list = [], [], []
    for _name in per_tok_b:
        _kg_b = float((per_tok_b[_name] * shift_toks_b).sum() / 1000.0)
        _kg_s = float((per_tok_s[_name] * shift_toks_s).sum() / 1000.0)
        _delta = (_kg_s - _kg_b) / _kg_b * 100.0 if _kg_b > 0 else 0.0
        print(f"{_name:>18s}   {_kg_b:>8.2f}kg   {_kg_s:>8.2f}kg   {_delta:>+6.1f}%")
        labels.append(_name)
        kg_b_list.append(_kg_b)
        kg_s_list.append(_kg_s)

    # Reconciliation invariant: the residual portion (rSCI - oSCI) summed across
    # the fleet equals RESIDUAL_KG regardless of placement. The fleet oSCI total
    # *does* change with placement (CI varies over time).
    _r0 = list(STRATEGIES)[0]
    _resid_b = float(((per_tok_b[f"rSCI[{_r0}]"] - osci) * toks_b).sum() / 1000.0)
    _resid_s = float(((per_tok_s[f"rSCI[{_r0}]"] - osci) * toks_s).sum() / 1000.0)
    print(f"\nresidual portion (load_peak): baseline={_resid_b:.2f} kg  "
          f"shifted={_resid_s:.2f} kg  (both should equal RESIDUAL_KG = {RESIDUAL_KG:.1f})")

    x = np.arange(len(labels))
    w = 0.38
    _fig, _ax = plt.subplots(figsize=(10, 4))
    _ax.bar(x - w/2, kg_b_list, w, label="baseline")
    _ax.bar(x + w/2, kg_s_list, w, label="shifted")
    for _i, (_b, _s) in enumerate(zip(kg_b_list, kg_s_list)):
        _delta = (_s - _b) / _b * 100.0 if _b > 0 else 0.0
        _ax.text(_i, max(_b, _s), f"{_delta:+.0f}%", ha="center", va="bottom", fontsize=8)
    _ax.set_xticks(x)
    _ax.set_xticklabels(labels, rotation=15, ha="right")
    _ax.set_ylabel("kg CO2e attributed to shiftable workload")
    _ax.set_title("Counterfactual: shiftable workload bill, baseline vs trough-shifted")
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


if __name__ == "__main__":
    app.run()
