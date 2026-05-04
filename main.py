from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
import requests
import io

app = Flask(__name__)

# Map each muscle NAME to its color in your avatar image
# You'll fill these in by eyedropping colors from your image
MUSCLE_COLORS = {
    "pectoralis_major":  (79, 160, 190),   # turquoise
    "deltoid":           (198, 96, 50),   # orange
    "bicep":             (234, 179, 8),    # orange
    "tricep":            (34, 197, 94),    # green
    "rectus_abdominis":  (220, 50, 50),    # red
    "obliques":          (236, 72, 153),   # pink
    "quadriceps":        (236, 72, 153),   # pink (adjust)
    "hamstring":         (59, 130, 246),   # blue (adjust)
    # add all muscles here
}

COLOR_TOLERANCE = 35  # how closely a pixel must match — adjust if needed

def colors_match(pixel, target, tolerance):
    return all(abs(int(pixel[i]) - int(target[i])) < tolerance for i in range(3))

@app.route("/recolor", methods=["POST"])
def recolor():
    data = request.json
    image_url = data["image_url"]
    highlight_muscles = data["muscles"]  # list of muscle names to make RED

    # Download the image
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    pixels = img.load()
    width, height = img.size

    # Build set of colors to highlight
    highlight_colors = [MUSCLE_COLORS[m] for m in highlight_muscles if m in MUSCLE_COLORS]

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            matched_highlight = any(colors_match(pixel, hc, COLOR_TOLERANCE) for hc in highlight_colors)
            
            # Check if pixel belongs to ANY muscle at all
            is_any_muscle = any(colors_match(pixel, mc, COLOR_TOLERANCE) for mc in MUSCLE_COLORS.values())

            if matched_highlight:
                pixels[x, y] = (220, 30, 30)    # RED
            elif is_any_muscle:
                pixels[x, y] = (20, 20, 20)     # near-BLACK
            # else: leave background/skin pixels untouched

    # Return image as PNG
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
