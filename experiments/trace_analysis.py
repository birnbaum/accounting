import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    return mdates, np, pd, plt


@app.cell
def _():
    TRACE_FILE = "data/AzureLLMInferenceTrace_conv_1week_minutely.csv"
    CI_FILE = "data/carbon_intensity_2024-05_azure_trace.csv"
    CI_ZONE = "US-CAL-CISO"

    # Single bare-metal DGX H100 node (8xH100). Full-node power basis (not GPU-only),
    # so the idle draw is a grounded quantity that lands in the capacity residual.
    TPS = 3000.0          # aggregate processing throughput, prefill+decode (tokens/s); ground with trace research
    PEAK_W = 10200.0      # node power at full load (NVIDIA DGX H100 max)
    IDLE_W = 2500.0       # node idle draw
    TE_KG = 2500.0        # embodied carbon of the node: 1312 kg for the 8-GPU HGX H100
                          # baseboard (NVIDIA PCF) + est. CPUs/memory/storage/NICs/PSU/cooling
    LIFESPAN_YR = 4.0     # SCI-spec amortization lifespan
    PUE = 1.2             # facility overhead, folded into the bottom-up model

    # Provider's top-down reported carbon per scope (illustrative). The bottom-up model
    # estimates only operational Scope-2, so reported-minus-operational is the residual;
    # residuals are DERIVED downstream once operational is known.
    S2_REPORTED = 80.0    # reported Scope-2 (kg); residual (=80-op) is dominated by idle draw oSCI omits
    S3_REPORTED = 20.0    # reported Scope-3 (kg): embodied hardware/buildings + upstream electricity (FERA)
    # beta = energy-driven fraction of each scope's residual (Sec 4); the rest is capacity-driven.
    # S2 residual ~90% idle (capacity) / ~10% energy-model error; S3 ~50/50 FERA (energy) vs embodied+buildings.
    BETA_S2 = 0.10
    BETA_S3 = 0.50

    SCALE = 57.0          # normalizes the fleet trace to one node; targets ~0.85 peak utilization
    J_PER_KWH = 3_600_000.0
    DAYS = 3              # window the trace to the first N days (None = full week)

    GAMMA = (PEAK_W - IDLE_W) / TPS  # marginal energy per processed token (J/tok)
    CAP_MIN = TPS * 60.0             # node token capacity per minute
    return (
        BETA_S2,
        BETA_S3,
        CAP_MIN,
        CI_FILE,
        CI_ZONE,
        DAYS,
        GAMMA,
        J_PER_KWH,
        LIFESPAN_YR,
        PUE,
        S2_REPORTED,
        S3_REPORTED,
        SCALE,
        TE_KG,
        TPS,
        TRACE_FILE,
    )


@app.cell
def _(DAYS, SCALE, TRACE_FILE, pd):
    df = pd.read_csv(TRACE_FILE)
    df["minute"] = pd.to_datetime(df["minute"])
    if DAYS is not None:
        df = df.iloc[: DAYS * 1440].reset_index(drop=True)  # first N days (minutely)
    t = df["minute"].dt.tz_localize(None)  # trace time axis (UTC, as recorded)
    # Total processed tokens/min (prefill+decode). Forward-pass compute is ~2N FLOPs per
    # token for both phases, so energy tracks context+generated; also the functional unit.
    toks = (df["context_tokens"] + df["generated_tokens"]).astype(float).values / SCALE

    context_toks = df["context_tokens"].astype(float).values / SCALE  # tokens served per minute
    generated_toks = df["generated_tokens"].astype(float).values / SCALE  # tokens served per minute

    hour_id = ((df["minute"] - df["minute"].iloc[0]).dt.total_seconds() // 3600).astype(int).values
    return context_toks, generated_toks, hour_id, t, toks


@app.cell
def _(CAP_MIN, SCALE, context_toks, generated_toks, plt, t):
    # Node utilization at the chosen SCALE
    _fig, _ax = plt.subplots(figsize=(10, 2))
    _ax.plot(t, context_toks / CAP_MIN)
    _ax.plot(t, generated_toks / CAP_MIN)
    _ax.set(ylim=(0, 1), ylabel="node utilization", title=f"Node Utilization (Scale={SCALE})")
    _fig.autofmt_xdate(); _fig.tight_layout()
    _fig
    return


@app.cell
def _(CI_FILE, CI_ZONE, pd, t):
    # CAISO carbon by UTC (weekday, hour), mapped onto the trace's UTC timestamps.
    # Trace (2024) and CI file (2024) share no dates, so align on recurring structure.
    _raw = pd.read_csv(CI_FILE, parse_dates=["datetime"])
    _ci = pd.Series(_raw[CI_ZONE].values, index=_raw["datetime"].dt.tz_localize(None))
    _prof = _ci.groupby([_ci.index.dayofweek, _ci.index.hour]).mean()
    ci_per_min = _prof.reindex(pd.MultiIndex.from_arrays([t.dt.dayofweek, t.dt.hour])).to_numpy()
    return (ci_per_min,)


@app.cell
def _(GAMMA, J_PER_KWH, PUE, ci_per_min, toks):
    # oSCI counts only the marginal energy decode adds above idle, scaled by PUE and
    # the hourly grid intensity. Idle draw between bursts is excluded by construction.
    E_kwh = toks * GAMMA / J_PER_KWH                     # IT energy per minute (no PUE)
    osci = GAMMA * PUE * ci_per_min / J_PER_KWH          # gCO2/tok (varies with grid CI)
    print(f"total kWh={E_kwh.sum():,.1f}  oSCI(mean)={osci.mean():.6f} gCO2/tok  "
          f"op={(osci * toks).sum() / 1000:.1f} kg")
    return E_kwh, osci


@app.cell
def _(BETA_S2, BETA_S3, S2_REPORTED, S3_REPORTED, osci, toks):
    # Residuals = provider's top-down reported scope totals minus the bottom-up model.
    # Only operational Scope-2 is modeled, so the S2 residual = reported - operational, and
    # the whole S3 report is residual. Regroup by driver (Sec 4) via beta: energy-driven
    # (flat) vs capacity-driven (peak-attributed).
    _op_kg = (osci * toks).sum() / 1000.0
    RESIDUAL_S2 = S2_REPORTED - _op_kg   # idle draw oSCI omits + energy-model error
    RESIDUAL_S3 = S3_REPORTED            # embodied/buildings + FERA (bottom-up models none of S3)
    RESIDUAL_EN = BETA_S2 * RESIDUAL_S2 + BETA_S3 * RESIDUAL_S3
    RESIDUAL_CAP = (1 - BETA_S2) * RESIDUAL_S2 + (1 - BETA_S3) * RESIDUAL_S3
    print(f"op={_op_kg:.1f}  S2res={RESIDUAL_S2:.1f}  S3res={RESIDUAL_S3:.1f}  "
          f"EN={RESIDUAL_EN:.1f} CAP={RESIDUAL_CAP:.1f}  provider={_op_kg + RESIDUAL_S2 + RESIDUAL_S3:.1f}")
    return RESIDUAL_CAP, RESIDUAL_EN, RESIDUAL_S2, RESIDUAL_S3


@app.cell
def _(LIFESPAN_YR, TE_KG, TPS, osci, toks):
    # SCI = oSCI + embodied, amortized over the device lifetime (age-independent; a
    # fair SCI implementation, since zeroing depreciated hardware is the sunk-carbon
    # fallacy).
    SECS_PER_YEAR = 365.25 * 24 * 3600
    _util = toks.sum() / (TPS * len(toks) * 60.0)
    _r_life = TPS * _util * LIFESPAN_YR * SECS_PER_YEAR  # tokens over the lifetime
    m_per_tok = TE_KG * 1000.0 / _r_life
    sci = osci + m_per_tok
    print(f"util={_util:.3f}  M={m_per_tok:.6f} gCO2/tok")
    return m_per_tok, sci


@app.cell
def _(m_per_tok):
    m_per_tok*1000000
    return


@app.cell
def _(E_kwh, RESIDUAL_CAP, RESIDUAL_EN, hour_id, np, osci, toks):
    # rSCI = oSCI + residual, allocated by physical driver (Sec 4):
    #   energy-driven residual -> energy-share weight (flat per token)
    #   capacity-driven residual -> peak-attribution weight, a temporal Shapley proxy.
    #       Per-token charge ~ (hourly load)^PEAK_P: convex in load, so near-peak
    #       tokens pay disproportionately more than trough tokens (P=1 is linear).
    PEAK_P = 2.0
    _safe = np.where(toks > 0, toks, 1.0)

    _wE = E_kwh / E_kwh.sum()
    res_e = _wE * RESIDUAL_EN * 1000.0 / _safe  # gCO2/tok (flat)

    _hload = np.bincount(hour_id, weights=toks)[hour_id]
    _wK = _hload**PEAK_P * toks
    _wK = _wK / _wK.sum()
    res_k = _wK * RESIDUAL_CAP * 1000.0 / _safe  # gCO2/tok (rises with load)

    rsci = osci + res_e + res_k
    _kg = ((res_e + res_k) * toks).sum() / 1000.0
    print(f"rSCI residual reconciles to {_kg:.2f} kg (energy-share + peak-attribution)")
    return res_e, res_k


@app.cell
def _(
    RESIDUAL_S2,
    RESIDUAL_S3,
    ci_per_min,
    hour_id,
    mdates,
    np,
    osci,
    plt,
    res_e,
    res_k,
    sci,
    t,
    toks,
):
    def _hourly(arr):
        # Token-weighted hourly mean = the metric's reporting cadence (grid CI is hourly).
        _c = np.bincount(hour_id, weights=arr * toks)
        _k = np.bincount(hour_id, weights=toks)
        return (_c / np.where(_k > 0, _k, 1.0))[hour_id]
    _op = _hourly(osci)
    _C_OP, _C_E, _C_K = "#3b6ba5", "#9ecae1", "#c44e52"  # operational / energy / capacity
    _C_TD2, _C_TD3 = "#b0b0b0", "#6b6b6b"                # top-down Scope-2 / Scope-3 greys

    # Aggregate attributed carbon (kg) for the right-column reconciliation gauges.
    _kg = lambda arr: float((arr * toks).sum() / 1000.0)
    _op_kg, _emb_kg = _kg(osci), _kg(sci - osci)   # _emb = SCI's per-server M
    _e_kg, _k_kg = _kg(res_e), _kg(res_k)
    _prov_kg = _op_kg + _e_kg + _k_kg              # provider top-down total (= rSCI)

    # Left column = timelines (shared x); right column = gauges on metric rows only.
    _fig = plt.figure(figsize=(6, 6))
    _gs = _fig.add_gridspec(4, 2, width_ratios=[5, 1], wspace=0.05)
    _axes = [_fig.add_subplot(_gs[0, 0])]
    _axes += [_fig.add_subplot(_gs[_r, 0], sharex=_axes[0]) for _r in range(1, 4)]

    _l_load, = _axes[0].plot(t, toks / 1e6, color="darksalmon", lw=1)  # load drives everything downstream
    _axes[0].set_ylabel("load\nMtok/min")
    _axes[0].set_ylim([0, .24])
    _ax0b = _axes[0].twinx()
    _l_ci, = _ax0b.plot(t, ci_per_min, color="black", alpha=0.8, lw=1)
    _ax0b.set_ylabel("carbon intensity\ngCO$_2$/kWh")
    _ax0b.set_ylim([0, 270])
    _ax0b.legend([_l_load, _l_ci], ["load", "carbon intensity"], loc="upper left", frameon=False, bbox_to_anchor=(-0.01, 1.15), ncol=2, columnspacing=1, handletextpad=0.5)
    _ax0b.tick_params(labelsize=9)

    _axes[0].spines[["top"]].set_visible(False)
    _ax0b.spines[["top"]].set_visible(False)

    # All three metrics reported per token, as stacked areas so the coverage ladder
    # oSCI < SCI < rSCI is visible.
    _axes[1].stackplot(t, _op * 1e6, colors=[_C_OP], labels=["operational"], alpha=0.95)
    _axes[2].stackplot(t, _op * 1e6, _hourly(sci - osci) * 1e6,
                       colors=[_C_OP, _C_K], labels=["operational", "embodied"], alpha=0.95)
    _axes[1].set_ylabel("oSCI\ngCO$_2$/Mtok")
    _axes[2].set_ylabel("SCI\ngCO$_2$/Mtok")

    # rSCI: operational + energy residual (flat) + capacity residual (rises with load).
    _axes[3].stackplot(
        t, _op * 1e6, _hourly(res_e) * 1e6, _hourly(res_k) * 1e6,
        labels=["operational", "energy-driven residual", "capacity-driven residual"],
        colors=[_C_OP, _C_E, _C_K], alpha=0.95)
    _axes[3].set_ylabel("rSCI\ngCO$_2$/Mtok")

    for _ax in _axes:
        _ax.grid(alpha=0.3)
    for _ax in _axes[:-1]:
        _ax.tick_params(labelbottom=False)  # dates only on the bottom row

    # x-axis: one tick per day at 00:00, labelled by weekday, unrotated.
    _axes[-1].set_xlim(t.min(), t.max())  # clip padding so only interior midnights tick
    _axes[-1].xaxis.set_major_locator(mdates.DayLocator())
    _axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%a"))
    for _lbl in _axes[-1].get_xticklabels():
        _lbl.set_rotation(0); _lbl.set_ha("center")

    # Reconciliation gauges: bottom-up captured (Agg., left, in metric colours) vs the
    # provider's top-down report (Top-down, right). The report differentiates Scope 2 vs 3
    # (two greys) but NOT operational vs residual within them. Only rSCI reaches it.
    _captured = {
        1: [(_op_kg, _C_OP)],                                    # oSCI: operational only
        2: [(_op_kg, _C_OP), (_emb_kg, _C_K)],                   # SCI: + embodied M
        3: [(_op_kg, _C_OP), (_e_kg, _C_E), (_k_kg, _C_K)],      # rSCI: full
    }
    _td = [(_op_kg + RESIDUAL_S2, _C_TD2, "S2"), (RESIDUAL_S3, _C_TD3, "S3")]  # reported scopes
    for _r in (1, 2, 3):
        _bax = _fig.add_subplot(_gs[_r, 1])
        _bottom = 0.0
        for _val, _col in _captured[_r]:
            _bax.bar(0, _val, bottom=_bottom, width=0.8, color=_col, edgecolor="white", linewidth=0.4)
            _bottom += _val
        _bottom = 0.0
        for _val, _col, _lab in _td:
            _bax.bar(1, _val, bottom=_bottom, width=0.8, color=_col)
            _bax.text(1, _bottom + _val / 2, _lab, ha="center", va="center", fontsize=9, weight='bold', color="white")
            _bottom += _val
        _bax.spines[["top", "left"]].set_visible(False)
        _bax.yaxis.tick_right()
        _bax.yaxis.set_label_position("right")
        _bax.set_ylabel("Total carbon\nkg CO$_2$")
        _bax.set_xlim(-0.6, 1.6)
        _bax.set_ylim(0, _prov_kg * 1.05)
        _bax.set_xticks([0, 1] if _r == 3 else [])
        _bax.set_yticks([0, 50, 100])
        _bax.tick_params(labelsize=9)
    _fig.axes[-1].set_xticklabels(["Agg.", "Top\ndown"], fontsize=10)

    for _ax in _axes:
        _ax.tick_params(labelsize=9)

    for _ax in _axes[1:]:
        _ax.set_ylim(0, 500)
        _ax.spines[["top", "right"]].set_visible(False)

    _axes[1].legend(loc="upper left", frameon=False, ncols=1, bbox_to_anchor=(-0.01, 1), columnspacing=1, handletextpad=0.3)
    _axes[2].legend(loc="upper left", frameon=False, ncols=1, bbox_to_anchor=(-0.01, 1), columnspacing=1, handletextpad=0.3)
    _h, _l = _axes[3].get_legend_handles_labels()
    _order = [0,2,1]
    _axes[3].legend([_h[i] for i in _order],[_l[i] for i in _order], loc="upper left", frameon=False, ncols=2, bbox_to_anchor=(-0.01, 1.2), columnspacing=-5.2, handletextpad=0.3)

    _fig.align_ylabels()
    _fig.tight_layout()
    _fig.savefig("paper/figures/sec5_example.pdf", bbox_inches="tight")
    _fig
    return


if __name__ == "__main__":
    app.run()
