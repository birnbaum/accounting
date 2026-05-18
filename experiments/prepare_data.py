"""
Resample and merge the Azure LLM Inference 2024 traces.

Inputs (gitignored, downloaded separately from Azure/AzurePublicDataset):
    data/AzureLLMInferenceTrace_code_1week.csv  (~16.8M rows, May 10-16 2024)
    data/AzureLLMInferenceTrace_conv_1week.csv  (~27.3M rows, May 12-18 2024)

Outputs (small, committed):
    data/processed/per_minute.parquet
        Long format. One row per (timestamp_minute, service).
        Columns: timestamp, service, n_requests, context_tokens_sum, generated_tokens_sum.
    data/processed/sample_per_request.parquet
        Random sample for per-request scatter plots (Analysis 1).
        50k rows per service, fixed seed.
        Columns: timestamp, service, context_tokens, generated_tokens.

Citation for the trace:
    Stojkovic et al., "DynamoLLM: Designing LLM Inference Clusters for Performance
    and Energy Efficiency", HPCA 2025, arXiv:2408.00741.
"""

from __future__ import annotations

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "processed"

SOURCES = {
    "code": DATA / "AzureLLMInferenceTrace_code_1week.csv",
    "conv": DATA / "AzureLLMInferenceTrace_conv_1week.csv",
}

SAMPLE_PER_SERVICE = 50_000
SEED = 42


def load_one(service: str, path: pathlib.Path) -> pd.DataFrame:
    print(f"  reading {path.name} ...")
    df = pd.read_csv(
        path,
        parse_dates=["TIMESTAMP"],
        dtype={"ContextTokens": "int32", "GeneratedTokens": "int32"},
        engine="pyarrow",
    )
    df = df.rename(
        columns={
            "TIMESTAMP": "timestamp",
            "ContextTokens": "context_tokens",
            "GeneratedTokens": "generated_tokens",
        }
    )
    df["service"] = pd.Categorical([service] * len(df), categories=["conv", "code"])
    print(f"    {len(df):>12,} rows, {df.timestamp.min()} → {df.timestamp.max()}")
    return df


def aggregate_per_minute(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.assign(timestamp=df.timestamp.dt.floor("min"))
        .groupby(["timestamp", "service"], observed=True)
        .agg(
            n_requests=("context_tokens", "size"),
            context_tokens_sum=("context_tokens", "sum"),
            generated_tokens_sum=("generated_tokens", "sum"),
        )
        .reset_index()
    )
    return g


def sample_per_request(df: pd.DataFrame) -> pd.DataFrame:
    n = min(SAMPLE_PER_SERVICE, len(df))
    return df.sample(n=n, random_state=SEED).sort_values("timestamp").reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    per_minute_parts: list[pd.DataFrame] = []
    sample_parts: list[pd.DataFrame] = []

    for service, path in SOURCES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found. Download from "
                "https://github.com/Azure/AzurePublicDataset/blob/master/"
                "AzureLLMInferenceDataset2024.md"
            )
        print(f"[{service}]")
        df = load_one(service, path)

        per_minute_parts.append(aggregate_per_minute(df))
        sample_parts.append(sample_per_request(df))

    per_minute = (
        pd.concat(per_minute_parts, ignore_index=True)
        .sort_values(["timestamp", "service"])
        .reset_index(drop=True)
    )
    sample = (
        pd.concat(sample_parts, ignore_index=True)
        .sort_values(["timestamp", "service"])
        .reset_index(drop=True)
    )

    pm_path = OUT / "per_minute.parquet"
    sm_path = OUT / "sample_per_request.parquet"
    per_minute.to_parquet(pm_path, compression="zstd")
    sample.to_parquet(sm_path, compression="zstd")

    print()
    print(f"wrote {pm_path}: {len(per_minute):,} rows, {pm_path.stat().st_size / 1024:.0f} KB")
    print(f"wrote {sm_path}: {len(sample):,} rows, {sm_path.stat().st_size / 1024:.0f} KB")
    print()
    print("Per-minute summary:")
    print(
        per_minute.groupby("service", observed=True)
        .agg(
            minutes=("timestamp", "nunique"),
            total_requests=("n_requests", "sum"),
            total_context_tokens=("context_tokens_sum", "sum"),
        )
        .to_string()
    )


if __name__ == "__main__":
    main()
