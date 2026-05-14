# %% [markdown]
# # Case Study Visualization: rSCI for EKS Management Cluster
# Matplotlib version for academic paper plots.

# %%
import pandas as pd
import matplotlib.pyplot as plt
import os

# Handle interactive environments where __file__ is not defined
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # If running interactively, assume we are in the script's directory 
    # or fallback to a path relative to the project root.
    SCRIPT_DIR = os.path.abspath('')
    if not os.path.exists(os.path.join(SCRIPT_DIR, 'timeline.csv')):
        # Attempt to find it in the expected subdirectory
        SCRIPT_DIR = os.path.join(os.getcwd(), 'aws', 'case_study')

df = pd.read_csv(os.path.join(SCRIPT_DIR, 'timeline.csv'), parse_dates=['timestamp'])
breakdown = pd.read_csv(os.path.join(SCRIPT_DIR, 'breakdown.csv'))

# Set global style for papers
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.size': 10, 'figure.autolayout': True})

# %% [markdown]
# ## 1. The Resource Timeline (Dual Axis)
# %%
fig, ax1 = plt.subplots(figsize=(10, 5))

# Instance Count (Left Axis)
color = 'tab:blue'
ax1.set_xlabel('Time (Feb 2026)')
ax1.set_ylabel('Instance Count', color=color)
ax1.plot(df['timestamp'], df['instance_count'], color=color, linewidth=2, label='Compute Nodes')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 20)

# Network Transfer (Right Axis)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Network Transfer (GB/h)', color=color)
ax2.plot(df['timestamp'], df['network_transfer_gb'], color=color, linewidth=1, linestyle='--', alpha=0.7, label='Data Transfer')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('System Activity Timeline')
fig.tight_layout()
plt.show()

# %% [markdown]
# ## 2. Carbon Composition (Reconciliation View)
# Instead of a Sankey, we use a stacked bar to show the breakdown of the 15.3kg total.

# %%
# Data from analyze.py
total_reported = 15322.0
op_s2 = 4478.2
res_s2 = 5217.8
res_s1 = 59.0
res_s3 = 5567.0

labels = ['Provider Scopes', 'rSCI Allocation']
# Left bar: Scopes
# Right bar: rSCI (Op + Res)

fig, ax = plt.subplots(figsize=(8, 6))

width = 0.5
# Left Bar
ax.bar(labels[0], res_s1, width, label='Scope 1', color='#EF553B')
ax.bar(labels[0], 9696.0, width, bottom=res_s1, label='Scope 2', color='#636EFA')
ax.bar(labels[0], 5567.0, width, bottom=res_s1 + 9696.0, label='Scope 3', color='#00CC96')

# Right Bar
ax.bar(labels[1], op_s2, width, label='Operational (Workload)', color='#AB63FA')
ax.bar(labels[1], res_s1 + res_s2 + res_s3, width, bottom=op_s2, label='Residual (Overhead)', color='#FFA15A')

ax.set_ylabel('Carbon Footprint (g CO2e)')
ax.set_title('Reconciliation: Reported Scopes vs. rSCI Allocation')
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

# %% [markdown]
# ## 3. Cost Breakdown
# %%
plt.figure(figsize=(10, 5))
plt.bar(breakdown['category'], breakdown['cost_usd'], color='gray', alpha=0.8)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Cost (USD)')
plt.title('Cost Breakdown per Component')
plt.show()
