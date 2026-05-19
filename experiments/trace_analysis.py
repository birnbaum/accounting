import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from pathlib import Path

    return Path, mo, pd


@app.cell
def _(Path, mo, pd):
    mo.md(rf"# Simulation Trace Analysis")

    trace_path = Path("../data/processed/per_minute.parquet")

    if not trace_path.exists():
        # Try relative to project root if run from there
        trace_path = Path("data/processed/per_minute.parquet")

    mo.stop(not trace_path.exists(), f"Trace file not found at {trace_path}")

    df = pd.read_parquet(trace_path)    return (df,)


@app.cell
def _(df, mo):
    mo.md(f"""
    Loaded trace with {len(df):,} rows.
    """)
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(df):
    df["grid_ci_gco2_per_kwh"].plot()
    return


if __name__ == "__main__":
    app.run()
