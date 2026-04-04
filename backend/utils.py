import cv2
import math
import random

# YOLO class → Threat type mapping
THREAT_MAP = {
    "person": "Enemy Soldier",
    "car": "Military Vehicle",
    "truck": "Military Vehicle",
    "bus": "Military Vehicle",
    "motorcycle": "Military Vehicle",
    "bicycle": "Military Vehicle",
    "aeroplane": "Military Vehicle",
    "airplane": "Military Vehicle",
    "boat": "Military Vehicle",
}

THREAT_COLORS = {
    "Enemy Soldier": (0, 0, 220),      # Red (BGR)
    "Military Vehicle": (0, 165, 255),  # Orange (BGR)
}

THREAT_LABEL_COLORS = {
    "Enemy Soldier": (255, 50, 50),
    "Military Vehicle": (50, 200, 255),
}


def map_label_to_threat(label: str) -> str | None:
    """Map YOLO class label to military threat category."""
    return THREAT_MAP.get(label.lower(), None)


def get_threat_level(enemy_count: int, vehicle_count: int) -> str:
    """Determine overall threat level based on detection counts."""
    if enemy_count > 0:
        return "HIGH"
    elif vehicle_count > 0:
        return "MEDIUM"
    else:
        return "LOW"


def draw_detection_box(frame, detection: dict):
    """Draw a styled military bounding box on the frame."""
    x1, y1, x2, y2 = detection["bbox"]
    threat_type = detection["threat_type"]
    confidence = detection["confidence"]
    label = detection.get("threat_type", "Unknown")

    color = THREAT_COLORS.get(threat_type, (200, 200, 200))
    h, w = frame.shape[:2]

    # Main bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Corner accent lines (military style)
    corner_len = min(12, (x2 - x1) // 4, (y2 - y1) // 4)
    for px, py in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
        dx = 1 if px == x1 else -1
        dy = 1 if py == y1 else -1
        cv2.line(frame, (px, py), (px + dx * corner_len, py), (255, 255, 255), 1)
        cv2.line(frame, (px, py), (px, py + dy * corner_len), (255, 255, 255), 1)

    # Label background
    label_text = f"{label} {confidence:.0f}%"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.42
    thickness = 1
    (tw, th), _ = cv2.getTextSize(label_text, font, font_scale, thickness)
    label_y = max(y1 - 4, th + 4)

    cv2.rectangle(frame, (x1, label_y - th - 4), (x1 + tw + 6, label_y + 2), color, -1)
    cv2.putText(frame, label_text, (x1 + 3, label_y - 2), font, font_scale, (255, 255, 255), thickness)

    # Center dot
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)


def generate_threat_coordinates(detections: list, frame_w: int, frame_h: int) -> list:
    """
    Convert pixel detections to normalized threat coordinates for 3D map.
    Returns list of {x, y, z, type} objects.
    """
    coords = []
    seen = set()

    for det in detections:
        cx = det.get("cx", 0)
        cy = det.get("cy", 0)
        threat_type = det.get("threat_type", "Unknown")

        # Quantize to avoid too many points
        grid_x = round(cx / max(frame_w, 1), 2)
        grid_y = round(cy / max(frame_h, 1), 2)
        key = (grid_x, grid_y, threat_type)

        if key not in seen:
            seen.add(key)
            # Map to 3D terrain coordinates (-50 to 50 range)
            tx = (grid_x - 0.5) * 100
            ty = (grid_y - 0.5) * 100
            # Add slight elevation variation
            tz = round(random.uniform(0.5, 3.0), 2)
            coords.append({
                "x": round(tx, 1),
                "y": round(ty, 1),
                "z": tz,
                "type": threat_type,
                "confidence": det.get("confidence", 0),
            })

    return coords[:50]  # Limit to 50 unique points
