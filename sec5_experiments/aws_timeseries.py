import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    # AWS top-down vs bottom-up emissions — time series (Dec 2025 .. May 2026).
    #
    # Aligns provider-reported emissions from CCFT (monthly_carbon_emissions.csv)
    # with bottom-up CUR usage (aws/cur_raw/BILLING_PERIOD=YYYY-MM/). Earlier
    # months had a promotional credit and an unstable usage profile, so the
    # reporting window starts at 2025-12 (6 months through 2026-05).
    from pathlib import Path

    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    REPO = Path(__file__).resolve().parents[1]
    CUR_DIR = REPO / "aws" / "cur_raw"
    EMISSIONS_CSV = REPO / "aws" / "monthly_carbon_emissions.csv"

    REPORT_FROM = "2025-12"  # inclusive; 6-month window ends at 2026-05

    # The whole report is Frankfurt-only. Emissions: keep Frankfurt (the other
    # reported regions are zero noise). Spend: keep Frankfurt PLUS "(global)" —
    # region-less global-tier services (public IPv4, data transfer, Route 53)
    # that back the Frankfurt workload; only the foreign-region noise is dropped.
    FRANKFURT = "Europe (Frankfurt)"
    REGION_KEEP = {FRANKFURT, "(global)"}
    return (
        CUR_DIR,
        EMISSIONS_CSV,
        FRANKFURT,
        Patch,
        REGION_KEEP,
        REPORT_FROM,
        np,
        pd,
        plt,
        pq,
    )


@app.cell
def _(CUR_DIR, pd, pq):
    # Load bottom-up CUR usage from the per-billing-period parquet snapshots.
    KEEP_COLS = [
        "bill_billing_period_start_date",
        "line_item_product_code",
        "line_item_line_item_type",
        "line_item_usage_type",
        "line_item_usage_amount",
        "line_item_unblended_cost",
        "product_location",
        "product_instance_type",
        "pricing_unit",
    ]

    def latest_snapshot_files(billing_period_dir):
        # AWS writes multiple incremental snapshots per billing period;
        # only the lexicographically last one (latest timestamp) is complete.
        snapshots = sorted(d for d in billing_period_dir.iterdir() if d.is_dir())
        if not snapshots:
            return []
        return list(snapshots[-1].glob("*.snappy.parquet"))

    def load_cur_month(parquet_path):
        t = pq.read_table(parquet_path, columns=KEEP_COLS)
        df = t.to_pandas()
        df["usage_month"] = pd.to_datetime(
            df["bill_billing_period_start_date"]
        ).dt.strftime("%Y-%m")
        return df

    billing_period_dirs = sorted(CUR_DIR.glob("BILLING_PERIOD=*"))
    files = [f for d in billing_period_dirs for f in latest_snapshot_files(d)]
    cur_raw = pd.concat([load_cur_month(p) for p in files], ignore_index=True)
    cur_raw.shape, sorted(cur_raw["usage_month"].unique())
    return (cur_raw,)


@app.cell
def _(REGION_KEEP, REPORT_FROM, cur_raw):
    # Roll CUR services up into the same buckets the carbon CSV uses
    # (AmazonEC2 / AmazonS3 / Other) so the two sources can be merged on service.
    def roll_up_service(code: str) -> str:
        if code == "AmazonEC2":
            return "AmazonEC2"
        if code == "AmazonS3":
            return "AmazonS3"
        return "Other"

    REGION_RENAME = {
        "EU (Frankfurt)": "Europe (Frankfurt)",
        "EU (Stockholm)": "Europe (Stockholm)",
        "EU (Ireland)": "Europe (Ireland)",
        "EU (London)": "Europe (London)",
        "EU (Paris)": "Europe (Paris)",
        "EU (Milan)": "Europe (Milan)",
        "EU (Spain)": "Europe (Spain)",
        "EU (Zurich)": "Europe (Zurich)",
        "Any": "(global)",
    }
    cur = cur_raw[cur_raw["usage_month"] >= REPORT_FROM].copy()
    cur["service"] = cur["line_item_product_code"].map(roll_up_service)
    cur["region"] = (
        cur["product_location"].fillna("(global)").replace(REGION_RENAME)
    )
    # Frankfurt-only report: keep Frankfurt + region-less "(global)" services,
    # drop the foreign-region noise (Stockholm, N. Virginia).
    cur = cur[cur["region"].isin(REGION_KEEP)].copy()

    cur_monthly = (
        cur.groupby(["usage_month", "service", "region"], as_index=False)
        .agg(
            usage_amount=("line_item_usage_amount", "sum"),
            unblended_cost=("line_item_unblended_cost", "sum"),
            line_items=("line_item_product_code", "size"),
        )
        .sort_values(["usage_month", "service", "region"])
    )
    cur_monthly.head(20)
    return cur, cur_monthly


@app.cell
def _(EMISSIONS_CSV, FRANKFURT, REPORT_FROM, pd):
    # Top-down provider-reported emissions, restricted to the reporting window
    # and to Frankfurt (the other reported regions carry zero emissions).
    emissions_full = pd.read_csv(EMISSIONS_CSV)
    emissions = emissions_full[
        (emissions_full["usage_month"] >= REPORT_FROM)
        & (emissions_full["region"] == FRANKFURT)
    ].copy()
    emissions.head()
    return (emissions,)


@app.cell
def _(cur_monthly, emissions, pd):
    # Outer join of top-down emissions and bottom-up CUR, keyed on the shared
    # (month, service, region) grain. `_merge` flags which rows exist on each side.
    merged = pd.merge(
        emissions,
        cur_monthly,
        on=["usage_month", "service", "region"],
        how="outer",
        indicator=True,
    )
    merged["_merge"].value_counts()
    return (merged,)


@app.cell
def _(Patch, cur, emissions, np, pd, plt):
    # Paper figure: (a) reported emissions, Scope 2 (solid) + Scope 3 (striped)
    # by service in kg CO2e; (b) spend by service in USD. Same EC2/Other split in
    # both; AmazonS3 is ~0 and folded away. Frankfurt-only from upstream cells.
    SERVICE_ORDER = ["AmazonEC2", "Other"]
    COLOR = {"AmazonEC2": "#4C72B0", "Other": "#DD8452"}
    LABEL = {"AmazonEC2": "EC2", "Other": "Other"}

    def _pivot(df, col, scale=1.0):
        return (
            df.pivot_table(index="usage_month", columns="service", values=col,
                           aggfunc="sum", fill_value=0.0)
            .reindex(columns=SERVICE_ORDER, fill_value=0.0)
            .sort_index() * scale
        )

    s2 = _pivot(emissions, "total_scope_2_lbm_emissions_value", 1000.0)
    s3 = _pivot(emissions, "total_scope_3_lbm_emissions_value", 1000.0)
    spend = _pivot(cur[cur["line_item_line_item_type"] == "Usage"], "line_item_unblended_cost")

    _x = np.arange(len(s2.index))
    _labels = [pd.to_datetime(m).strftime("%b\n%Y") for m in s2.index]
    fig_paper, (ax_em, ax_sp) = plt.subplots(2, 1, figsize=(6, 5), sharex=True)

    # (a) bottom to top per month: EC2 S2, EC2 S3, Other S2, Other S3.
    _bottom = np.zeros(len(_x))
    for _svc in SERVICE_ORDER:
        for _piv, _hatch in ((s2, None), (s3, "//")):
            ax_em.bar(_x, _piv[_svc], 0.6, bottom=_bottom, color=COLOR[_svc],
                      hatch=_hatch, edgecolor="white" if _hatch else "none")
            _bottom = _bottom + _piv[_svc].to_numpy()
    ax_em.set_ylabel("LBM emissions (kg CO$_2$e)")
    ax_em.set_title("(a) AWS reported emissions: Scope 2 vs Scope 3, by service")
    ax_em.legend(
        handles=[Patch(facecolor=COLOR[s], label=LABEL[s]) for s in SERVICE_ORDER]
        + [Patch(facecolor="#bbb", label="Scope 2"),
           Patch(facecolor="#bbb", hatch="//", edgecolor="white", label="Scope 3")],
        ncol=2, frameon=False, loc="upper center", bbox_to_anchor=(0.55, 1)
    )

    # (b) spend, one stacked bar per month by service.
    _bottom = np.zeros(len(_x))
    for _svc in SERVICE_ORDER:
        ax_sp.bar(_x, spend[_svc], 0.6, bottom=_bottom, color=COLOR[_svc], label=LABEL[_svc])
        _bottom = _bottom + spend[_svc].to_numpy()
    ax_sp.set_ylabel("Spend (USD)")
    ax_sp.set_title("(b) AWS spend, aggregated by service")
    ax_sp.legend(ncol=2, frameon=False, loc="upper center", bbox_to_anchor=(0.4, 0.95))

    ax_sp.set_xticks(_x)
    ax_sp.set_xticklabels(_labels)

    # Styling
    ax_em.spines[["top", "right"]].set_visible(False)
    ax_sp.spines[["top", "right"]].set_visible(False)

    fig_paper.tight_layout()
    fig_paper
    return


@app.cell
def _(Patch, cur, emissions, np, pd, plt):
    # Paper figure with a "zoom" inset (experimental copy of the cell above):
    #   (a) emissions by scope/service; (b) spend by service; (c) explodes May's
    #   "Other" spend into its top usage types and blows it up to full height,
    #   with dashed connectors from the "Other" segment of (b)'s May bar.
    # All names are underscore-local so this coexists with the cell above.
    from matplotlib.patches import ConnectionPatch

    _SERVICE_ORDER = ["AmazonEC2", "Other"]
    _COLOR = {"AmazonEC2": "#4C72B0", "Other": "#DD8452"}
    _LABEL = {"AmazonEC2": "EC2", "Other": "Other"}

    def _pivot(df, col, scale=1.0):
        return (
            df.pivot_table(index="usage_month", columns="service", values=col,
                           aggfunc="sum", fill_value=0.0)
            .reindex(columns=_SERVICE_ORDER, fill_value=0.0)
            .sort_index() * scale
        )

    _s2 = _pivot(emissions, "total_scope_2_lbm_emissions_value", 1000.0)
    _s3 = _pivot(emissions, "total_scope_3_lbm_emissions_value", 1000.0)
    _spend = _pivot(cur[cur["line_item_line_item_type"] == "Usage"], "line_item_unblended_cost")

    # Explode the "Other" service into usage-type categories (top 6 + remainder).
    _USAGE_LABEL = {
        "EUC1-VendedLog-Bytes": "CloudWatch Logs",
        "EUC1-AmazonEKS-Hours:perCluster": "EKS control-plane",
        "EUC1-LoadBalancerUsage": "ELB hours",
        "EUC1-PublicIPv4:InUseAddress": "Public IPv4",
        "EUC1-CW:MetricMonitorUsage": "CloudWatch Metrics",
        "EUC1-DataProcessing-Bytes": "ELB data",
        "EUC1-DataTransfer-Out-Bytes": "Data transfer out",
        "EUC1-DataTransfer-Regional-Bytes": "Data transfer",
    }
    _other = cur[(cur["service"] == "Other") & (cur["line_item_line_item_type"] == "Usage")].copy()
    _other["label"] = _other["line_item_usage_type"].map(lambda u: _USAGE_LABEL.get(u, u))
    _by_label = (
        _other.groupby(["usage_month", "label"])["line_item_unblended_cost"]
        .sum().unstack("label").fillna(0.0).sort_index()
    )
    _top6 = _by_label.sum().sort_values(ascending=False).head(6).index
    _month = _spend.index[-1]  # 2026-05
    _may = _by_label.loc[_month]
    _zoom_cats = list(_top6) + ["Other"]
    _zoom_vals = list(_may[_top6].to_numpy()) + [_may.sum() - _may[_top6].sum()]

    _x = np.arange(len(_s2.index))
    _labels = [pd.to_datetime(m).strftime("%b\n%Y") for m in _s2.index]
    fig_zoom, _axd = plt.subplot_mosaic(
        [["a", "l"], ["b", "c"]],
        figsize=(7.5, 5), gridspec_kw={"width_ratios": [4, 0.5]},
    )
    _ax_em, _ax_sp, _ax_c, _ax_leg = _axd["a"], _axd["b"], _axd["c"], _axd["l"]

    # (a) emissions: EC2 S2, EC2 S3, Other S2, Other S3 (solid = S2, striped = S3).
    _bottom = np.zeros(len(_x))
    for _svc in _SERVICE_ORDER:
        for _piv, _hatch in ((_s2, None), (_s3, "//")):
            _ax_em.bar(_x, _piv[_svc], 0.6, bottom=_bottom, color=_COLOR[_svc],
                       hatch=_hatch, edgecolor="white" if _hatch else "none")
            _bottom = _bottom + _piv[_svc].to_numpy()
    _ax_em.set_ylabel("LBM emissions (kg CO$_2$e)")
    _ax_em.set_title("(a) AWS reported emissions: Scope 2 vs Scope 3, by service")
    _ax_em.legend(
        handles=[Patch(facecolor=_COLOR[s], label=_LABEL[s]) for s in _SERVICE_ORDER]
        + [Patch(facecolor="#bbb", label="Scope 2"),
           Patch(facecolor="#bbb", hatch="//", edgecolor="white", label="Scope 3")],
        ncol=2, frameon=False, loc="upper center", bbox_to_anchor=(0.55, 1),
    )
    _ax_em.set_xticks(_x)
    _ax_em.set_xticklabels([])

    # (b) spend by service.
    _bottom = np.zeros(len(_x))
    for _svc in _SERVICE_ORDER:
        _ax_sp.bar(_x, _spend[_svc], 0.6, bottom=_bottom, color=_COLOR[_svc], label=_LABEL[_svc])
        _bottom = _bottom + _spend[_svc].to_numpy()
    _ax_sp.set_ylabel("Spend (USD)")
    _ax_sp.set_title("(b) AWS spend, aggregated by service")
    _ax_sp.legend(ncol=2, frameon=False, loc="upper center", bbox_to_anchor=(0.4, 0.95))
    _ax_sp.set_xticks(_x)
    _ax_sp.set_xticklabels(_labels)
    _ax_em.set_xlim(_ax_sp.get_xlim())

    # (c) zoom: May's "Other" spend exploded into its top usage types, full height.
    _cmap = plt.cm.tab10.colors[2:]
    _b = 0.0
    for _i, (_cat, _val) in enumerate(zip(_zoom_cats, _zoom_vals)):
        _col = "#cccccc" if _cat == "Other" else _cmap[_i % 10]
        _ax_c.bar(0, _val, 0.8, bottom=_b, color=_col, label=_cat)
        _b += _val
    _ax_c.set_xticks([0])
    _ax_c.set_xticklabels(["May"])
    _ax_c.set_title("(c) May 'Other'")
    #_ax_c.set_ylabel("Spend (USD)")

    # Category legend goes in the empty top-right cell.
    _ax_leg.axis("off")
    _hc, _lc = _ax_c.get_legend_handles_labels()
    _ax_leg.legend(_hc, _lc, frameon=False, loc="center left", title="'Other' usage type")

    # Connectors tie May's "Other" segment in (b) to the full-height bar in (c).
    _may_ec2 = _spend["AmazonEC2"].iloc[-1]
    _may_oth = _spend["Other"].iloc[-1]
    for _y_b, _y_c in [(_may_ec2, 0.0), (_may_ec2 + _may_oth, _may_oth)]:
        _con = ConnectionPatch(
            xyA=(_x[-1] + 0.3, _y_b), coordsA=_ax_sp.transData,
            xyB=(-0.4, _y_c), coordsB=_ax_c.transData,
            color="#999", linewidth=0.6, linestyle=(0, (3, 3)),
        )
        fig_zoom.add_artist(_con)

    for _ax in (_ax_em, _ax_sp, _ax_c):
        _ax.spines[["top", "right"]].set_visible(False)

    fig_zoom.align_ylabels()
    fig_zoom.tight_layout()
    fig_zoom.savefig("paper/figures/aws_spend_carbon.pdf", bbox_inches="tight")
    fig_zoom
    return


@app.cell
def _(cur):
    # Bottom-up EC2 Scope 2 LBM estimate: vCPU-hours -> kWh -> tCO2e.
    #   kWh       = vCPU-hours * watts_per_vCPU / 1000 * PUE
    #   emissions = kWh * grid_intensity (Germany LBM, tCO2e/MWh)
    # The fleet is all-Frankfurt and CPU-bound, so a per-vCPU power model with
    # published CCF coefficients is the defensible, citable choice. We carry a
    # utilization range (idle..full) because CloudWatch telemetry is unavailable.
    VCPU = {
        "t2.micro": 1, "t3.medium": 2, "t3.2xlarge": 8, "m6i.large": 2,
        "c6g.large": 2, "g4ad.xlarge": 4, "g6.xlarge": 4, "g6e.xlarge": 4,
    }
    CCF_MIN_W_PER_VCPU = 0.74   # idle
    CCF_MAX_W_PER_VCPU = 3.50   # 100% util
    PUE = 1.135                 # AWS published global average
    GRID_INTENSITY_TCO2_PER_MWH = 0.363  # Germany 2024 avg (Ember); fleet all-Frankfurt

    ec2 = cur[
        (cur["service"] == "AmazonEC2")
        & cur["line_item_usage_type"].str.contains("BoxUsage", na=False)
        & (cur["line_item_line_item_type"] == "Usage")
    ].copy()
    ec2["vcpu"] = ec2["product_instance_type"].map(VCPU)
    _missing = ec2[ec2["vcpu"].isna()]["product_instance_type"].unique()
    ec2["vcpu_hours"] = ec2["line_item_usage_amount"] * ec2["vcpu"]

    def _scope2_t(watts_per_vcpu):
        _kwh = ec2["vcpu_hours"] * watts_per_vcpu / 1000.0 * PUE
        return _kwh / 1000.0 * GRID_INTENSITY_TCO2_PER_MWH

    _w_mid = (CCF_MIN_W_PER_VCPU + CCF_MAX_W_PER_VCPU) / 2.0
    ec2["bu_idle_t"] = _scope2_t(CCF_MIN_W_PER_VCPU)
    ec2["bu_mid_t"] = _scope2_t(_w_mid)
    ec2["bu_full_t"] = _scope2_t(CCF_MAX_W_PER_VCPU)

    bottom_up_monthly = (
        ec2.groupby("usage_month", as_index=False)
        .agg(
            ec2_hours=("line_item_usage_amount", "sum"),
            vcpu_hours=("vcpu_hours", "sum"),
            bu_idle_t=("bu_idle_t", "sum"),
            bu_mid_t=("bu_mid_t", "sum"),
            bu_full_t=("bu_full_t", "sum"),
        )
        .sort_values("usage_month")
        .reset_index(drop=True)
    )
    {"missing_instance_types": list(_missing), "monthly": bottom_up_monthly}
    return (bottom_up_monthly,)


@app.cell
def _(bottom_up_monthly, merged, pd):
    # Reconciliation: CCFT-reported EC2 Scope 2 LBM vs the bottom-up range.
    # Bottom-up exceeds top-down every month, so we report the gap as a factor
    # (bottom-up / top-down). It is unattributable: AWS's LBM factor IS the grid
    # average (Model 3.0 §3.2.3), so the gap lives in undisclosed *Load* (§3.2.2).
    ec2_top_down = (
        merged[(merged["_merge"] == "both") & (merged["service"] == "AmazonEC2")]
        .groupby("usage_month", as_index=False)
        .agg(top_down_t=("total_scope_2_lbm_emissions_value", "sum"))
    )
    reconciliation = pd.merge(
        ec2_top_down, bottom_up_monthly, on="usage_month", how="outer"
    ).sort_values("usage_month")
    reconciliation["gap_x_mid"] = (
        reconciliation["bu_mid_t"] / reconciliation["top_down_t"]
    )

    _t = reconciliation[["top_down_t", "bu_idle_t", "bu_mid_t", "bu_full_t"]].sum()
    _agg = {
        "top_down_total_t": round(_t["top_down_t"], 4),
        "gap_x_idle": round(_t["bu_idle_t"] / _t["top_down_t"], 1),
        "gap_x_mid": round(_t["bu_mid_t"] / _t["top_down_t"], 1),
        "gap_x_full": round(_t["bu_full_t"] / _t["top_down_t"], 1),
    }
    _agg
    return (reconciliation,)


@app.cell
def _(plt, reconciliation):
    # Reconciliation plot: (A) top-down vs bottom-up EC2 Scope 2 LBM with the
    # idle..full band, (B) the bottom-up/top-down gap factor per month.
    fig_r, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4))
    _m = reconciliation["usage_month"]
    axA.plot(
        _m, reconciliation["top_down_t"], "o-",
        label="Top-down (CCFT LBM)", color="#1f77b4",
    )
    axA.plot(
        _m, reconciliation["bu_mid_t"], "s--",
        label="Bottom-up (CCF, 50% util)", color="#d62728",
    )
    axA.fill_between(
        _m, reconciliation["bu_idle_t"], reconciliation["bu_full_t"],
        color="#d62728", alpha=0.15, label="Bottom-up idle..full",
    )
    axA.set_ylabel("EC2 Scope 2 LBM (tCO2e)")
    axA.set_xlabel("Month")
    axA.tick_params(axis="x", rotation=45)
    axA.legend()

    axB.bar(_m, reconciliation["gap_x_mid"], color="#7f7f7f")
    axB.axhline(1, color="black", linewidth=0.6)
    axB.set_ylabel("Bottom-up / top-down (×)")
    axB.set_xlabel("Month")
    axB.tick_params(axis="x", rotation=45)

    fig_r.tight_layout()
    fig_r
    return


@app.cell
def _(cur, pd, plt):
    # "Other" service breakdown: top non-EC2/S3 services by cost — the same bucket
    # that dominates the top-down Scope 3 and Scope 2 "Other" rows in CCFT.
    # (Scaffolding for the later billing comparison.)
    OTHER_SERVICES = [
        "AmazonCloudWatch",
        "AmazonEKS",
        "AWSELB",
        "AmazonVPC",
        "AWSDataTransfer",
        "awskms",
        "AWSGlue",
        "AWSQueueService",
        "AmazonSNS",
        "AWSSecretsManager",
    ]
    USAGE_LABEL = {
        "EUC1-VendedLog-Bytes":           "CloudWatch Logs (GB)",
        "EUC1-AmazonEKS-Hours:perCluster":"EKS control-plane (hrs)",
        "EUC1-LoadBalancerUsage":         "ELB hours",
        "EUC1-PublicIPv4:InUseAddress":   "Public IPv4 (IP-hrs)",
        "EUC1-CW:MetricMonitorUsage":     "CloudWatch Metrics",
        "EUC1-DataProcessing-Bytes":      "ELB data (GB)",
        "EUC1-DataTransfer-Regional-Bytes":"Data transfer (GB)",
    }

    other_cur = cur[
        (cur["service"] == "Other")
        & (cur["line_item_line_item_type"] == "Usage")
    ].copy()
    other_cur["label"] = other_cur["line_item_usage_type"].map(
        lambda u: USAGE_LABEL.get(u, u)
    )

    other_pivot = (
        other_cur.groupby(["usage_month", "label"])["line_item_unblended_cost"]
        .sum()
        .unstack("label")
        .fillna(0)
        .sort_index()
    )
    top_labels = other_pivot.sum().sort_values(ascending=False).head(6).index
    other_top = other_pivot[top_labels]

    fig_o, ax_o = plt.subplots(figsize=(10, 4))
    bottom = pd.Series(0.0, index=other_top.index)
    colors = plt.cm.tab10.colors
    for i, col in enumerate(other_top.columns):
        ax_o.bar(other_top.index, other_top[col], bottom=bottom, label=col, color=colors[i])
        bottom = bottom + other_top[col]
    ax_o.set_ylabel("Unblended cost (USD)")
    ax_o.set_xlabel("Month")
    ax_o.tick_params(axis="x", rotation=45)
    ax_o.legend(fontsize=8, loc="upper right")
    fig_o.tight_layout()
    fig_o
    return


@app.cell
def _():
    # Notes & next steps:
    # - Power table uses static averages — refine with CloudWatch CPU utilization
    #   per instance and CCF's min/max watts-per-vCPU curves.
    # - Grid intensity is a Germany-wide annual average; hourly intensity
    #   (e.g. ElectricityMaps) would tighten the LBM estimate.
    # - Bottom-up is EC2-only. To reconcile total Scope 2 LBM, add S3 and the
    #   non-trivial "Other" services (CloudWatch, NAT, ELB).
    # - Next: overlay the billing ("Other" cost breakdown) against the emissions
    #   figure to compare cost vs carbon per category.
    return


if __name__ == "__main__":
    app.run()
