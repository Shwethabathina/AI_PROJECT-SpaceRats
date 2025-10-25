import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("bot2_ratMoving_fixedship_100runs.csv")

# Compute total = Steps + Pings
df["Total"] = df["Steps"] + df["Pings"]
alpha_summary = df.groupby("Alpha")["Total"].mean().reset_index()

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(
    alpha_summary["Alpha"], alpha_summary["Total"],
    color='maroon', marker='s', linestyle='-.', linewidth=2, markersize=6, label="Avg (Steps + Pings)"
)

# Annotate points
for i in range(len(alpha_summary)):
    plt.text(
        alpha_summary["Alpha"][i], alpha_summary["Total"][i] + 2,
        f"({alpha_summary['Alpha'][i]:.2f}, {alpha_summary['Total'][i]:.1f})",
        fontsize=9, ha='center', color='maroon'
    )

# Styling
plt.title("Effect of Alpha on Bot 2 with moving rat: Average Total (Steps + Pings)", fontsize=14, fontweight='bold')
plt.xlabel("Alpha", fontsize=12)
plt.ylabel("Average Total Count", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left', fontsize=11)
plt.tight_layout()

# Save and display
plt.savefig("steps_plus_pings_only_maroon.png")
plt.show()
