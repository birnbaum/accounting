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
    df_ci = pd.read_csv("data/carbonintensity_2026-03-23.csv")

    fig_ci, ax_ci = plt.subplots(figsize=(10, 4))
    df_ci.plot(ax=ax_ci)
    fig_ci.tight_layout()

    fig_ci
    return


@app.cell
def _(df, plt):
    _fig, _ax = plt.subplots(figsize=(10,2))
    (df["context_tokens"] / 60 / 9100 / 15).plot(ax=_ax)
    _ax.set(ylim=(0,1))
    _fig
    return


if __name__ == "__main__":
    app.run()
