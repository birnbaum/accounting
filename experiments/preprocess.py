import pandas as pd
from pathlib import Path

def aggregate_trace():
    input_path = Path("data/AzureLLMInferenceTrace_conv_1week.csv")
    output_path = Path("data/AzureLLMInferenceTrace_conv_1week_minutely.csv")

    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], format='ISO8601', utc=True)

    print(f"Preprocessing ...")
    df["minute"] = df["TIMESTAMP"].dt.floor("min")
    aggregated = df.groupby("minute").agg(
        n_requests=("TIMESTAMP", "count"),
        context_tokens=("ContextTokens", "sum"),
        generated_tokens=("GeneratedTokens", "sum")
    ).reset_index()

    print(f"Saving to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    aggregated.to_csv(output_path, index=False)

if __name__ == "__main__":
    aggregate_trace()
