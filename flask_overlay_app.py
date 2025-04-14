from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from pathlib import Path
import logging
import os
import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static"
TEMPLATE_SIZE = (1080, 1920)
STATIC_DIR = Path(app.config["UPLOAD_FOLDER"])
STENCIL_FILENAME = "stencil_1080x1920.png"
STENCIL_PATH = STATIC_DIR / STENCIL_FILENAME

EXPIRATION_SECONDS = 15 * 60  # 15 minutes


stencil = Image.open(STENCIL_PATH).convert("RGBA")


def cleanup_static_folder():
    now = time.time()
    for file in STATIC_DIR.iterdir():
        if file.name == STENCIL_FILENAME:
            continue
        if file.is_file():
            try:
                if now - file.stat().st_mtime > EXPIRATION_SECONDS:
                    file.unlink()
                    logger.info("Deleted expired file: %s", file.name)
            except Exception as e:
                logger.warning("Failed to delete file: %s", file.name)


@app.route("/", methods=["GET", "POST"])
def index():
    video_url = None
    image_url = None

    if request.method == "POST":
        file = request.files.get("image") or request.files.get("video")

        if not file or not file.filename:
            logger.warning("No file selected for upload")
            return render_template("index.html", video_url=None, image_url=None, stencil_url=STENCIL_FILENAME)

        filename = secure_filename(file.filename)
        file_ext = Path(filename).suffix.lower()

        try:
            if file_ext in [".jpg", ".jpeg", ".png"]:
                image = Image.open(file.stream).convert("RGBA")
                image = ImageOps.fit(image, TEMPLATE_SIZE, method=Image.BICUBIC, centering=(0.5, 0.5))
                result = Image.alpha_composite(image, stencil)
                output_filename = f"output_{filename}"
                output_path = STATIC_DIR / output_filename
                result.save(output_path)
                logger.info("Image uploaded and processed: %s", filename)
                image_url = url_for("static", filename=output_filename)

            elif file_ext == ".mp4":
                save_path = STATIC_DIR / filename
                file.save(save_path)
                logger.info("Video uploaded: %s", filename)
                video_url = url_for("static", filename=filename)

            else:
                logger.warning("Unsupported file type: %s", filename)

        except Exception as e:
            logger.exception("Failed to handle uploaded file: %s", filename)

    cleanup_static_folder()
    return render_template("index.html", video_url=video_url, image_url=image_url, stencil_url=STENCIL_FILENAME)


if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.run(debug=True)
