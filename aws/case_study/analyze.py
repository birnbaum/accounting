import pandas as pd
import os

# Paths relative to the script location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUR_FILE = os.path.join(BASE_DIR, 'philipp-cur-export-00001_2026-02.snappy.parquet')
CARBON_CSV = os.path.join(BASE_DIR, 'monthly_carbon_emissions.csv')
INTENSITY = 394.32 / 1000 # g/Wh

# CCF Baseline (Idle Power)
W_PER_VCPU = 0.65 
VCPUS_PER_NODE = 2
HOURS_IN_MONTH = 672

# Reported Totals for Feb 2026 Frankfurt
S1_TOTAL = 59.0
S2_TOTAL = 9696.0
S3_TOTAL = 5567.0
TOTAL_REPORTED = S1_TOTAL + S2_TOTAL + S3_TOTAL

def run_analysis():
    print("1. Loading and categorizing data...")
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

    print("2. Reconstructing timeline and energy...")
    pivot = df.pivot_table(
        index='timestamp', 
        columns='category', 
        values='line_item_usage_amount', 
        aggfunc='sum'
    ).fillna(0)

    # Instance Count
    instance_count = df[df['category'] == 'compute_nodes'].groupby('timestamp')['line_item_resource_id'].nunique()
    pivot['instance_count'] = instance_count.fillna(0)

    # Operational Carbon
    pivot['operational_energy_wh'] = pivot['instance_count'] * VCPUS_PER_NODE * W_PER_VCPU
    pivot['carbon_s2_operational_g'] = pivot['operational_energy_wh'] * INTENSITY

    # Save enriched timeline
    pivot.to_csv(os.path.join(os.path.dirname(__file__), 'timeline.csv'))
    
    # Cost Breakdown
    breakdown = df.groupby('category')['line_item_unblended_cost'].sum().reset_index()
    breakdown.rename(columns={'line_item_unblended_cost': 'cost_usd'}, inplace=True)
    breakdown.to_csv(os.path.join(os.path.dirname(__file__), 'breakdown.csv'), index=False)

    # Summary
    total_op_s2 = pivot['carbon_s2_operational_g'].sum()
    s2_residual = S2_TOTAL - total_op_s2
    
    print(f"\n--- System Reconciliation Summary (Feb 2026) ---")
    print(f"Total Reported Carbon: {TOTAL_REPORTED:.2f} g CO2e")
    print(f"Actionable Work (Op):  {total_op_s2:.2f} g CO2e")
    print(f"Infrastructure Res:    {(TOTAL_REPORTED - total_op_s2):.2f} g CO2e")
    print(f"Overhead Ratio:        {(1 - total_op_s2/TOTAL_REPORTED):.1%}")

if __name__ == "__main__":
    run_analysis()
