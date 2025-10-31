# Simple Face Detection (Flask + OpenCV + HTML)

This project is a minimal, offline-capable face detection demo:

- A clean web page (`index.html`) to upload an image and draw green boxes on detected faces
- A tiny Python backend (`server.py`) using Flask + OpenCV Haar cascade to detect faces locally (no CDNs, no internet required)
- A simple dependency file (`requirements.txt`)

## What’s inside

Project root: `face_detection-using-opencv-main/face_detection-using-opencv-main`

- `index.html` – Single-page UI. Sends the selected image to the backend at `/detect` and renders boxes on a canvas.
- `server.py` – Flask server exposing:
  - `GET /` – serves `index.html`
  - `POST /detect` – accepts an uploaded image (multipart form field `image`) and returns JSON with face bounding boxes.
- `requirements.txt` – Python dependencies: `flask`, `opencv-python`, `numpy`
- `haarcascade_frontalface_default.xml` – A local copy of the Haar cascade (optional). The server uses OpenCV’s built-in cascade path via `cv2.data.haarcascades` by default.
- Sample images (`testing  (1).jpeg`, `testing  (2).jpeg`, etc.) for quick manual testing.

## How it works

On image selection, the browser posts the file to `/detect`. The server:

1. Reads the image and converts it to grayscale (+ histogram equalization for robustness)
2. Runs OpenCV’s Haar cascade face detector
3. Returns bounding boxes as JSON

The frontend draws the boxes and shows a face count.

## Quick start (Windows)

Open a terminal in: `face_detection-using-opencv-main/face_detection-using-opencv-main`

### Using Command Prompt (cmd)

```bat
REM Optional: create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Start the server
python server.py
```

### Using PowerShell

```powershell
# Optional: create and activate a virtual environment
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

Then open your browser at:

```
http://127.0.0.1:5000/
```

Upload an image and you’ll see green rectangles around detected faces.

## API

### POST /detect

- Content-Type: multipart/form-data
- Field name: `image` (file)

Optional query params to tune detection (defaults shown):

- `scale` (float, default `1.1`) – detection scaleFactor
- `neighbors` (int, default `5`) – minNeighbors (increase to reduce false positives)
- `min` (int, default `30`) – minimum face size in pixels

Response:

```json
{
  "faces": [{ "x": 123, "y": 45, "width": 160, "height": 160, "score": 1.0 }],
  "width": 1920,
  "height": 1080
}
```

Example request with curl.exe (Windows):

```powershell
$p = "C:\\path\\to\\photo.jpg"
curl.exe -X POST -F "image=@$p;type=image/jpeg" "http://127.0.0.1:5000/detect"
```

Notes:

- If your path contains spaces, keep the quotes around the URL and use the variable as shown above.
- PowerShell’s `Invoke-WebRequest` doesn’t support `-Form` on some versions; use `curl.exe` or a tool like Postman.

## Tuning and tips

- Too many false positives? Try increasing `neighbors` (e.g., 6–8) and `min` (e.g., 40–60).
- Missed small faces? Lower `min` (e.g., 20) or `scale` slightly, but this can increase false positives.
- Use clear, front-facing photos with good lighting for best results.

## Troubleshooting

- Server not reachable:

  - Make sure it’s running in the terminal (`python server.py`) and listening on `http://127.0.0.1:5000/`.
  - Check firewall rules or any app already using port 5000.

- Cascade loading errors:
  - The code uses OpenCV’s built-in cascades: `cv2.data.haarcascades/haarcascade_frontalface_default.xml`.
  - If your OpenCV install is missing data files, you can switch the path in `server.py` to the local `haarcascade_frontalface_default.xml` included here.

## Credits

- Face detection: OpenCV Haar Cascade (frontal face)
- UI: plain HTML/CSS/JS

Enjoy experimenting!
