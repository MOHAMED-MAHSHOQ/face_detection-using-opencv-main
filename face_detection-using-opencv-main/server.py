from __future__ import annotations
import io
import os
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np

APP_DIR = Path(__file__).parent.resolve()
# Use OpenCV's built-in haarcascade path to avoid shipping XML ourselves
CASCADE_PATH = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
STATIC_INDEX = APP_DIR / "index.html"

app = Flask(__name__, static_folder=str(APP_DIR), static_url_path="/")


def load_cascade():
    if not CASCADE_PATH.exists():
        raise FileNotFoundError(f"Cascade not found: {CASCADE_PATH}")
    cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    if cascade.empty():
        raise RuntimeError("Failed to load Haar cascade (OpenCV install may be missing data files)")
    return cascade


# Lazy-load cascade once
_cascade = None

def get_cascade():
    global _cascade
    if _cascade is None:
        _cascade = load_cascade()
    return _cascade


@app.route("/")
def root():
    # Serve the index.html from the same folder
    return send_from_directory(str(APP_DIR), "index.html")


@app.post("/detect")
def detect():
    """Detect faces in an uploaded image.
    Returns JSON: { faces: [{x,y,width,height,score}], width, height }
    """
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    data = file.read()
    if not data:
        return jsonify({"error": "Empty file"}), 400

    # Decode image to OpenCV format
    image_array = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Improve robustness on low-light
    gray = cv2.equalizeHist(gray)

    # Parameters tuned to reduce false positives
    scale_factor = float(request.args.get("scale", 1.1))
    min_neighbors = int(request.args.get("neighbors", 5))
    min_size = int(request.args.get("min", 30))

    cascade = get_cascade()
    faces_rects = cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_size, min_size),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    # Build response
    faces = []
    for (x, y, w, h) in faces_rects:
        # Basic sanity filters (discard extremely small/large boxes)
        if w < 20 or h < 20:
            continue
        if w > img.shape[1] or h > img.shape[0]:
            continue
        faces.append({
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
            "score": 1.0,  # Haar doesn't give score; treat as 1.0
        })

    return jsonify({
        "faces": faces,
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
    })


if __name__ == "__main__":
    # Run the server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
