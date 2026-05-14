import pandas as pd
import numpy as np

# --- Configuration ---
CUR_FILE = 'aws/philipp-cur-export-00001_2026-02.snappy.parquet'
MONTH = '2026-02'
REGION = 'Europe (Frankfurt)'
INTENSITY = 394.32 / 1000 # g/Wh
HOURS_IN_MONTH = 672
W_PER_VCPU = 0.65
VCPUS_PER_NODE = 2

# Reported Totals (from CSV)
S1_TOTAL = 59.0
S2_TOTAL = 9696.0
S3_TOTAL = 5567.0

# --- Load and Process ---
df = pd.read_parquet(CUR_FILE)
df = df[df['line_item_line_item_type'] == 'Usage'].copy()
df['timestamp'] = pd.to_datetime(df['line_item_usage_start_date'])

def categorize(row):
    if row['product_servicecode'] == 'AmazonEKS': return 'eks_control_plane'
    if row['product_product_family'] == 'Storage': return 'storage_gb'
    if row['product_product_family'] == 'NAT Gateway': return 'nat_gateway_gb'
    if 'DataTransfer' in row['product_servicecode']: return 'network_transfer_gb'
    if row['product_product_family'] in ['Compute Instance', 'Compute']: return 'compute_nodes'
    return 'other'

df['category'] = df.apply(categorize, axis=1)

# --- Hourly Aggregation ---
print("Generating hourly timeline...")
pivot = df.pivot_table(
    index='timestamp', 
    columns='category', 
    values='line_item_usage_amount', 
    aggfunc='sum'
).fillna(0)

# Add Instance Count specifically
instance_count = df[df['category'] == 'compute_nodes'].groupby('timestamp')['line_item_resource_id'].nunique()
pivot['instance_count'] = instance_count.fillna(0)

# Calculate Operational Carbon (Hourly)
# E = instances * 2 vcpus * 0.65W
pivot['operational_energy_wh'] = pivot['instance_count'] * VCPUS_PER_NODE * W_PER_VCPU
pivot['carbon_s2_operational_g'] = pivot['operational_energy_wh'] * INTENSITY

pivot.to_csv('case_study_timeline_enriched.csv')
print("Saved case_study_timeline_enriched.csv")

# --- Granular Breakdown per Cluster-Hour ---
# S2 Residual = Total S2 - Total Operational
total_op_s2 = pivot['carbon_s2_operational_g'].sum()
s2_residual = S2_TOTAL - total_op_s2

print(f"\n--- Granular Carbon Breakdown per Cluster-Hour (n={HOURS_IN_MONTH}) ---")
print(f"{'Component':<25} | {'Hourly (g CO2e/h)':<20} | {'Total Month (g)':<15}")
print("-" * 70)

metrics = [
    ("Scope 1 (Residual)", S1_TOTAL),
    ("Scope 2 (Operational)", total_op_s2),
    ("Scope 2 (Residual)", s2_residual),
    ("Scope 3 (Residual)", S3_TOTAL)
]

for name, total in metrics:
    hourly = total / HOURS_IN_MONTH
    print(f"{name:<25} | {hourly:<20.4f} | {total:<15.2f}")

print("-" * 70)
total_hourly = sum(t for n, t in metrics) / HOURS_IN_MONTH
print(f"{'TOTAL rSCI':<25} | {total_hourly:<20.4f} | {sum(t for n, t in metrics):<15.2f}")
