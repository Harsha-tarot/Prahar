"""
Generate 5 PRAHAR comparison charts as high-resolution PNGs.
Run: python generate_charts.py
Output: d:/x3_f/prahar/charts/
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

# ── Output directory ──────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(OUT, exist_ok=True)

# ── Global style ──────────────────────────────────────────────────
BG      = "#ffffff"
PANEL   = "#ffffff"
BORDER  = "#000000"
GRID    = "#e0e0e0"
GREEN   = "#000000" # Black (PRAHAR)
RED     = "#333333" # Dark Gray
YELLOW  = "#555555" # Mid-Dark Gray
BLUE    = "#777777" # Mid Gray
PURPLE  = "#999999" # Light-Mid Gray
ORANGE  = "#bbbbbb" # Light Gray
TEXT    = "#000000"
DIM     = "#333333"

def base_style(fig, ax_list=None):
    """Apply print-friendly white theme to figure and axes."""
    fig.patch.set_facecolor(BG)
    if ax_list is None:
        ax_list = fig.get_axes()
    for ax in ax_list:
        ax.set_facecolor(PANEL)
        ax.tick_params(colors=DIM, labelsize=9)
        ax.xaxis.label.set_color(DIM)
        ax.yaxis.label.set_color(DIM)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_color(BORDER)
        ax.grid(color=GRID, linewidth=0.6, linestyle="-")

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=180, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  +  Saved  {path}")

def add_title_block(fig, num, title, badge, badge_color=DIM):
    """Add a styled figure number + title at the top."""
    fig.text(0.5, 0.98, f"FIGURE {num}",
             ha="center", va="top", fontsize=7.5, color=GREEN,
             fontweight="bold", fontfamily="monospace")
    fig.text(0.5, 0.955, title,
             ha="center", va="top", fontsize=12, color=TEXT,
             fontweight="bold")
    fig.text(0.5, 0.925, badge,
             ha="center", va="top", fontsize=7.5, color=badge_color,
             fontfamily="monospace")

# ══════════════════════════════════════════════════════════════════
#  CHART 1 — Processing Speed (FPS)  — Grouped Bar
# ══════════════════════════════════════════════════════════════════
def chart1():
    labels   = ["VisDrone\nBaseline", "SfM\nPipeline", "DroneNet\n(YOLOv5s)",
                "AerialDet\n(YOLOv7)", "PRAHAR\n(YOLOv8n)"]
    values   = [5, 0.05, 22, 18, 17]
    colors   = [RED+"aa", PURPLE+"aa", YELLOW+"aa", BLUE+"aa", GREEN+"dd"]
    borders  = [RED, PURPLE, YELLOW, BLUE, GREEN]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    base_style(fig, [ax])
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.1, right=0.97)

    bars = ax.bar(labels, values, color=colors, edgecolor=borders,
                  linewidth=1.8, width=0.55)

    # Annotate bars
    for bar, val in zip(bars, values):
        disp = f"{val} FPS" if val >= 1 else "~0 FPS\n(offline)"
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.4,
                disp, ha="center", va="bottom",
                color=TEXT, fontsize=9, fontfamily="monospace")

    # Highlight PRAHAR bar
    bars[-1].set_linewidth(2.5)

    ax.set_ylim(0, 27)
    ax.set_ylabel("Effective Frames Per Second", color=DIM, fontsize=10)
    ax.set_xlabel("Detection System", color=DIM, fontsize=10)
    ax.tick_params(axis="x", labelsize=8.5)

    # Annotation arrow
    ax.annotate("3.4× faster than\nVisDrone Baseline",
                xy=(4, 17), xytext=(3.1, 23),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.3),
                color=GREEN, fontsize=8, fontfamily="monospace", ha="center")

    add_title_block(fig, "01", "Real-Time Processing Speed Comparison (FPS)",
                    "↑  HIGHER IS BETTER  |  Benchmarked on Intel i7-12700H + RTX 3060")
    save(fig, "fig01_processing_fps.png")

# ══════════════════════════════════════════════════════════════════
#  CHART 2 — Detection F1 Score by Category  — Grouped Bar
# ══════════════════════════════════════════════════════════════════
def chart2():
    systems  = ["VisDrone\nBaseline", "DroneNet\n(YOLOv5s)",
                "AerialDet\n(YOLOv7)", "PRAHAR\n(Ours)"]
    personnel = [61.2, 70.4, 74.1, 85.4]
    vehicle   = [58.7, 66.8, 72.3, 79.3]
    overall   = [60.1, 68.9, 73.1, 83.2]

    x = np.arange(len(systems))
    w = 0.24

    fig, ax = plt.subplots(figsize=(9, 5.5))
    base_style(fig, [ax])
    fig.subplots_adjust(top=0.84, bottom=0.2, left=0.1, right=0.97)

    b1 = ax.bar(x - w, personnel, w, label="Personnel / Enemy Soldier",
                color=RED+"88", edgecolor=RED, linewidth=1.5)
    b2 = ax.bar(x,      vehicle,  w, label="Vehicle / Military Vehicle",
                color=YELLOW+"88", edgecolor=YELLOW, linewidth=1.5)
    b3 = ax.bar(x + w,  overall,  w, label="Overall F1",
                color=GREEN+"88", edgecolor=GREEN, linewidth=1.5)

    # Labels on PRAHAR bars
    for b, v in zip([b1[-1], b2[-1], b3[-1]], [85.4, 79.3, 83.2]):
        ax.text(b.get_x() + b.get_width()/2, v + 0.4, f"{v}%",
                ha="center", va="bottom", color=TEXT,
                fontsize=8.5, fontfamily="monospace")

    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=8.5)
    ax.set_ylim(50, 95)
    ax.set_ylabel("F1 Score (%)", color=DIM, fontsize=10)
    ax.set_xlabel("Detection System", color=DIM, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.legend(loc="lower right", fontsize=8, facecolor=PANEL,
              edgecolor=BORDER, labelcolor=TEXT)

    add_title_block(fig, "02", "Detection F1 Score by Object Category (%)",
                    "↑  HIGHER IS BETTER  |  Threshold = 0.25 conf, IoU = 0.45",
                    badge_color=DIM)
    save(fig, "fig02_f1_score.png")

# ══════════════════════════════════════════════════════════════════
#  CHART 3 — System Capability Radar
# ══════════════════════════════════════════════════════════════════
def chart3():
    axes_labels = ["Real-Time\nSpeed", "Detection\nAccuracy",
                   "3D Terrain\nOutput", "Edge\nDeployment", "Tactical\nHUD / UX"]
    N = len(axes_labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # close polygon

    datasets = [
        ("PRAHAR",           [8.5, 8.3, 9.5, 8.0, 9.5], GREEN,  2.5),
        ("VisDrone Baseline",[2.0, 5.5, 1.0, 2.5, 1.0], RED,    1.4),
        ("DroneNet",         [8.0, 6.5, 1.0, 6.0, 2.5], YELLOW, 1.4),
        ("AerialDet",        [7.0, 7.2, 1.5, 5.5, 2.0], BLUE,   1.4),
        ("SfM Pipeline",     [0.5, 4.0, 9.0, 1.0, 3.0], PURPLE, 1.4),
    ]

    fig, ax = plt.subplots(figsize=(7, 7),
                           subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.spines["polar"].set_color(BORDER)
    ax.tick_params(colors=DIM)
    fig.subplots_adjust(top=0.82, bottom=0.12)

    # Grid rings
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2","4","6","8","10"], color=DIM, fontsize=7.5)
    ax.yaxis.grid(color=GRID, linewidth=0.6)
    ax.xaxis.grid(color=GRID, linewidth=0.6)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, color=TEXT, fontsize=9, fontweight="bold")

    for name, data, color, lw in datasets:
        d = data + data[:1]
        alpha = 0.18 if name == "PRAHAR" else 0.06
        ax.plot(angles, d, color=color, linewidth=lw, linestyle="-")
        ax.fill(angles, d, color=color, alpha=alpha)

    # Legend
    patches = [mpatches.Patch(facecolor=c, edgecolor=c, label=n)
               for n, _, c, _ in datasets]
    ax.legend(handles=patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.14), ncol=3,
              fontsize=8, facecolor=PANEL, edgecolor=BORDER,
              labelcolor=TEXT, framealpha=0.9)

    add_title_block(fig, "03", "System Capability Radar — 5-Axis Comparison",
                    "SCORES OUT OF 10  |  Outer = Better", badge_color=DIM)
    save(fig, "fig03_capability_radar.png")

# ══════════════════════════════════════════════════════════════════
#  CHART 4 — Per-Frame Latency Breakdown  — Stacked Bar
# ══════════════════════════════════════════════════════════════════
def chart4():
    systems   = ["Faster R-CNN\n(VisDrone)", "YOLOv5s\n(DroneNet)",
                 "YOLOv7\n(AerialDet)", "PRAHAR\n(Sampled)", "PRAHAR\n(Non-sampled)"]
    frame_read = np.array([4.2,  2.8,  2.5,  2.1, 2.1])
    inference  = np.array([108,  53,   48,   42.3, 0])
    postproc   = np.array([12.5, 7.2,  6.8,  5.4, 5.9])
    encode     = np.array([18.3, 11.0, 10.2, 9.9, 9.0])
    total      = frame_read + inference + postproc + encode

    x  = np.arange(len(systems))
    w  = 0.5

    fig, ax = plt.subplots(figsize=(9, 5.5))
    base_style(fig, [ax])
    fig.subplots_adjust(top=0.84, bottom=0.2, left=0.11, right=0.97)

    b1 = ax.bar(x, frame_read, w, label="Frame Read",       color=BLUE+"88",   edgecolor=BLUE,   linewidth=1.2)
    b2 = ax.bar(x, inference,  w, label="Inference (YOLO)", color=RED+"88",    edgecolor=RED,    linewidth=1.2, bottom=frame_read)
    b3 = ax.bar(x, postproc,   w, label="Post-process/Draw",color=YELLOW+"88", edgecolor=YELLOW, linewidth=1.2, bottom=frame_read+inference)
    b4 = ax.bar(x, encode,     w, label="Encode/Write",     color=GREEN+"77",  edgecolor=GREEN,  linewidth=1.2, bottom=frame_read+inference+postproc)

    # Total labels
    for xi, tot in enumerate(total):
        ax.text(xi, tot + 1.5, f"{tot:.0f} ms",
                ha="center", va="bottom", color=TEXT,
                fontsize=8.5, fontfamily="monospace")

    # Annotate saving
    ax.annotate("61% faster\ninference",
                xy=(3, 42.3/2 + 4.2), xytext=(2.0, 85),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.2),
                color=GREEN, fontsize=8, fontfamily="monospace", ha="center")

    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=8.5)
    ax.set_ylabel("Latency (ms)", color=DIM, fontsize=10)
    ax.set_xlabel("Detection System", color=DIM, fontsize=10)
    ax.legend(loc="upper right", fontsize=8, facecolor=PANEL,
              edgecolor=BORDER, labelcolor=TEXT)

    add_title_block(fig, "04", "Per-Frame Latency Breakdown (ms)",
                    "↓  LOWER IS BETTER  |  Stacked by Processing Stage",
                    badge_color=DIM)
    save(fig, "fig04_latency_breakdown.png")

# ══════════════════════════════════════════════════════════════════
#  CHART 5 — Precision & Recall vs. Altitude  — Line
# ══════════════════════════════════════════════════════════════════
def chart5():
    altitudes = [20, 40, 60, 80, 100, 120, 150, 180, 200]

    prahar_prec  = [95.1, 92.3, 90.4, 88.2, 85.6, 81.1, 74.8, 68.3, 62.1]
    prahar_rec   = [93.8, 91.5, 87.9, 84.6, 81.2, 76.5, 70.1, 63.4, 57.8]
    drone_prec   = [89.2, 85.4, 82.1, 78.8, 74.3, 68.7, 61.2, 53.9, 47.0]
    drone_rec    = [86.7, 82.1, 78.3, 74.0, 69.5, 63.8, 56.4, 49.2, 43.1]
    aerial_prec  = [91.3, 87.8, 84.5, 81.2, 77.0, 71.6, 64.9, 57.3, 50.4]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    base_style(fig, [ax])
    fig.subplots_adjust(top=0.84, bottom=0.14, left=0.09, right=0.97)

    # PRAHAR — filled
    ax.plot(altitudes, prahar_prec, color=GREEN, lw=2.5,
            marker="o", ms=5, label="PRAHAR Precision")
    ax.fill_between(altitudes, prahar_prec, prahar_rec,
                    alpha=0.10, color=GREEN)
    ax.plot(altitudes, prahar_rec, color=BLUE, lw=2.5,
            marker="s", ms=5, label="PRAHAR Recall")

    # Competitors — dashed
    ax.plot(altitudes, drone_prec, color=RED, lw=1.6, ls="--",
            marker="^", ms=4, label="DroneNet Precision", alpha=0.85)
    ax.plot(altitudes, drone_rec,  color=YELLOW, lw=1.6, ls="--",
            marker="v", ms=4, label="DroneNet Recall", alpha=0.85)
    ax.plot(altitudes, aerial_prec, color=PURPLE, lw=1.6, ls=":",
            marker="D", ms=4, label="AerialDet Precision", alpha=0.85)

    # Gap annotation at 80 m
    gap = prahar_prec[3] - drone_prec[3]
    ax.annotate(f"+{gap:.1f}% vs DroneNet\n@ 80 m",
                xy=(80, prahar_prec[3]), xytext=(110, 93),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.2),
                color=GREEN, fontsize=8, fontfamily="monospace")

    # Danger zone shading
    ax.axvspan(150, 200, alpha=0.06, color=RED, label="High-altitude degradation zone")
    ax.axvline(150, color=RED, lw=0.8, ls=":", alpha=0.6)
    ax.text(152, 93.5, "≥150 m\nlimit", color=RED, fontsize=7.5,
            fontfamily="monospace")

    ax.set_xlim(15, 205)
    ax.set_ylim(40, 100)
    ax.set_xlabel("UAV Altitude (m)", color=DIM, fontsize=10)
    ax.set_ylabel("Score (%)", color=DIM, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xticks(altitudes)
    ax.legend(loc="lower left", fontsize=8, facecolor=PANEL,
              edgecolor=BORDER, labelcolor=TEXT, ncol=2)

    add_title_block(fig, "05",
                    "Detection Precision & Recall vs. UAV Altitude (m)",
                    "PRAHAR outperforms all baselines at every altitude tested  |  conf=0.25",
                    badge_color=DIM)
    save(fig, "fig05_altitude_performance.png")


# ── Run all ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  PRAHAR — Generating comparison charts...\n")
    chart1()
    chart2()
    chart3()
    chart4()
    chart5()
    print(f"\n  All 5 PNGs saved to: {OUT}\n")
