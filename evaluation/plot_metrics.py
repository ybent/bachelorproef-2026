import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

# ==========================================
# 1. Parse File Argument
# ==========================================
if len(sys.argv) < 2:
    print("Error: Missing CSV file parameter.")
    print("Usage: python3 plot_metrics.py <path_to_csv_file>")
    print("Example: python3 plot_metrics.py /output/phase1_suricata_idle.csv")
    sys.exit(1)

csv_file = sys.argv[1]

if not os.path.exists(csv_file):
    print(f"Error: File '{csv_file}' not found.")
    sys.exit(1)

# ==========================================
# 2. Load Data & Format Metadata
# ==========================================
df = pd.read_csv(csv_file)

# Extract directory path and base file name
output_dir = os.path.dirname(csv_file)
base_name = os.path.splitext(os.path.basename(csv_file))[0]
clean_title = base_name.replace("_", " ").title()

# Define output file paths in the same directory as the input CSV
output_png = (
    os.path.join(output_dir, f"{base_name}_plot.png")
    if output_dir
    else f"{base_name}_plot.png"
)
output_pdf = (
    os.path.join(output_dir, f"{base_name}_plot.pdf")
    if output_dir
    else f"{base_name}_plot.pdf"
)

# ==========================================
# 3. Build Subplots (CPU & RAM)
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# Color palette suitable for academic publishing
cpu_color = "#D95F02"  # Slate Orange
ram_color = "#7570B3"  # Deep Purple

# Top Plot: CPU Usage
ax1.plot(
    df["Timestamp_Sec"],
    df["CPU_Percent"],
    color=cpu_color,
    linewidth=1.5,
    label="CPU Usage (%)",
)
ax1.set_ylabel("CPU Usage (%)", fontsize=11, fontweight="bold")
ax1.set_title(
    f"IDS Performance Metrics: {clean_title}",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.legend(loc="upper right")

# Bottom Plot: RAM Usage
ax2.plot(
    df["Timestamp_Sec"],
    df["RAM_MB"],
    color=ram_color,
    linewidth=1.5,
    label="RAM Usage (MB)",
)
ax2.set_xlabel("Elapsed Time (Seconds)", fontsize=11, fontweight="bold")
ax2.set_ylabel("RAM Usage (MB)", fontsize=11, fontweight="bold")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend(loc="upper right")

# Disable scientific notation (+1.5271e3) and format Y-axis with 2 decimals
ax2.ticklabel_format(useOffset=False, style="plain", axis="y")
ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))

# ==========================================
# 4. Save Figures
# ==========================================
plt.tight_layout()

# Save PNG (Raster, 300 DPI)
plt.savefig(output_png, dpi=300, bbox_inches="tight")

# Save PDF (Vector, for LaTeX / Thesis)
plt.savefig(output_pdf, bbox_inches="tight")

print(f"[✓] Graph generation complete for '{base_name}':")
print(f"    ├─ Image Saved: {output_png} (300 DPI)")
print(f"    └─ Vector Saved: {output_pdf}")