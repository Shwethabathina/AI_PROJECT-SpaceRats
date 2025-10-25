import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("bot1_ratStationery_fixedship_100runs.csv")

# Group by Alpha
alpha_summary = df.groupby("Alpha")[["Steps", "Pings"]].mean().reset_index()

# Create figure with light grey background
fig, ax1 = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('#d9d9d9')  # Light grey outer background
ax1.set_facecolor('#c0c0c0')        # Darker grey for plot area

# Plot Average Steps (maroon)
ln1 = ax1.plot(
    alpha_summary["Alpha"], alpha_summary["Steps"],
    color='maroon', marker='o', linestyle='-', linewidth=2, markersize=6, label="Average Steps"
)
ax1.set_xlabel("Alpha", fontsize=13)
ax1.set_ylabel("Average Steps", color='maroon', fontsize=13)
ax1.tick_params(axis='y', labelcolor='maroon', labelsize=11)
ax1.tick_params(axis='x', labelsize=11)

# Twin axis for Pings
ax2 = ax1.twinx()
ax2.set_facecolor('#c0c0c0')  # Match darker grey for right axis plot area
ln2 = ax2.plot(
    alpha_summary["Alpha"], alpha_summary["Pings"],
    color='black', marker='^', linestyle='--', linewidth=2, markersize=6, label="Average Pings"
)
ax2.set_ylabel("Average Pings", color='black', fontsize=13)
ax2.tick_params(axis='y', labelcolor='black', labelsize=11)

# Combine legends
lines = ln1 + ln2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', fontsize=12)

# Title and grid
plt.title("Effect of Alpha on Bot 1 Performance with stationary rat: Average Steps vs Pings", fontsize=15, pad=15)
ax1.grid(True, linestyle='--', alpha=0.5)
fig.tight_layout()

# Save and show
plt.savefig("avg_steps_pings_vs_alpha_darkergreybg.png")
plt.show()
