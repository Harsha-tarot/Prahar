import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(figsize=(4.0, 7.5), dpi=300)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.axis("off")
ax.set_xlim(0, 150)
ax.set_ylim(0, 270)

def draw_box(ax, x, y, w, h, text, fill_color="#f8f8f8", ec="#444444", font_size=6.5, font_weight="bold"):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=2", ec=ec, fc=fill_color, lw=1.0, zorder=10)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=font_size, fontweight=font_weight, fontfamily="sans-serif", color="#111111", zorder=12)

def draw_container(ax, x, y, w, h, title):
    # Dashed box
    box = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", ec="#aaaaaa", fc="#fcfcfc", lw=1.0, linestyle="--", zorder=1)
    ax.add_patch(box)
    # Title on top boundary with a white background to mask intersecting lines
    ax.text(x + 5, y + h, title, ha="left", va="center", fontsize=8, fontweight="bold", fontfamily="sans-serif", color="#222222", bbox=dict(fc="white", ec="none", pad=2), zorder=20)

def draw_arrow(ax, x1, y1, x2, y2, label="", label_pos=0.5):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", color="#444444", lw=1.2, mutation_scale=8, zorder=5)
    ax.add_patch(arrow)
    if label:
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos
        ax.text(lx, ly, label, ha="center", va="center", fontsize=5.5, fontweight="bold", fontfamily="sans-serif", color="#111111", bbox=dict(fc="white", ec="none", pad=1.5), zorder=15)

# L1: Field Assets
draw_container(ax, 2, 235, 146, 25, "1. Field Assets")
draw_box(ax, 6, 240, 42, 15, "UAV Camera\n(Video Stream)", fill_color="#eeeeee")
draw_box(ax, 102, 240, 42, 15, "UAV Sensors\n(GPS / IMU)", fill_color="#eeeeee")

# L2: Edge Node
draw_container(ax, 2, 115, 146, 95, "2. Edge Computing Node (Python/Flask)")
draw_box(ax, 6, 185, 42, 15, "Frame\nExtractor")
draw_box(ax, 102, 185, 42, 15, "Telemetry\nHandler")

draw_box(ax, 6, 150, 42, 15, "YOLOv8n\nDetection")
draw_box(ax, 54, 150, 42, 15, "Luminance\n3D Mapping")
draw_box(ax, 102, 150, 42, 15, "Geo-Registration\nModule")

draw_box(ax, 6, 115, 42, 15, "Object Tracking\n(DeepSORT)")
draw_box(ax, 54, 115, 42, 15, "Threat Assessment\nEngine", fill_color="#eeeeee")

# L3: Middleware
draw_container(ax, 2, 55, 146, 40, "3. Middleware & Storage")
draw_box(ax, 6, 65, 42, 20, "Processed\nVideo FS")
draw_box(ax, 54, 65, 42, 20, "Edge API\nGateway", fill_color="#eeeeee")
draw_box(ax, 102, 65, 42, 20, "MongoDB\n(Routes / Logs)")

# L4: Command Center
draw_container(ax, 2, 2, 146, 35, "4. Command Center Dashboard (React)")
draw_box(ax, 40, 22, 70, 10, "State Management & API")
draw_box(ax, 10, 6, 55, 10, "Deck.gl 3D Map\n(Terrain & Overlay)", fill_color="#f0f0f0")
draw_box(ax, 85, 6, 55, 10, "Mission UI\n(HUD & Alerts)", fill_color="#f0f0f0")


# --- DRAW ARROWS ---

# Field to Edge
draw_arrow(ax, 27, 240, 27, 200, "RTSP Stream", label_pos=0.4)
draw_arrow(ax, 123, 240, 123, 200, "Telemetry", label_pos=0.4)

# Inside Edge
draw_arrow(ax, 27, 185, 27, 165) # Frame -> YOLO
draw_arrow(ax, 48, 192.5, 75, 165, "RGB Frame", label_pos=0.4) # Frame -> Lum
draw_arrow(ax, 123, 185, 123, 165) # Sync -> GeoReg
draw_arrow(ax, 27, 150, 27, 130) # YOLO -> Tracking
draw_arrow(ax, 96, 157.5, 102, 157.5) # Lum -> GeoReg (Horizontal)
draw_arrow(ax, 48, 122.5, 54, 122.5) # Tracking -> Threat (Horizontal)
draw_arrow(ax, 123, 150, 96, 130, "3D Coords", label_pos=0.5) # GeoReg -> Threat

# Edge to Middleware
draw_arrow(ax, 27, 115, 27, 85, "MP4 Save", label_pos=0.45) # Tracking -> FS
draw_arrow(ax, 75, 115, 75, 85, "JSON Events", label_pos=0.45) # Threat -> API
draw_arrow(ax, 85, 115, 123, 85, "Log Save", label_pos=0.5) # Threat -> Mongo

# Middleware to Command
draw_arrow(ax, 75, 65, 75, 32, "WSS / HTTP", label_pos=0.4) # API -> State
draw_arrow(ax, 27, 65, 37.5, 16, "Video Stream", label_pos=0.4) # FS -> Deck.gl

# Inside Command
draw_arrow(ax, 50, 22, 37.5, 16) # State -> Deck.gl
draw_arrow(ax, 100, 22, 112.5, 16) # State -> Mission UI

save_path = os.path.join(OUT, "fig06_system_architecture.png")
fig.savefig(save_path, dpi=300, bbox_inches="tight")
print(f"Generated pixel-perfect IEEE architecture diagram: {save_path}")
