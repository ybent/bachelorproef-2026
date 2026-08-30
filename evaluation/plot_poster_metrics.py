import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

# ==========================================
# 1. Parse File Arguments
# ==========================================
if len(sys.argv) < 4:
    print("Gebruik: python plot_combined.py <normaal_csv> <aanval_csv> <titel_en_output_naam>")
    print("Voorbeeld: python plot_combined.py suricata_normaal.csv suricata_aanval.csv Suricata")
    sys.exit(1)

normal_csv = sys.argv[1]
attack_csv = sys.argv[2]
system_name = sys.argv[3] 

# ==========================================
# 2. Load Data
# ==========================================
df_normal = pd.read_csv(normal_csv)
df_attack = pd.read_csv(attack_csv)

output_png = f"P_{system_name.lower()}_combined.png"
output_pdf = f"P_{system_name.lower()}_combined.pdf"

# ==========================================
# 3. Build Subplots (Systeemmonitor stijl)
# ==========================================
# Gebruik de standaard matplotlib stijl (witte achtergrond, geen opmaak-franjes)
plt.style.use('default')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

# Instellingen om de referentiefoto na te bootsen
color_normal = "blue"
color_attack = "red"
marker_normal = "d"  # Ruitjes (diamonds) voor normaal
marker_attack = "s"  # Vierkantjes (squares) voor aanval
LINE_WIDTH = 1.0
MARKER_SIZE = 3      # Kleine symbooltjes op de lijnen

# --- Top Plot: CPU Usage ---
line_norm, = ax1.plot(df_normal["Timestamp_Sec"], df_normal["CPU_Percent"], 
                      color=color_normal, marker=marker_normal, markersize=MARKER_SIZE, 
                      linewidth=LINE_WIDTH, label="Normaal Verkeer")

line_att, = ax1.plot(df_attack["Timestamp_Sec"], df_attack["CPU_Percent"], 
                     color=color_attack, marker=marker_attack, markersize=MARKER_SIZE, 
                     linewidth=LINE_WIDTH, label="Stress-test (Aanval)")

ax1.set_ylabel("CPU usage(%)", fontweight="bold")
ax1.set_title(f"{system_name.title()}: Normaal vs. Aanval", fontweight="bold", pad=12)

# Specifiek grid: Grijze stippellijnen, net als in het voorbeeld
ax1.grid(True, linestyle="--", color="gray", alpha=0.8)

# --- Bottom Plot: RAM Usage ---
ax2.plot(df_normal["Timestamp_Sec"], df_normal["RAM_MB"], 
         color=color_normal, marker=marker_normal, markersize=MARKER_SIZE, linewidth=LINE_WIDTH)

ax2.plot(df_attack["Timestamp_Sec"], df_attack["RAM_MB"], 
         color=color_attack, marker=marker_attack, markersize=MARKER_SIZE, linewidth=LINE_WIDTH)

ax2.set_xlabel("Time (s)", fontweight="bold")
ax2.set_ylabel("RAM usage (MB)", fontweight="bold")
ax2.grid(True, linestyle="--", color="gray", alpha=0.8)

# Y-as formattering om wetenschappelijke notatie te voorkomen
ax2.ticklabel_format(useOffset=False, style="plain", axis="y")
ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))

# ==========================================
# 4. Legende Onderaan & Opslaan
# ==========================================
# Verwijder lege ruimte tussen de twee grafieken
plt.subplots_adjust(hspace=0.1)

# Plaats één gezamenlijke legende helemaal onderaan de afbeelding, gecentreerd
fig.legend(handles=[line_norm, line_att], loc='lower center', ncol=2, 
           bbox_to_anchor=(0.5, 0.0), frameon=False, handletextpad=0.5)

# Zorg voor extra ruimte onderaan, zodat de legende niet over de as-labels valt
plt.subplots_adjust(bottom=0.12)

plt.savefig(output_png, dpi=300, bbox_inches="tight")
plt.savefig(output_pdf, bbox_inches="tight")

print(f"[✓] Grafiek in systeemmonitor-stijl gegenereerd: {output_png}")