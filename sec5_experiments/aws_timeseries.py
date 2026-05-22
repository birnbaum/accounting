import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import pandas as pd
    import pyarrow.parquet as pq
    import matplotlib.pyplot as plt

    REPO = Path(__file__).resolve().parents[1]
    CUR_DIR = REPO / "aws" / "cur_raw"
    EMISSIONS_CSV = REPO / "aws" / "monthly_carbon_emissions.csv"

    REPORT_FROM = "2025-12"
    return CUR_DIR, EMISSIONS_CSV, REPORT_FROM, mo, pd, plt, pq


@app.cell
def _(REPORT_FROM, mo):
    mo.md(
        rf"""
        # AWS top-down vs bottom-up — time series

        Aligns provider-reported emissions from CCFT (`monthly_carbon_emissions.csv`)
        with bottom-up CUR usage (`aws/cur_raw/BILLING_PERIOD=YYYY-MM/`).

        **Reporting window:** {REPORT_FROM} onwards. Earlier months had a promotional
        credit and an unstable usage profile, so they aren't comparable.

        Carbon CSV groups services into `AmazonEC2`, `AmazonS3`, `Other`. CUR identifies
        the service via `line_item_product_code`; we apply the same roll-up to merge.

        We focus on **scope 2 LBM** for the reconciliation since this is the only
        operational electricity-driven term that should move with bottom-up usage.
        """
    )
    return


@app.cell
def _(CUR_DIR, pd, pq):
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

    def load_cur_month(parquet_path):
        t = pq.read_table(parquet_path, columns=KEEP_COLS)
        df = t.to_pandas()
        df["usage_month"] = pd.to_datetime(
            df["bill_billing_period_start_date"]
        ).dt.strftime("%Y-%m")
        return df

    files = sorted(CUR_DIR.glob("BILLING_PERIOD=*/**/*.snappy.parquet"))
    cur_raw = pd.concat([load_cur_month(p) for p in files], ignore_index=True)
    cur_raw.shape, sorted(cur_raw["usage_month"].unique())
    return (cur_raw,)


@app.cell
def _(REPORT_FROM, cur_raw):
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
def _(EMISSIONS_CSV, REPORT_FROM, pd):
    emissions_full = pd.read_csv(EMISSIONS_CSV)
    emissions = emissions_full[emissions_full["usage_month"] >= REPORT_FROM].copy()
    emissions.head()
    return (emissions,)


@app.cell
def _(cur_monthly, emissions, pd):
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
def _(mo):
    mo.md(
        r"""
        ## Top-down: scope decomposition (LBM)

        Stack Scope 1 (direct fuel) + Scope 2 LBM (grid electricity, location-based)
        + Scope 3 LBM (upstream / embodied). Scope 2 MBM is omitted — AWS reports it
        as zero under their 100% renewable claim, so it carries no information.
        """
    )
    return


@app.cell
def _(merged):
    both = merged[merged["_merge"] == "both"].drop(columns="_merge")
    scopes_monthly = (
        both.groupby("usage_month", as_index=False)
        .agg(
            scope_1=("total_scope_1_emissions_value", "sum"),
            scope_2_lbm=("total_scope_2_lbm_emissions_value", "sum"),
            scope_3_lbm=("total_scope_3_lbm_emissions_value", "sum"),
        )
        .sort_values("usage_month")
        .reset_index(drop=True)
    )
    scopes_monthly
    return (scopes_monthly,)


@app.cell
def _(plt, scopes_monthly):
    fig_s, ax_s = plt.subplots(figsize=(8, 4))
    months = scopes_monthly["usage_month"]
    s1 = scopes_monthly["scope_1"]
    s2 = scopes_monthly["scope_2_lbm"]
    s3 = scopes_monthly["scope_3_lbm"]
    ax_s.bar(months, s1, label="Scope 1", color="#444")
    ax_s.bar(months, s2, bottom=s1, label="Scope 2 (LBM)", color="#1f77b4")
    ax_s.bar(months, s3, bottom=s1 + s2, label="Scope 3 (LBM)", color="#ff7f0e")
    ax_s.set_ylabel("Emissions (tCO2e)")
    ax_s.set_xlabel("Month")
    ax_s.tick_params(axis="x", rotation=45)
    ax_s.legend()
    fig_s.tight_layout()
    fig_s
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Bottom-up: EC2 instance-hours → kWh → kgCO2e

        Only six EC2 instance types appear in the window, so a static lookup is fine.
        Power numbers are mid-load averages (CCF-style: ~50% utilization assumed in the
        absence of CloudWatch telemetry). GPU instances include the accelerator TDP.

        - kWh = hours × avg_watts / 1000 × PUE
        - emissions = kWh × grid_intensity (Frankfurt LBM, tCO2e/MWh)
        - PUE = 1.135 (AWS published global average)
        - Frankfurt LBM grid intensity = 0.366 tCO2e/MWh (Germany 2024 avg, Ember/EEA)

        This estimates **scope 2 LBM only** — the term we should be able to reproduce
        from operational metering. Embodied (scope 3) is out of scope here.
        """
    )
    return


@app.cell
def _(cur):
    INSTANCE_POWER = {
        "t2.micro":   {"vcpu": 1, "avg_watts": 2.5},
        "t3.medium":  {"vcpu": 2, "avg_watts": 5.0},
        "t3.2xlarge": {"vcpu": 8, "avg_watts": 18.0},
        "m6i.large":  {"vcpu": 2, "avg_watts": 9.0},
        "g4ad.xlarge":{"vcpu": 4, "avg_watts": 75.0},
        "g6e.xlarge": {"vcpu": 4, "avg_watts": 200.0},
    }
    PUE = 1.135
    GRID_INTENSITY_TCO2_PER_MWH = 0.366

    ec2 = cur[
        (cur["service"] == "AmazonEC2")
        & cur["line_item_usage_type"].str.contains("BoxUsage", na=False)
        & (cur["line_item_line_item_type"] == "Usage")
    ].copy()
    ec2["avg_watts"] = ec2["product_instance_type"].map(
        lambda i: INSTANCE_POWER.get(i, {}).get("avg_watts")
    )
    missing = ec2[ec2["avg_watts"].isna()]["product_instance_type"].unique()

    ec2["kwh"] = (
        ec2["line_item_usage_amount"] * ec2["avg_watts"] / 1000.0 * PUE
    )
    ec2["bottom_up_scope2_lbm_t"] = ec2["kwh"] / 1000.0 * GRID_INTENSITY_TCO2_PER_MWH

    bottom_up_monthly = (
        ec2.groupby("usage_month", as_index=False)
        .agg(
            ec2_hours=("line_item_usage_amount", "sum"),
            kwh=("kwh", "sum"),
            bottom_up_scope2_lbm_t=("bottom_up_scope2_lbm_t", "sum"),
        )
        .sort_values("usage_month")
        .reset_index(drop=True)
    )
    {"missing_instance_types": list(missing), "monthly": bottom_up_monthly}
    return (bottom_up_monthly,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Reconciliation: top-down vs bottom-up Scope 2 LBM

        Compare CCFT-reported scope 2 LBM (AmazonEC2 only) against the bottom-up
        estimate from instance-hours. The residual is the top-down − bottom-up gap.
        """
    )
    return


@app.cell
def _(bottom_up_monthly, merged, pd):
    ec2_top_down = (
        merged[(merged["_merge"] == "both") & (merged["service"] == "AmazonEC2")]
        .groupby("usage_month", as_index=False)
        .agg(top_down_scope2_lbm_t=("total_scope_2_lbm_emissions_value", "sum"))
    )
    reconciliation = pd.merge(
        ec2_top_down, bottom_up_monthly, on="usage_month", how="outer"
    ).sort_values("usage_month")
    reconciliation["residual_t"] = (
        reconciliation["top_down_scope2_lbm_t"]
        - reconciliation["bottom_up_scope2_lbm_t"]
    )
    reconciliation["residual_pct_of_top_down"] = (
        100.0
        * reconciliation["residual_t"]
        / reconciliation["top_down_scope2_lbm_t"]
    )
    reconciliation.round(6)
    return (reconciliation,)


@app.cell
def _(plt, reconciliation):
    fig_r, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4))
    m = reconciliation["usage_month"]
    axA.plot(
        m,
        reconciliation["top_down_scope2_lbm_t"],
        "o-",
        label="Top-down (CCFT)",
        color="#1f77b4",
    )
    axA.plot(
        m,
        reconciliation["bottom_up_scope2_lbm_t"],
        "s--",
        label="Bottom-up (CUR × power × grid)",
        color="#d62728",
    )
    axA.set_ylabel("EC2 Scope 2 LBM (tCO2e)")
    axA.set_xlabel("Month")
    axA.tick_params(axis="x", rotation=45)
    axA.legend()

    axB.bar(m, reconciliation["residual_t"], color="#7f7f7f")
    axB.axhline(0, color="black", linewidth=0.6)
    axB.set_ylabel("Residual (top-down − bottom-up, tCO2e)")
    axB.set_xlabel("Month")
    axB.tick_params(axis="x", rotation=45)

    fig_r.tight_layout()
    fig_r
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Notes & next steps
        - Power table uses static averages — refine with CloudWatch CPU utilization
          per instance and CCF's min/max watts-per-vCPU curves.
        - Grid intensity is a Germany-wide annual average. Hourly grid intensity
          (e.g. ElectricityMaps) would tighten the LBM estimate.
        - Currently EC2-only. To reconcile total scope 2 LBM, add S3 (storage-byte-hours
          × disk power) and the non-trivial "Other" services (CloudWatch, NAT, ELB).
        - Once April / May 2026 CUR exports land, re-run the sync and the window
          extends to 6 months without further code changes.
        """
    )
    return


if __name__ == "__main__":
    app.run()
