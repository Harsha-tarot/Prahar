import cv2
import time
import json
import os
import random
import math
from utils import (
    map_label_to_threat,
    get_threat_level,
    draw_detection_box,
    generate_threat_coordinates,
)

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[WARNING] ultralytics not installed. Running in DEMO mode.")


def process_video(input_path: str, output_path: str) -> dict:
    """
    Process a video file frame-by-frame using YOLOv8.
    Falls back to demo mode if YOLO is not available.
    Returns a result dict with all metrics.
    """

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {input_path}")

    # Video metadata
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps_in if fps_in > 0 else 0

    # Output writer — use mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps_in, (width, height))

    # Load YOLO model
    model = None
    if YOLO_AVAILABLE:
        try:
            model = YOLO("yolov8n.pt")  # nano = fastest
            print("[INFO] YOLOv8 model loaded.")
        except Exception as e:
            print(f"[WARNING] YOLO model load failed: {e}. Using demo mode.")

    # Metrics
    total_detections = 0
    enemy_count = 0
    vehicle_count = 0
    frame_times = []
    all_detections = []

    frame_idx = 0
    sample_rate = max(1, int(fps_in / 15))  # Process up to 15 frames/sec of inference
    last_detections = []  # carry forward boxes between sampled frames

    print(f"[INFO] Processing video: {width}x{height} @ {fps_in:.1f}fps, {total_frames} frames")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_start = time.time()

        if frame_idx % sample_rate == 0:
            if model is not None:
                detections = run_yolo_inference(model, frame)
            else:
                detections = run_demo_inference(frame, frame_idx, total_frames)

            last_detections = detections  # update last known detections

            # Count unique detections only on sampled frames
            for det in detections:
                draw_detection_box(frame, det)
                threat_type = det["threat_type"]
                if threat_type == "Enemy Soldier":
                    enemy_count += 1
                elif threat_type == "Military Vehicle":
                    vehicle_count += 1
                total_detections += 1
                all_detections.append(det)

            if detections:
                print(f"[DET] Frame {frame_idx}: {len(detections)} threat(s) detected")
        else:
            # Draw last known bounding boxes on non-sampled frames (smooth playback)
            for det in last_detections:
                draw_detection_box(frame, det)

        # Draw HUD overlay
        draw_hud(frame, frame_idx, total_frames, fps_in)

        out.write(frame)
        frame_times.append(time.time() - frame_start)
        frame_idx += 1

    cap.release()
    out.release()

    # Re-encode with ffmpeg if available for browser compatibility (H.264)
    try:
        import subprocess, shutil
        temp_path = output_path.replace(".mp4", "_temp.mp4")

        # If temp already exists from a previous run, remove it
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Move the mp4v-encoded file to temp
        shutil.move(output_path, temp_path)

        result = subprocess.run(
            [
                "ffmpeg", "-y", "-i", temp_path,
                "-vcodec", "libx264", "-preset", "fast",
                "-crf", "23",
                "-acodec", "aac",
                "-movflags", "+faststart",
                output_path
            ],
            capture_output=True, timeout=300
        )
        if result.returncode == 0:
            os.remove(temp_path)
            print("[INFO] ffmpeg re-encode successful.")
        else:
            # ffmpeg failed — restore original
            print(f"[WARN] ffmpeg failed (code {result.returncode}), using raw mp4v output")
            print(f"[WARN] ffmpeg stderr: {result.stderr.decode('utf-8', errors='ignore')[-300:]}")
            shutil.move(temp_path, output_path)
    except FileNotFoundError:
        print("[INFO] ffmpeg not found, using raw mp4v output.")
        # temp_path may exist if move succeeded but ffmpeg not found
        temp_path = output_path.replace(".mp4", "_temp.mp4")
        if not os.path.exists(output_path) and os.path.exists(temp_path):
            import shutil as _sh
            _sh.move(temp_path, output_path)
    except Exception as e:
        print(f"[WARN] ffmpeg step error: {e}")
        temp_path = output_path.replace(".mp4", "_temp.mp4")
        if not os.path.exists(output_path) and os.path.exists(temp_path):
            import shutil as _sh
            _sh.move(temp_path, output_path)

    avg_fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else fps_in
    threat_level = get_threat_level(enemy_count, vehicle_count)
    threat_coords = generate_threat_coordinates(all_detections, width, height)

    return {
        "threat_level": threat_level,
        "total_detections": total_detections,
        "enemy_count": enemy_count,
        "vehicle_count": vehicle_count,
        "fps": round(avg_fps, 2),
        "duration": round(duration, 2),
        "frame_count": total_frames,
        "resolution": f"{width}x{height}",
        "threat_coordinates": threat_coords,
    }


def run_yolo_inference(model, frame):
    """Run YOLOv8 inference on a single frame."""
    detections = []
    results = model(frame, verbose=False, conf=0.25)  # lower threshold = more detections
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls_id]
            threat_type = map_label_to_threat(label)
            if threat_type is None:
                continue
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
            detections.append({
                "label": label,
                "threat_type": threat_type,
                "confidence": round(conf * 100, 1),
                "bbox": [x1, y1, x2, y2],
                "cx": (x1 + x2) // 2,
                "cy": (y1 + y2) // 2,
            })
            print(f"[YOLO] Detected {label!r} → {threat_type} ({conf*100:.1f}%)")
    return detections


def run_demo_inference(frame, frame_idx, total_frames):
    """
    Demo mode: generate synthetic detections for showcase.
    Simulates detection pattern over time.
    """
    h, w = frame.shape[:2]
    detections = []

    # Pseudo-random but deterministic pattern
    random.seed(frame_idx // 5)
    num_dets = random.randint(0, 3) if frame_idx % 15 < 10 else 0

    for i in range(num_dets):
        bw = random.randint(w // 8, w // 4)
        bh = random.randint(h // 8, h // 4)
        x1 = random.randint(10, max(10, w - bw - 10))
        y1 = random.randint(10, max(10, h - bh - 10))
        x2, y2 = x1 + bw, y1 + bh
        threat_type = random.choice(["Enemy Soldier", "Enemy Soldier", "Military Vehicle"])
        label = "person" if threat_type == "Enemy Soldier" else "car"
        conf = round(random.uniform(55, 95), 1)
        detections.append({
            "label": label,
            "threat_type": threat_type,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2],
            "cx": (x1 + x2) // 2,
            "cy": (y1 + y2) // 2,
        })
    return detections


def draw_hud(frame, frame_idx, total_frames, fps):
    """Draw military HUD overlay on frame."""
    h, w = frame.shape[:2]

    # Scan lines effect (subtle)
    overlay = frame.copy()

    # Corner brackets
    bracket_color = (0, 200, 50)  # Military green
    bracket_len = 25
    thickness = 2

    corners = [(10, 10), (w - 10, 10), (10, h - 10), (w - 10, h - 10)]
    for cx, cy in corners:
        dx = 1 if cx < w // 2 else -1
        dy = 1 if cy < h // 2 else -1
        cv2.line(frame, (cx, cy), (cx + dx * bracket_len, cy), bracket_color, thickness)
        cv2.line(frame, (cx, cy), (cx, cy + dy * bracket_len), bracket_color, thickness)

    # Center crosshair
    cc = (w // 2, h // 2)
    cv2.line(frame, (cc[0] - 15, cc[1]), (cc[0] - 5, cc[1]), bracket_color, 1)
    cv2.line(frame, (cc[0] + 5, cc[1]), (cc[0] + 15, cc[1]), bracket_color, 1)
    cv2.line(frame, (cc[0], cc[1] - 15), (cc[0], cc[1] - 5), bracket_color, 1)
    cv2.line(frame, (cc[0], cc[1] + 5), (cc[0], cc[1] + 15), bracket_color, 1)

    # Progress bar
    progress = frame_idx / max(total_frames, 1)
    bar_w = int(w * progress)
    cv2.rectangle(frame, (0, h - 4), (bar_w, h), (0, 180, 80), -1)

    # Frame counter
    text = f"PRAHAR REC | FRM {frame_idx:04d}/{total_frames:04d}"
    cv2.putText(frame, text, (15, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 50), 1)

    # Timestamp simulation
    ts = f"UTC 2024-01-{15 + (frame_idx // 100 % 15):02d} {(frame_idx // 10 % 24):02d}:{(frame_idx % 10 * 6):02d}:00"
    cv2.putText(frame, ts, (w - 250, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 50), 1)

    # PRAHAR label
    cv2.putText(frame, "PRAHAR-EDGE-AI", (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 50), 1)
