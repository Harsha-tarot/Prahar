# PRAHAR – Real-Time Edge AI Reconnaissance System

>  YOLOv8 · OpenCV · Flask · React · Three.js

![PRAHAR System](https://img.shields.io/badge/PRAHAR-Edge_AI-00ff8c?style=for-the-badge&logo=radar&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF4040?style=flat-square)
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-prahar--eight.vercel.app-00ff8c?style=flat-square)](https://prahar-eight.vercel.app/)
[![Backend](https://img.shields.io/badge/🤗_Backend-HuggingFace_Spaces-FFD21E?style=flat-square)](https://huggingface.co/spaces/Harsha-tarot117/prahar-backend)

---

## 🌐 Live Deployment

> **Shipped and running — no setup required.**

| Layer | Platform | URL |
|-------|----------|-----|
| 🖥️ **Frontend** | Vercel | [prahar-eight.vercel.app](https://prahar-eight.vercel.app/) |
| ⚙️ **Backend API** | HuggingFace Spaces (Docker) | [harsha-tarot117-prahar-backend.hf.space](https://harsha-tarot117-prahar-backend.hf.space/) |

---

## 🎯 Overview

PRAHAR processes uploaded drone videos frame-by-frame using YOLOv8, detects military threats (enemy soldiers & vehicles), overlays bounding boxes with confidence scores, and visualizes the results in a military-grade dark themed dashboard with 3D terrain maps.

---

## ⚙️ Quick Start

### Backend (Flask + YOLOv8)

```bash
cd prahar/backend
pip install -r requirements.txt
python app.py
```

> Backend starts on `http://localhost:5000`

### Frontend (React + Vite)

```bash
cd prahar/frontend
npm install
npm run dev
```

> Frontend starts on `http://localhost:5173`

---

## 🧠 Architecture

```
Upload Video → Flask Backend → OpenCV Frame Extraction
                                    ↓
                             YOLOv8 Inference
                                    ↓
                        Detection Mapping + Bounding Box Draw
                                    ↓
                        Output Video (MP4) + JSON Metrics
                                    ↓
                     React Dashboard ← Axios HTTP Client
                          ↓                  ↓
                   Video Playback       MetricsPanel
                   (with HUD overlay)   TerrainMap (Three.js)
```

---

## 🗂️ Project Structure

```
prahar/
├── backend/
│   ├── app.py              # Flask server, API routes
│   ├── video_processor.py  # YOLOv8 + OpenCV processing pipeline
│   ├── utils.py            # Threat mapping, drawing utilities
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx                    # Root component & layout
│       ├── index.css                  # Military dark theme CSS
│       └── components/
│           ├── MetricsPanel.jsx       # Animated stats + threat level
│           ├── TerrainMap.jsx         # Three.js 3D terrain
│           └── ActivityLog.jsx        # Live event log
└── README.md
```

---

## 🔍 Detection Mapping

| YOLO Class      | Threat Type        | Marker Color |
|-----------------|--------------------|--------------|
| `person`        | Enemy Soldier       | 🔴 Red       |
| `car`, `truck`  | Military Vehicle    | 🟡 Yellow    |
| `bus`, `boat`   | Military Vehicle    | 🟡 Yellow    |
| `airplane`      | Military Vehicle    | 🟡 Yellow    |

---

## ⚠️ Threat Level Logic

| Condition                     | Threat Level | UI Color        |
|-------------------------------|--------------|-----------------|
| Any enemy soldiers detected   | `HIGH`       | 🔴 Red flashing |
| Only military vehicles        | `MEDIUM`     | 🟡 Yellow       |
| No threats                    | `LOW`        | 🟢 Green        |

---

## 📊 API Reference

### `POST /analyze-video`

Upload a drone video for threat analysis.

**Request:** `multipart/form-data` with field `video`

**Response:**
```json
{
  "video_url": "/video/output_abc123.mp4",
  "threat_level": "HIGH | MEDIUM | LOW",
  "total_detections": 42,
  "enemy_count": 12,
  "vehicle_count": 8,
  "fps": 18.4,
  "duration": 34.5,
  "frame_count": 863,
  "resolution": "1920x1080",
  "threat_coordinates": [
    { "x": 15.5, "y": -20.1, "z": 2.1, "type": "Enemy Soldier", "confidence": 87.3 }
  ]
}
```

### `GET /video/<filename>`
Serve the processed output video.

### `GET /health`
System health check.

---

## 🌍 3D Terrain Visualization

Built with **Three.js** — generates a procedural terrain using sinusoidal noise:

- **Green terrain** → elevation-colored geometry
- **Wireframe overlay** → military grid aesthetic  
- **Auto-rotating camera** → continuous orbit around the battlefield
- **Red markers** → Enemy Soldier positions  
- **Yellow markers** → Military Vehicle positions  
- **Pulsing rings** → animated threat indicators  

---

## 🔗 Datature Integration (Conceptual)

> This section explains how PRAHAR can scale from a prototype to a production-ready military AI system using Datature's annotation and training platform.

### What is Datature?

[Datature](https://datature.io) is a no-code AI platform for building, training, and deploying computer vision models. It provides:

- **Annotation Tools** — Bounding box, polygon, semantic & instance segmentation
- **Model Training** — Train YOLOv8, Detectron2, EfficientDet on custom datasets
- **Model Hub** — Version-controlled model registry
- **Deployment** — One-click inference API deployment

### How Datature Fits Into PRAHAR

| Stage | Tool | Description |
|-------|------|-------------|
| **Dataset Curation** | Datature Annotator | Label drone footage with enemy/vehicle classes |
| **Model Training** | Datature Nexus | Fine-tune YOLOv8 on military terrain images |
| **Model Export** | Datature Hub | Export `.pt` model → deploy to edge device |
| **Edge Inference** | PRAHAR Backend | Run Datature model via Ultralytics API |

### Replacing YOLOv8 Generic with Datature-Trained Model

```python
# Current: Generic YOLOv8 pretrained on COCO
model = YOLO("yolov8n.pt")

# Scalable: Datature-trained military detection model
model = YOLO("datature_military_v2.pt")  # Exported from Datature Hub
```

The swap is **one line** — the entire PRAHAR pipeline scales automatically.

### Benefits

- **Terrain-specific accuracy** — Model trained on camouflage, night-vision, aerial footage
- **Custom class vocabulary** — `sniper`, `armored_vehicle`, `bunker`, `weapon_cache`
- **Continual learning** — Retrain via Datature as new footage is labeled
- **Edge-optimized** — Export TFLite/ONNX for Jetson/Raspberry Pi deployment

---

## 🎨 UI Features

- **Military dark theme** with green accent colors (`#00ff8c`)
- **Real-time clock** in UTC
- **Blinking HIGH threat alert** on video frame
- **Animated metric counters** (count-up animation)
- **Drag & drop video upload**
- **HUD overlay** on processed video frames (brackets, crosshair, progress bar, timestamp)
- **Activity log** with timestamped events
- **3D rotating terrain** with threat markers

---

## 🚀 Demo Mode

If `ultralytics` is not installed or the model fails to load, PRAHAR automatically enters **Demo Mode**:

- Generates synthetic detections per frame
- Still draw bounding boxes, HUD, metrics
- Full UI experience without real ML inference
- Great for showcase without a GPU

---

## 🖥️ System Requirements

| Component  | Minimum          | Recommended       |
|------------|------------------|-------------------|
| Python     | 3.10+            | 3.11+             |
| RAM        | 8 GB             | 16 GB             |
| GPU        | None (CPU mode)  | NVIDIA 8GB VRAM   |
| Storage    | 2 GB             | 10 GB             |
| Node.js    | 18+              | 20+               |

---

## 📄 License

MIT License — Free for hackathon use.

---

> Built for the **PRAHAR Defense-Tech Hackathon** · Edge AI · Drone Surveillance · Real-Time Threat Detection
