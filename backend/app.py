import os
import uuid
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from video_processor import process_video

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "system": "PRAHAR Edge AI"})


@app.route("/test-mapping", methods=["GET"])
def test_mapping():
    """Debug endpoint — verify detection mapping logic works end-to-end."""
    from utils import map_label_to_threat, get_threat_level
    sample_labels = ["person", "car", "truck", "bus", "dog", "cat", "airplane", "boat"]
    mapping_results = {
        label: map_label_to_threat(label) for label in sample_labels
    }
    return jsonify({
        "mapping": mapping_results,
        "threat_level_examples": {
            "enemy_only":    get_threat_level(3, 0),
            "vehicle_only":  get_threat_level(0, 2),
            "both":          get_threat_level(1, 1),
            "none":          get_threat_level(0, 0),
        },
        "status": "mapping ok"
    })


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save uploaded video
    file_id = str(uuid.uuid4())[:8]
    input_filename = f"input_{file_id}.mp4"
    output_filename = f"output_{file_id}.mp4"

    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    video_file.save(input_path)

    try:
        result = process_video(input_path, output_path)
        result["video_url"] = f"/video/{output_filename}"
        result["file_id"] = file_id
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/video/<filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/uploads/<filename>", methods=["GET"])
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    print("=" * 60)
    print("  PRAHAR – Real-Time Edge AI Reconnaissance System")
    print("  Backend running on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
